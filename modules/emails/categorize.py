#!/usr/bin/env python3

import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

import click

from llm import MODEL, OllamaAPI
from modules.emails.models import EmailLabel, build_categorization_prompt


def categorize_email(
    email_data: dict[str, str],
    api: Optional[OllamaAPI] = None,
) -> dict[str, Any]:
    """Categorize a single email using the LLM.

    Args:
        email_data: Dictionary containing "subject" and "from_address".
        api: Optional OllamaAPI instance. If None, a new one is created.

    Returns:
        Dictionary with keys: "category", "subcategory", "labels", "confidence".
        If categorization fails, returns default "Uncategorized" values.
    """
    if api is None:
        api = OllamaAPI()

    subject = email_data.get("subject", "")
    from_address = email_data.get("from_address", "")

    if not subject and not from_address:
        return {
            "category": "Uncategorized",
            "subcategory": "Unknown",
            "labels": [],
            "confidence": 1.0,
        }

    user_content = json.dumps(
        {
            "subject": subject,
            "from": from_address,
        }
    )

    try:
        response = api.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": build_categorization_prompt()},
                {"role": "user", "content": user_content},
            ],
            stream=False,
            keep_alive="60m",
        )

        if not response.message.content:
            click.echo("Empty response from model", err=True)
            return {
                "category": "Uncategorized",
                "subcategory": "Unknown",
                "labels": [],
                "confidence": 0.0,
            }

        result = response.message.content.strip()

        try:
            categorization = json.loads(result)
            category = str(categorization.get("category", "Uncategorized"))
            subcategory = str(categorization.get("subcategory", "Unknown"))
            labels = categorization.get("labels", [])
            confidence = float(categorization.get("confidence", 0.0))

            valid_labels = [label for label in labels if label in EmailLabel.values()]

            return {
                "category": category,
                "subcategory": subcategory,
                "labels": valid_labels,
                "confidence": confidence,
            }

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            click.echo(f"Error parsing model response: {result} ({e})", err=True)
            return {
                "category": "Uncategorized",
                "subcategory": "Unknown",
                "labels": [],
                "confidence": 0.0,
            }

    except Exception as e:
        click.echo(f"Error calling Ollama: {e}", err=True)
        return {
            "category": "Uncategorized",
            "subcategory": "Unknown",
            "labels": [],
            "confidence": 0.0,
        }


def extract_domain(email_address: str) -> Optional[str]:
    """Extract the domain from an email address.

    Args:
        email_address: The email address string.

    Returns:
        The domain part of the email address (lowercased), or None if not found.
    """
    if "@" in email_address:
        return email_address.split("@")[-1].lower()
    return None


