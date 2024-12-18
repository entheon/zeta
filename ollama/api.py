from typing import Dict, List, Optional, Union
import ollama
from ollama import ChatResponse, GenerateResponse

class OllamaAPI:
    def __init__(self, host: str = "http://localhost:11434"):
        """Initialize the Ollama API client.

        Args:
            host (str): Host URL for Ollama API. Defaults to local instance.
        """
        self.client = ollama.Client(host=host)

    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict] = None,
        stream: bool = False
    ) -> Union[GenerateResponse, list[GenerateResponse]]:
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
            options=options,
            stream=stream
        )

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        options: Optional[Dict] = None
    ) -> Union[ChatResponse, list[ChatResponse]]:
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
            model=model,
            messages=messages,
            options=options,
            stream=stream
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
