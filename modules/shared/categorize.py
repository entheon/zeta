import time
from typing import Optional

import click

from llm.api import OllamaAPI
from modules.shared.models import CategorizeResult, Category


def categorize_item(
    data: dict[str, str],
    task_description: str,
    empty_check_fields: list[str],
    api: Optional[OllamaAPI] = None,
) -> CategorizeResult:
    """Categorize a single item using the LLM.

    Generic categorization wrapper that handles empty-input checks,
    API instantiation, and delegates to the OllamaAPI.categorize()
    method with the shared Category enum.

    Args:
        data: Key-value pairs describing the item to categorize,
            serialized as JSON for the LLM user message.
        task_description: Human-readable description of the item
            type, e.g. "a password entry (URL and name)".
        empty_check_fields: List of keys in data to check for
            non-empty values. If all are empty, returns
            Uncategorized immediately.
        api: Optional OllamaAPI instance. Creates a new one if None.

    Returns:
        CategorizeResult with category and confidence fields.
    """
    if all(not data.get(field) for field in empty_check_fields):
        return CategorizeResult(
            category=Category.UNCATEGORIZED.value,
            confidence=0.0,
        )

    if api is None:
        api = OllamaAPI()

    return api.categorize(
        data=data,
        system_prompt=Category.build_system_prompt(task_description),
        valid_categories=Category.values(),
        default_category=Category.UNCATEGORIZED.value,
    )


def log_progress(
    idx: int,
    total: int,
    start_time: float,
    item_noun: str = "items",
) -> None:
    """Log categorization progress with ETA.

    Prints a single line showing current progress, average time per
    item, and estimated time remaining. Intended to be called at
    regular intervals during a categorization loop.

    Args:
        idx: Current 1-based index in the loop.
        total: Total number of items to process.
        start_time: The `time.time()` value from before the loop.
        item_noun: Noun for the items, e.g. "entries" or "emails".
    """
    elapsed = time.time() - start_time
    avg_time = elapsed / idx
    remaining = (total - idx) * avg_time
    pct = (idx / total) * 100

    eta_min = int(remaining // 60)
    eta_sec = int(remaining % 60)
    eta_str = f"{eta_min}m {eta_sec}s" if eta_min else f"{eta_sec}s"

    click.echo(
        f"Processing {idx}/{total} ({pct:.1f}%) "
        f"- avg {avg_time:.1f}s/{item_noun} - ETA: ~{eta_str}"
    )