def generate_filter_suggestions(
    categorized_emails: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate potential email filter rules based on categorization patterns.

    Analyzes processed emails to find consistent patterns by sender domain
    or subject keywords that map to specific categories.

    Args:
        categorized_emails: List of processed email dictionaries.

    Returns:
        List of suggestion dictionaries with keys: "category", "confidence",
        "count", and either "from_domain" or "subject_pattern".
    """
    domain_categories: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    subject_patterns: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for email in categorized_emails:
        category = email["category"]
        subcategory = email["subcategory"]
        full_category = f"{category}/{subcategory}"
        confidence = email["confidence"]
        from_address = email["from"]
        subject = email["subject"].lower()

        domain = extract_domain(from_address)
        if domain:
            domain_categories[domain][full_category].append(confidence)

        words = subject.split()
        for word in words:
            if len(word) > 4:
                subject_patterns[word][full_category].append(confidence)

    suggestions = []

    for domain, categories in domain_categories.items():
        for category, confidences in categories.items():
            if len(confidences) >= 2:
                avg_confidence = sum(confidences) / len(confidences)
                suggestions.append(
                    {
                        "category": category,
                        "from_domain": domain,
                        "count": len(confidences),
                        "confidence": round(avg_confidence, 2),
                    }
                )

    for pattern, categories in subject_patterns.items():
        for category, confidences in categories.items():
            if len(confidences) >= 3:
                avg_confidence = sum(confidences) / len(confidences)
                suggestions.append(
                    {
                        "category": category,
                        "subject_pattern": pattern,
                        "count": len(confidences),
                        "confidence": round(avg_confidence, 2),
                    }
                )

    suggestions.sort(key=lambda x: (x["count"], x["confidence"]), reverse=True)
    return suggestions


def _load_existing_results(output_path: Path) -> tuple[list[dict[str, Any]], set[str]]:
    """Load existing categorization results from output file.

    Args:
        output_path: Path to the JSON output file.

    Returns:
        Tuple containing:
        - List of already categorized email dictionaries.
        - Set of file stems (IDs) that have been processed.
    """
    if not output_path.exists():
        return [], set()

    try:
        with open(output_path) as f:
            data = json.load(f)
        existing_emails = data.get("categorized_emails", [])
        processed_files = {email["file"] for email in existing_emails}
        return existing_emails, processed_files
    except (json.JSONDecodeError, KeyError) as e:
        click.echo(f"Warning: Could not load existing results: {e}", err=True)
        return [], set()


def _save_results(
    output_path: Path,
    categorized_emails: list[dict[str, Any]],
) -> None:
    """Save current results to output file.

    Args:
        output_path: Path to write the JSON output to.
        categorized_emails: List of email categorization results to save.
    """
    suggested_rules = generate_filter_suggestions(categorized_emails)
    output_data = {
        "categorized_emails": categorized_emails,
        "suggested_rules": suggested_rules,
    }
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)


@click.command()
@click.argument("emails_dir", type=click.Path(exists=True))
@click.option(
    "--output",
    default=None,
    help="Output file path (default: emails_categorized.json in EMAILS_DIR)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Print categorizations without writing output file",
)
@click.option(
    "--save-interval",
    default=100,
    help="Save results every N emails (default: 100)",
)
@click.option(
    "--no-resume",
    is_flag=True,
    help="Start fresh, ignoring any existing results",
)
def categorize(
    emails_dir: str,
    output: Optional[str],
    dry_run: bool,
    save_interval: int,
    no_resume: bool,
) -> None:
    """Categorize emails in a directory using LLM.

    Supports incremental saving and resume from interruptions.
    """
    emails_path = Path(emails_dir)

    if output is None:
        output = str(emails_path / "emails_categorized.json")

    output_path = Path(output)

    if not emails_path.is_dir():
        click.echo(f"Error: {emails_dir} is not a directory", err=True)
        return

    json_files = list(emails_path.glob("*.metadata.json"))

    if not json_files:
        click.echo(f"No metadata JSON files found in {emails_dir}", err=True)
        return

    # Load existing results for resume capability
    if no_resume or dry_run:
        categorized_emails: list[dict[str, Any]] = []
        processed_files: set[str] = set()
    else:
        categorized_emails, processed_files = _load_existing_results(output_path)
        if processed_files:
            click.echo("=" * 60)
            click.echo(f"RESUMING FROM {output}")
            click.echo(f"Found {len(processed_files)} previously processed emails.")
            click.echo("=" * 60)

    total_emails = len(json_files)
    remaining_files = [f for f in json_files if f.stem not in processed_files]
    remaining_count = len(remaining_files)

    if remaining_count == 0:
        click.echo("All emails already processed!")
        return

    click.echo(f"Found {total_emails} emails, {remaining_count} remaining to process")

    api = OllamaAPI()
    start_time = time.time()
    log_interval = max(10, remaining_count // 20)
    processed_this_run = 0

    for idx, json_file in enumerate(remaining_files, start=1):
        base_name = json_file.name.split(".", 1)[0]
        eml_file = json_file.parent / f"{base_name}.eml"

        if not eml_file.exists():
            click.echo(
                f"Warning: No matching .eml file for {json_file.name}",
                err=True,
            )
            continue

        with open(json_file) as f:
            email_data = json.load(f)

        payload = email_data.get("Payload", {})
        sender = payload.get("Sender", {})

        processed_data = {
            "subject": payload.get("Subject", ""),
            "from_address": sender.get("Address", ""),
        }

        result = categorize_email(processed_data, api=api)

        categorized_emails.append(
            {
                "file": json_file.stem,
                "subject": processed_data["subject"],
                "from": processed_data["from_address"],
                "category": result["category"],
                "subcategory": result["subcategory"],
                "labels": result["labels"],
                "confidence": result["confidence"],
            }
        )
        processed_this_run += 1

        if dry_run:
            labels_str = f" [{', '.join(result['labels'])}]" if result["labels"] else ""
            click.echo(
                f"{json_file.stem}: {email_data.get('subject', 'N/A')} "
                f"-> {result['category']}/{result['subcategory']}{labels_str} "
                f"({result['confidence']:.2f})"
            )

        # Incremental save
        if not dry_run and processed_this_run % save_interval == 0:
            _save_results(output_path, categorized_emails)
            click.echo(f"  [Saved progress: {len(categorized_emails)} emails]")

        if idx % log_interval == 0 or idx == remaining_count:
            elapsed = time.time() - start_time
            avg_time = elapsed / idx
            remaining = (remaining_count - idx) * avg_time
            percent = (idx / remaining_count) * 100

            eta_minutes = int(remaining // 60)
            eta_seconds = int(remaining % 60)
            if eta_minutes > 0:
                eta_str = f"{eta_minutes}m {eta_seconds}s"
            else:
                eta_str = f"{eta_seconds}s"

            click.echo(
                f"Processing {idx}/{remaining_count} ({percent:.1f}%) - "
                f"avg {avg_time:.1f}s/email - ETA: ~{eta_str}"
            )

    total_time = time.time() - start_time
    total_minutes = int(total_time // 60)
    total_seconds = int(total_time % 60)

    if dry_run:
        click.echo(f"\nCompleted in {total_minutes}m {total_seconds}s")
        return

    # Final save
    _save_results(output_path, categorized_emails)

    suggested_rules = generate_filter_suggestions(categorized_emails)

    click.echo(
        f"\nCategorized {processed_this_run} emails this run "
        f"({len(categorized_emails)} total) in {total_minutes}m {total_seconds}s"
    )
    click.echo(f"Generated {len(suggested_rules)} filter suggestions")
    click.echo(f"Results written to {output}")


if __name__ == "__main__":
    categorize()
