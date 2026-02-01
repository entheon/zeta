from collections.abc import Iterator, Mapping, Sequence
from typing import Any, Literal, Optional, Union, overload

from ollama import (
    ChatResponse,
    Client,
    GenerateResponse,
    ListResponse,
    Message,
    Options,
)


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
    ) -> ChatResponse: ...

    @overload
    def chat(
        self,
        model: str,
        messages: Sequence[Union[Mapping[str, Any], Message]],
        stream: Literal[True],
        options: Optional[Union[Mapping[str, Any], Options]] = None,
    ) -> Iterator[ChatResponse]: ...

    def chat(
        self,
        model: str,
        messages: Sequence[Union[Mapping[str, Any], Message]],
        stream: Literal[True, False] = False,
        options: Optional[Union[Mapping[str, Any], Options]] = None,
    ) -> Union[ChatResponse, Iterator[ChatResponse]]:
        """Have a chat conversation with the model.

        Args:
            model: Name of the model to use.
            messages: List of messages.
                Format: [{"role": "user", "content": "Hello"}, ...].
            stream: Whether to stream the response.
            options: Additional model parameters.

        Returns:
            Single response or stream of responses based on stream parameter.
        """
        return self.client.chat(
            model=model,
            messages=messages,
            stream=stream,
            options=options or {},
        )

    def list_models(self) -> ListResponse:
        """List all available models.

        Returns:
            List of available models and their details.
        """
        return self.client.list()

    def pull_model(self, model: str) -> None:
        """Pull a model from the Ollama library.

        Args:
            model: Name of the model to pull.
        """
        self.client.pull(model)
