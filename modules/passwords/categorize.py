import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import click

from modules.passwords.models import PasswordSuggestion
from modules.shared.categorize import categorize_item, log_progress
from modules.shared.models import CategorizeResult
from modules.shared.report import generate_html_report

if TYPE_CHECKING:
    from llm.api import OllamaAPI


def _extract_login_uri(item: dict[str, Any]) -> str:
    login = item.get("login") or {}
    uris = login.get("uris") or []
    if uris:
        return str(uris[0].get("uri", ""))
    return ""


def _build_folder_map(data: dict[str, Any]) -> dict[str, str]:
    folders = data.get("folders") or []
    return {f["id"]: f["name"] for f in folders}


def categorize_with_ollama(
    entry: dict[str, str],
    api: "Optional[OllamaAPI]" = None,
) -> CategorizeResult:
    """Categorize a single password entry using the LLM.

    Args:
        entry: Dict with "login_uri" and "name" keys.
        api: Optional OllamaAPI instance. Creates new one if None.

    Returns:
        CategorizeResult with category and confidence fields.
    """
    data = {
        "url": entry.get("login_uri", ""),
        "name": entry.get("name", ""),
    }
    return categorize_item(
        data=data,
        task_description="a password entry (URL and name)",
        empty_check_fields=["url", "name"],
        api=api,
    )


@click.command()
@click.argument("json_file", type=click.Path(exists=True))
@click.option(
    "--output",
    default=None,
    help="Output directory for suggestions (default: same dir as JSON)",
)
@click.option(
    "--recategorize",
    is_flag=True,
    help="Re-categorize entries that already have a folder assigned",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show suggestions without writing output files",
)
def suggest(
    json_file: str,
    output: Optional[str],
    recategorize: bool,
    dry_run: bool,
) -> None:
    """Generate categorization suggestions for passwords.

    Reads a Bitwarden JSON export, runs LLM categorization, and
    produces a suggestion report (HTML + JSON) without modifying
    the original file.
    """
    from llm.api import OllamaAPI

    json_path = Path(json_file)

    if output is None:
        output_dir = json_path.parent
    else:
        output_dir = Path(output)
        output_dir.mkdir(parents=True, exist_ok=True)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    folder_map = _build_folder_map(data)
    items = data.get("items") or []

    login_items = [item for item in items if item.get("type") == 1]

    if not login_items:
        click.echo("No login items found in JSON.", err=True)
        return

    api = OllamaAPI()
    suggestions: list[PasswordSuggestion] = []

    to_process = [
        item for item in login_items if recategorize or not item.get("folderId")
    ]
    skipped = len(login_items) - len(to_process)
    total = len(to_process)

    if total == 0:
        if skipped:
            click.echo(
                f"All {skipped} entries already categorized "
                f"(use --recategorize to re-process)"
            )
        else:
            click.echo("No entries to categorize.")
        return

    click.echo(f"Found {len(login_items)} login items, {total} to categorize")

    start_time = time.time()

    for idx, item in enumerate(to_process, start=1):
        login_uri = _extract_login_uri(item)
        name = item.get("name", "")
        current_folder = folder_map.get(item.get("folderId", ""), "")

        entry = {"login_uri": login_uri, "name": name}
        result = categorize_with_ollama(entry, api=api)

        suggestions.append(
            PasswordSuggestion(
                item_id=item["id"],
                name=name,
                login_uri=login_uri,
                current_folder=current_folder,
                suggested_folder=result.category,
                confidence=result.confidence,
            )
        )

        log_progress(idx, total, start_time, item_noun="entry")

    total_time = time.time() - start_time
    total_min = int(total_time // 60)
    total_sec = int(total_time % 60)

    if skipped:
        click.echo(
            f"Skipped {skipped} already-categorized entries "
            f"(use --recategorize to include them)"
        )

    click.echo(f"\nCategorized {len(suggestions)} entries in {total_min}m {total_sec}s")

    if dry_run:
        for s in suggestions:
            click.echo(
                f"{s.name} ({s.login_uri}) -> {s.suggested_folder} ({s.confidence:.2f})"
            )
        click.echo(f"\n{len(suggestions)} suggestions generated.")
        return

    json_out_path = output_dir / "passwords_suggestions.json"
    with open(json_out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "json_file": str(json_path),
                "suggestions": [s.model_dump() for s in suggestions],
            },
            f,
            indent=2,
        )
    click.echo(f"Suggestions written to {json_out_path}")

    report_items = [
        {
            "category": s.suggested_folder,
            "confidence": s.confidence,
            "login_uri": s.login_uri,
            "name": s.name,
        }
        for s in suggestions
    ]

    report_path = output_dir / "passwords_report.html"
    generate_html_report(
        report_items,
        report_path,
        title="Password Categorization Suggestions",
        item_noun="passwords",
        source_field="login_uri",
        source_label="Domains",
        detail_field="name",
        detail_label="Entry Names",
    )
    click.echo(f"HTML report written to {report_path}")


if __name__ == "__main__":
    suggest()
