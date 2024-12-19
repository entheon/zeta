from typing import Any, Dict, List, Literal, Optional, Union, overload

from ollama import ChatResponse, Client, GenerateResponse


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

    @overload
    def generate(
        self,
        model: str,
        prompt: str,
        *,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        stream: Literal[False] = False,
    ) -> GenerateResponse:
        ...

    @overload
    def generate(
        self,
        model: str,
        prompt: str,
        *,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        stream: Literal[True],
    ) -> List[GenerateResponse]:
        ...

    def generate(
        self,
        model: str,
        prompt: str,
        *,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> Union[GenerateResponse, List[GenerateResponse]]:
        """Generate a completion from the model.

        Args:
            model (str): Name of the model to use
            prompt (str): The prompt to generate from
            system (str, optional): System prompt to use
            options (Dict, optional): Additional model parameters
            stream (bool): Whether to stream the response

        Returns:
            Union[GenerateResponse, list[GenerateResponse]]: Response from the model
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
        messages: List[Dict[str, str]],
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None,
    ) -> Union[ChatResponse, List[ChatResponse]]:
        """Have a chat conversation with the model.

        Args:
            model (str): Name of the model to use
            messages (List[Dict[str, str]]): List of messages in the conversation
                Format: [{"role": "user", "content": "Hello"}, ...]
            stream (bool): Whether to stream the response
            options (Optional[Dict]): Additional model parameters

        Returns:
            Union[ChatResponse, list[ChatResponse]]: Response from the model
        """
        return self.client.chat(
            model=model, messages=messages, stream=stream, options=options or {}
        )

    def list_models(self) -> List[Dict]:
        """List all available models.

        Returns:
            List[Dict]: List of available models and their details
        """
        return self.client.list()

    def pull_model(self, model: str) -> None:
        """Pull a model from the Ollama library.

        Args:
            model (str): Name of the model to pull
        """
        self.client.pull(model)
