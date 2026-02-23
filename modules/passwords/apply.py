#!/usr/bin/env python3

"""Apply password categorization suggestions to the original CSV."""

import csv
import json
from typing import Optional

import click


def verify_data(
    original_entries: list[dict[str, str]],
    new_entries: list[dict[str, str]],
) -> bool:
    """Verify data integrity between original and modified CSV entries.

    Checks that row count matches and all fields except 'folder'
    are preserved between the original and new entry lists.

    Args:
        original_entries: Original CSV rows before categorization.
        new_entries: Modified CSV rows with updated folder assignments.

    Returns:
        True if data integrity holds, False if any corruption detected.
    """
    if len(original_entries) != len(new_entries):
        click.echo(
            f"Error: Row count mismatch! "
            f"Original: {len(original_entries)}, "
            f"New: {len(new_entries)}",
            err=True,
        )
        return False

    for i, (orig, new) in enumerate(zip(original_entries, new_entries, strict=True)):
        orig_fields = {k: v for k, v in orig.items() if k != "folder"}
        new_fields = {k: v for k, v in new.items() if k != "folder"}

        if orig_fields != new_fields:
            click.echo(f"Error: Data mismatch in row {i + 1}!", err=True)
            click.echo(f"Original: {orig_fields}", err=True)
            click.echo(f"New: {new_fields}", err=True)
            return False

    return True


@click.command()
@click.argument("suggestions_file", type=click.Path(exists=True))
@click.option(
    "--csv-file",
    default=None,
    help="Override CSV path (default: path from suggestions file)",
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
    csv_file: Optional[str],
    min_confidence: float,
    dry_run: bool,
) -> None:
    """Apply categorization suggestions to a password CSV.

    Reads a suggestions JSON file produced by the suggest command and
    applies the suggested folders to the original CSV, writing a new
    _categorized.csv file. Only suggestions meeting the minimum
    confidence threshold are applied.

    Args:
        suggestions_file: Path to the suggestions JSON file.
        csv_file: Override path to original CSV. If None, uses the
            path stored in the suggestions file.
        min_confidence: Minimum confidence threshold for applying
            a suggestion. Suggestions below this are skipped.
        dry_run: If True, print what would be applied without writing.
    """

    with open(suggestions_file) as f:
        data = json.load(f)

    suggestions = data["suggestions"]
    original_csv = csv_file or data.get("csv_file", "")

    if not original_csv:
        click.echo(
            "Error: No CSV file specified and none found in suggestions file.",
            err=True,
        )
        return

    suggestion_map: dict[tuple[str, str], tuple[str, float]] = {}
    for s in suggestions:
        key = (str(s["name"]), str(s["login_uri"]))
        suggestion_map[key] = (
            str(s["suggested_folder"]),
            float(s["confidence"]),
        )

    with open(original_csv) as f:
        reader = csv.DictReader(f)
        original_entries = list(reader)

    entries = [entry.copy() for entry in original_entries]

    applied = 0
    skipped_low_conf = 0

    for entry in entries:
        key = (entry.get("name", ""), entry.get("login_uri", ""))
        if key in suggestion_map:
            folder, confidence = suggestion_map[key]
            if confidence >= min_confidence:
                entry["folder"] = folder
                applied += 1
                if dry_run:
                    click.echo(
                        f"{entry['name']} ({entry['login_uri']}) "
                        f"-> {folder} ({confidence:.2f})"
                    )
            else:
                skipped_low_conf += 1

    click.echo(
        f"\n{applied} entries categorized, "
        f"{skipped_low_conf} skipped (below {min_confidence} confidence)"
    )

    if dry_run:
        return

    if not verify_data(original_entries, entries):
        click.echo("Aborting due to data verification failure.", err=True)
        return

    output_file = original_csv.replace(".csv", "_categorized.csv")
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=entries[0].keys())
        writer.writeheader()
        writer.writerows(entries)

    click.echo(f"Categorized entries written to {output_file}")


if __name__ == "__main__":
    apply()
