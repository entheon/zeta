#!/usr/bin/env python3

import json
import os
from typing import Any, Optional

import click

from llm import OllamaAPI

MODEL = os.environ.get("ZETA_MODEL", "qwen3:8b")


def categorize_with_llm(
    data: dict[str, str],
    category_enum: Any,
    default_category: str,
    api: Optional[OllamaAPI] = None,
) -> dict[str, Any]:
    """Call LLM to categorize data and parse response.

    Args:
        data: Dictionary of data to categorize (will be JSON serialized).
        category_enum: Enum class with values() and build_system_prompt() methods.
        default_category: Category to return on error or low confidence.
        api: Optional OllamaAPI instance to reuse. Creates new one if None.

    Returns:
        Dict with "category" and "confidence" keys.
    """
    if api is None:
        api = OllamaAPI()

    user_content = json.dumps(data)

    try:
        response = api.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": category_enum.build_system_prompt()},
                {"role": "user", "content": user_content},
            ],
            stream=False,
        )

        if not response.message.content:
            click.echo("Empty response from model", err=True)
            return {
                "category": default_category,
                "confidence": 0.0,
            }

        result = response.message.content.strip()

        try:
            categorization = json.loads(result)
            category = str(categorization["category"])
            confidence = float(categorization["confidence"])

            if category not in category_enum.values():
                click.echo(f"Invalid category from model: {category}", err=True)
                return {
                    "category": default_category,
                    "confidence": 0.0,
                }

            return {
                "category": category,
                "confidence": confidence,
            }

        except (json.JSONDecodeError, KeyError) as e:
            click.echo(f"Error parsing model response: {result} ({e})", err=True)
            return {
                "category": default_category,
                "confidence": 0.0,
            }

    except Exception as e:
        click.echo(f"Error calling Ollama: {e}", err=True)
        return {
            "category": default_category,
            "confidence": 0.0,
        }
