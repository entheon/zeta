#!/usr/bin/env python3

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

import click

from llm import OllamaAPI
from modules.emails.models import EmailCategory

MODEL = os.environ.get("ZETA_MODEL", "qwen3:8b")


def categorize_email(
    email_data: dict[str, str],
    api: Optional[OllamaAPI] = None,
) -> dict[str, Any]:
    if api is None:
        api = OllamaAPI()

    subject = email_data.get("subject", "")
    from_address = email_data.get("from_address", "")

    if not subject and not from_address:
        return {
            "category": EmailCategory.UNCATEGORIZED.value,
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
                {"role": "system", "content": EmailCategory.build_system_prompt()},
                {"role": "user", "content": user_content},
            ],
            stream=False,
        )

        if not response.message.content:
            click.echo("Empty response from model", err=True)
            return {
                "category": EmailCategory.UNCATEGORIZED.value,
                "confidence": 0.0,
            }

        result = response.message.content.strip()

        try:
            categorization = json.loads(result)
            category = str(categorization["category"])
            confidence = float(categorization["confidence"])

            if category not in EmailCategory.values():
                click.echo(f"Invalid category from model: {category}", err=True)
                return {
                    "category": EmailCategory.UNCATEGORIZED.value,
                    "confidence": 0.0,
                }

            return {
                "category": category,
                "confidence": confidence,
            }

        except (json.JSONDecodeError, KeyError) as e:
            click.echo(f"Error parsing model response: {result} ({e})", err=True)
            return {
                "category": EmailCategory.UNCATEGORIZED.value,
                "confidence": 0.0,
            }

    except Exception as e:
        click.echo(f"Error calling Ollama: {e}", err=True)
        return {
            "category": EmailCategory.UNCATEGORIZED.value,
            "confidence": 0.0,
        }


def extract_domain(email_address: str) -> Optional[str]:
    if "@" in email_address:
        return email_address.split("@")[-1].lower()
    return None


def generate_filter_suggestions(
    categorized_emails: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    domain_categories: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    subject_patterns: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for email in categorized_emails:
        category = email["category"]
        confidence = email["confidence"]
        from_address = email["from"]
        subject = email["subject"].lower()

        domain = extract_domain(from_address)
        if domain:
            domain_categories[domain][category].append(confidence)

        words = subject.split()
        for word in words:
            if len(word) > 4:
                subject_patterns[word][category].append(confidence)

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


@click.command()
@click.argument("emails_dir", type=click.Path(exists=True))
@click.option(
    "--output",
    default="emails_categorized.json",
    help="Output file path",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Print categorizations without writing output file",
)
def categorize(emails_dir: str, output: str, dry_run: bool) -> None:
    emails_path = Path(emails_dir)

    if not emails_path.is_dir():
        click.echo(f"Error: {emails_dir} is not a directory", err=True)
        return

    json_files = list(emails_path.glob("*.json"))

    if not json_files:
        click.echo(f"No JSON files found in {emails_dir}", err=True)
        return

    api = OllamaAPI()
    categorized_emails = []

    for json_file in json_files:
        eml_file = json_file.with_suffix(".eml")

        if not eml_file.exists():
            click.echo(f"Warning: No matching .eml file for {json_file.name}", err=True)
            continue

        with open(json_file) as f:
            email_data = json.load(f)

        result = categorize_email(email_data, api=api)

        categorized_emails.append(
            {
                "file": json_file.stem,
                "subject": email_data.get("subject", ""),
                "from": email_data.get("from_address", ""),
                "category": result["category"],
                "confidence": result["confidence"],
            }
        )

        if dry_run:
            click.echo(
                f"{json_file.stem}: {email_data.get('subject', 'N/A')} "
                f"-> {result['category']} ({result['confidence']:.2f})"
            )

    if dry_run:
        return

    suggested_rules = generate_filter_suggestions(categorized_emails)

    output_data = {
        "categorized_emails": categorized_emails,
        "suggested_rules": suggested_rules,
    }

    with open(output, "w") as f:
        json.dump(output_data, f, indent=2)

    click.echo(f"Categorized {len(categorized_emails)} emails")
    click.echo(f"Generated {len(suggested_rules)} filter suggestions")
    click.echo(f"Results written to {output}")


if __name__ == "__main__":
    categorize()
