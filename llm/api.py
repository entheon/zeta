from typing import Any, Iterator, Literal, Mapping, Optional, Sequence, Union

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
            host (str): Host URL for Ollama API. Defaults to local instance.
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
            model (str): Name of the model to use
            prompt (str): The prompt to generate from
            system (str): System prompt to use. Defaults to empty string.
            options (Union[Mapping[str, Any], Options], optional): Additional model
                parameters
            stream (Literal[False]): Must be False, streaming not supported

        Returns:
            GenerateResponse: Single response from the model
        """
        return self.client.generate(
            model=model,
            prompt=prompt,
            system=system,
            options=options or {},
            stream=stream,
        )

    def chat(
        self,
        model: str,
        messages: Sequence[Union[Mapping[str, Any], Message]],
        stream: Literal[True, False] = False,
        options: Optional[Union[Mapping[str, Any], Options]] = None,
    ) -> Union[ChatResponse, Iterator[ChatResponse]]:
        """Have a chat conversation with the model.

        Args:
            model (str): Name of the model to use
            messages (Sequence[Union[Mapping[str, Any], Message]]): List of messages
                Format: [{"role": "user", "content": "Hello"}, ...]
            stream (Literal[True, False]): Whether to stream the response
            options (Union[Mapping[str, Any], Options], optional): Additional model
                parameters

        Returns:
            Union[ChatResponse, Iterator[ChatResponse]]: Single response or stream of
                responses
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
            ListResponse: List of available models and their details
        """
        return self.client.list()

    def pull_model(self, model: str) -> None:
        """Pull a model from the Ollama library.

        Args:
            model (str): Name of the model to pull
        """
        self.client.pull(model)
