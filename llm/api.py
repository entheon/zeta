import json
import os
from collections.abc import Iterator, Mapping, Sequence
from typing import Any, Literal, Optional, Union, overload

import click
from ollama import (
    ChatResponse,
    Client,
    GenerateResponse,
    Message,
    Options,
)

MODEL = os.environ.get("ZETA_MODEL", "qwen3:8b")


class OllamaAPI:
    """Client wrapper for the Ollama API.

    This class provides a Pythonic interface to interact with Ollama's API,
    supporting both chat and completion endpoints with proper type hints.
    """

    def __init__(self, host: str = "http://localhost:11434") -> None:
        """Initialize the Ollama API client.

        Args:
            host: Host URL for Ollama API. Defaults to local instance.
        """
        self.client = Client(host=host)
        self.model = MODEL

    def generate(
        self,
        model: str,
        prompt: str,
        *,
        system: str = "",
        options: Optional[Union[Mapping[str, Any], Options]] = None,
        stream: Literal[False] = False,
    ) -> GenerateResponse:
        """Generate a completion from the model.

        Args:
            model: Name of the model to use.
            prompt: The prompt to generate from.
            system: System prompt to use. Defaults to empty string.
            options: Additional model parameters.
            stream: Must be False, streaming not supported.

        Returns:
            Single response from the model.
        """
        return self.client.generate(
            model=model,
            prompt=prompt,
            system=system,
            options=options or {},
            stream=stream,
        )

    @overload
    def chat(
        self,
        model: str,
        messages: Sequence[Union[Mapping[str, Any], Message]],
        stream: Literal[False] = False,
        options: Optional[Union[Mapping[str, Any], Options]] = None,
        keep_alive: Optional[str] = None,
    ) -> ChatResponse: ...

    @overload
    def chat(
        self,
        model: str,
        messages: Sequence[Union[Mapping[str, Any], Message]],
        stream: Literal[True],
        options: Optional[Union[Mapping[str, Any], Options]] = None,
        keep_alive: Optional[str] = None,
    ) -> Iterator[ChatResponse]: ...

    def chat(
        self,
        model: str,
        messages: Sequence[Union[Mapping[str, Any], Message]],
        stream: Literal[True, False] = False,
        options: Optional[Union[Mapping[str, Any], Options]] = None,
        keep_alive: Optional[str] = None,
    ) -> Union[ChatResponse, Iterator[ChatResponse]]:
        """Have a chat conversation with the model.

        Args:
            model: Name of the model to use.
            messages: List of messages.
                Format: [{"role": "user", "content": "Hello"}, ...].
            stream: Whether to stream the response.
            options: Additional model parameters.
            keep_alive: Duration to keep model loaded (e.g., "5m", "60m").
                If None, uses Ollama's default (5m).

        Returns:
            Single response or stream of responses based on stream parameter.
        """
        return self.client.chat(
            model=model,
            messages=messages,
            stream=stream,
            options=options or {},
            keep_alive=keep_alive,
        )

    def categorize(
        self,
        data: dict[str, str],
        system_prompt: str,
        valid_categories: list[str],
        default_category: str,
    ) -> dict[str, Any]:
        """Categorize data using the LLM.

        Sends a chat request with the system prompt and data, parses the JSON
        response, and validates the returned category.

        Args:
            data: Dictionary of data to categorize (JSON serialized as user
                message).
            system_prompt: Full system prompt with category definitions.
            valid_categories: List of valid category strings to validate
                against.
            default_category: Category to return on error or invalid response.

        Returns:
            Dict with "category" and "confidence" keys.
        """
        user_content = json.dumps(data)

        try:
            response = self.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                stream=False,
                keep_alive="60m",
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

                if category not in valid_categories:
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
