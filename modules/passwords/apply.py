import json
import uuid
from pathlib import Path
from typing import Any, Optional

import click

from modules.passwords.models import PasswordSuggestion


def verify_data(
    original_items: list[dict[str, Any]],
    new_items: list[dict[str, Any]],
) -> bool:
    """Verify data integrity between original and modified Bitwarden items.

    Checks that item count matches and all fields except 'folderId'
    are preserved between the original and new item lists.

    Args:
        original_items: Original Bitwarden items before categorization.
        new_items: Modified items with updated folderId assignments.

    Returns:
        True if data integrity holds, False if any corruption detected.
    """
    if len(original_items) != len(new_items):
        click.echo(
            f"Error: Item count mismatch! "
            f"Original: {len(original_items)}, "
            f"New: {len(new_items)}",
            err=True,
        )
        return False

    for i, (orig, new) in enumerate(zip(original_items, new_items, strict=True)):
        orig_fields = {k: v for k, v in orig.items() if k != "folderId"}
        new_fields = {k: v for k, v in new.items() if k != "folderId"}

        if orig_fields != new_fields:
            click.echo(f"Error: Data mismatch in item {i + 1}!", err=True)
            click.echo(f"Original: {orig_fields}", err=True)
            click.echo(f"New: {new_fields}", err=True)
            return False

    return True


@click.command()
@click.argument("suggestions_file", type=click.Path(exists=True))
@click.option(
    "--json-file",
    default=None,
    help="Override Bitwarden JSON path (default: path from suggestions file)",
)
@click.option(
    "--min-confidence",
    default=0.4,
    help="Minimum confidence to apply a suggestion (default: 0.4)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be applied without writing",
)
def apply(
    suggestions_file: str,
    json_file: Optional[str],
    min_confidence: float,
    dry_run: bool,
) -> None:
    """Apply categorization suggestions to a Bitwarden JSON export.

    Reads a suggestions JSON file produced by the suggest command and
    applies the suggested folders to the original Bitwarden JSON,
    writing a new _categorized.json file. Only suggestions meeting the
    minimum confidence threshold are applied.

    Args:
        suggestions_file: Path to the suggestions JSON file.
        json_file: Override path to original Bitwarden JSON. If None,
            uses the path stored in the suggestions file.
        min_confidence: Minimum confidence threshold for applying
            a suggestion. Suggestions below this are skipped.
        dry_run: If True, print what would be applied without writing.
    """

    with open(suggestions_file, encoding="utf-8") as f:
        suggestion_data = json.load(f)

    raw_suggestions = suggestion_data["suggestions"]
    original_json = json_file or suggestion_data.get("json_file", "")

    if not original_json:
        click.echo(
            "Error: No JSON file specified and none found in suggestions file.",
            err=True,
        )
        return

    suggestion_map: dict[str, tuple[str, float]] = {}
    for raw in raw_suggestions:
        s = PasswordSuggestion.model_validate(raw)
        suggestion_map[s.item_id] = (s.suggested_folder, s.confidence)

    with open(original_json, encoding="utf-8") as f:
        bw_data = json.load(f)

    original_items = bw_data.get("items") or []
    items = json.loads(json.dumps(original_items))
    folders = list(bw_data.get("folders") or [])

    folder_name_to_id: dict[str, str] = {f["name"]: f["id"] for f in folders}

    applied = 0
    skipped_low_conf = 0

    for item in items:
        item_id = item.get("id", "")
        if item_id in suggestion_map:
            folder_name, confidence = suggestion_map[item_id]
            if confidence >= min_confidence:
                # Create a new folder entry if this category doesn't
                # exist yet.  The uuid4 ID is an internal reference
                # within the JSON file — Bitwarden regenerates all IDs
                # on import, so the actual value doesn't matter as long
                # as item.folderId matches a folder.id in the same file.
                if folder_name not in folder_name_to_id:
                    new_id = str(uuid.uuid4())
                    folders.append({"id": new_id, "name": folder_name})
                    folder_name_to_id[folder_name] = new_id

                # Only field we modify on each item — everything else
                # (login, fido2Credentials, notes, etc.) is untouched.
                item["folderId"] = folder_name_to_id[folder_name]
                applied += 1
                if dry_run:
                    _login = item.get("login") or {}
                    _uris = _login.get("uris") or []
                    login_uri = str(_uris[0].get("uri", "")) if _uris else ""
                    click.echo(
                        f"{item['name']} ({login_uri}) "
                        f"-> {folder_name} ({confidence:.2f})"
                    )
            else:
                skipped_low_conf += 1

    click.echo(
        f"\n{applied} entries categorized, "
        f"{skipped_low_conf} skipped (below {min_confidence} confidence)"
    )

    if dry_run:
        return

    if not verify_data(original_items, items):
        click.echo("Aborting due to data verification failure.", err=True)
        return

    # Write categorized Bitwarden JSON — only folderId fields and the
    # folders array have been modified; all item data is preserved.
    bw_data["items"] = items
    bw_data["folders"] = folders

    output_path = Path(original_json).with_name(
        Path(original_json).stem + "_categorized.json"
    )
    output_path.write_text(
        json.dumps(bw_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    click.echo(f"Categorized entries written to {output_path}")


if __name__ == "__main__":
    apply()
