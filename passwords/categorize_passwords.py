#!/usr/bin/env python3

import csv
import json
from typing import Dict, List, Optional

import click

from llm.api import OllamaAPI
from passwords.models import Category


def categorize_with_ollama(
    entry: Dict[str, str], api: Optional[OllamaAPI] = None
) -> str:
    """Use Ollama to categorize the login based on login_uri and name."""
    if not entry.get("login_uri") and not entry.get("name"):
        return Category.NO_FOLDER.value

    if api is None:
        api = OllamaAPI()

    # Prepare context for the model
    prompt = f"""{{
    "url": "{entry.get('login_uri', '')}",
    "name": "{entry.get('name', '')}"
}}"""

    try:
        response = api.generate(model="ryanliu6/xipe", prompt=prompt, stream=False)
        result = response.response.strip()

        try:
            # Parse the JSON response
            categorization = json.loads(result)
            category = categorization["category"]
            confidence = categorization["confidence"]

            # Validate category and confidence
            if category not in Category.values():
                click.echo(f"Invalid category from model: {category}", err=True)
                return Category.NO_FOLDER.value

            # Use confidence thresholds from Modelfile
            if confidence >= 0.4 and category != Category.NO_FOLDER.value:
                return category
            return Category.NO_FOLDER.value

        except (json.JSONDecodeError, KeyError) as e:
            click.echo(f"Error parsing model response: {result} ({e})", err=True)
            return Category.NO_FOLDER.value

    except Exception as e:
        click.echo(f"Error calling Ollama: {e}", err=True)
        return Category.NO_FOLDER.value


def verify_data(
    original_entries: List[Dict[str, str]], new_entries: List[Dict[str, str]]
) -> bool:
    """Verify that no data was lost during processing."""
    if len(original_entries) != len(new_entries):
        click.echo(
            f"Error: Row count mismatch! "
            f"Original: {len(original_entries)}, "
            f"New: {len(new_entries)}",
            err=True,
        )
        return False

    # Verify all original fields except 'folder' are preserved
    for i, (orig, new) in enumerate(zip(original_entries, new_entries)):
        orig_fields = {k: v for k, v in orig.items() if k != "folder"}
        new_fields = {k: v for k, v in new.items() if k != "folder"}

        if orig_fields != new_fields:
            click.echo(f"Error: Data mismatch in row {i + 1}!", err=True)
            click.echo(f"Original: {orig_fields}", err=True)
            click.echo(f"New: {new_fields}", err=True)
            return False

    return True


@click.command()
@click.argument("csv_file", type=click.Path(exists=True))
@click.option(
    "--dry-run", is_flag=True, help="Show categorization without writing output file"
)
def categorize(csv_file: str, dry_run: bool):
    """Categorize login entries from a CSV file using Ollama."""
    # Process the input CSV
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        original_entries = list(reader)

    # Create a copy for processing
    entries = [entry.copy() for entry in original_entries]

    # Create single API instance for all entries
    api = OllamaAPI()

    # Process each entry
    for entry in entries:
        category = categorize_with_ollama(entry, api=api)
        entry["folder"] = category

    # Check for dry run
    if dry_run:
        for entry in entries:
            click.echo(f"{entry['name']} ({entry['login_uri']}) -> {entry['folder']}")
        return

    # Verify data integrity
    if not verify_data(original_entries, entries):
        click.echo("Aborting due to data verification failure.", err=True)
        return

    # Write the categorized entries back to a new CSV
    output_file = csv_file.replace(".csv", "_categorized.csv")
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=entries[0].keys())
        writer.writeheader()
        writer.writerows(entries)

    click.echo(f"Categorized entries written to {output_file}")


if __name__ == "__main__":
    categorize()
