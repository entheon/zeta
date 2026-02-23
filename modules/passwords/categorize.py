#!/usr/bin/env python3

import csv
import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import click

from modules.shared.categorize import categorize_item, log_progress, should_log
from modules.shared.report import generate_html_report

if TYPE_CHECKING:
    from llm import OllamaAPI


def categorize_with_ollama(
    entry: dict[str, str],
    api: "Optional[OllamaAPI]" = None,
) -> dict[str, str | float]:
    """Categorize a single password entry using the LLM.

    Args:
        entry: CSV row dict with "login_uri" and "name" keys.
        api: Optional OllamaAPI instance. Creates new one if None.

    Returns:
        Dict with "category" (str) and "confidence" (float) keys.
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
@click.argument("csv_file", type=click.Path(exists=True))
@click.option(
    "--output",
    default=None,
    help="Output directory for suggestions (default: same dir as CSV)",
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
    csv_file: str,
    output: Optional[str],
    recategorize: bool,
    dry_run: bool,
) -> None:
    """Generate categorization suggestions for passwords.

    Reads a CSV, runs LLM categorization, and produces a suggestion
    report (HTML + JSON) without modifying the original CSV.
    """
    from llm import OllamaAPI

    csv_path = Path(csv_file)

    if output is None:
        output_dir = csv_path.parent
    else:
        output_dir = Path(output)
        output_dir.mkdir(parents=True, exist_ok=True)

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        entries = list(reader)

    if not entries:
        click.echo("No entries found in CSV.", err=True)
        return

    api = OllamaAPI()
    suggestions: list[dict[str, str | float]] = []
    to_process = [e for e in entries if recategorize or not e.get("folder", "")]
    skipped = len(entries) - len(to_process)
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

    click.echo(f"Found {len(entries)} entries, {total} to categorize")

    start_time = time.time()
    log_interval = max(5, total // 20)

    for idx, entry in enumerate(to_process, start=1):
        result = categorize_with_ollama(entry, api=api)
        category = str(result["category"])
        confidence = float(result["confidence"])

        suggestion: dict[str, str | float] = {
            "name": entry.get("name", ""),
            "login_uri": entry.get("login_uri", ""),
            "current_folder": entry.get("folder", ""),
            "suggested_folder": category,
            "confidence": confidence,
        }
        suggestions.append(suggestion)

        if should_log(idx, total, log_interval):
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
                f"{s['name']} ({s['login_uri']}) "
                f"-> {s['suggested_folder']} "
                f"({s['confidence']:.2f})"
            )
        click.echo(f"\n{len(suggestions)} suggestions generated.")
        return

    json_path = output_dir / "passwords_suggestions.json"
    with open(json_path, "w") as f:
        json.dump(
            {"csv_file": str(csv_path), "suggestions": suggestions},
            f,
            indent=2,
        )
    click.echo(f"Suggestions written to {json_path}")

    report_items = [
        {
            "category": s["suggested_folder"],
            "confidence": s["confidence"],
            "login_uri": s["login_uri"],
            "name": s["name"],
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
