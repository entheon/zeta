# Ollama API

A Python wrapper for the Ollama API, providing a simple interface to interact with local Ollama models.

## Features

- Simple interface for text generation and chat
- Model management (listing and pulling models)
- Support for streaming responses
- Built on the official Ollama Python client
- Type-safe API with proper Literal types

## Usage

### Basic Generation

```python
from llm.api import OllamaAPI

api = OllamaAPI()

# Generate text (non-streaming)
response = api.generate(
    model="llama2",
    prompt="Write a haiku about coding",
    stream=False,  # Type system enforces non-streaming
)
print(response.response)
```

### Chat Conversations

```python
from typing import Dict, Any

# Have a chat conversation
messages: list[Dict[str, Any]] = [
    {"role": "user", "content": "What is the capital of France?"}
]
response = api.chat(
    model="llama2",
    messages=messages,
    stream=False,
)
print(response.message.content)
```

### Model Management

```python
# List available models
models = api.list_models()
print(models)

# Pull a new model
api.pull_model("llama2")
```

## API Reference

### OllamaAPI

```python
class OllamaAPI:
    def __init__(self, host: str = "http://localhost:11434")
```

#### Methods

- `generate(model: str, prompt: str, *, system: str = "", options: Optional[Union[Mapping[str, Any], Options]] = None, stream: Literal[False] = False) -> GenerateResponse`
  - Generate text from a prompt
  - Non-streaming only, returns single `GenerateResponse`

- `chat(model: str, messages: Sequence[Union[Mapping[str, Any], Message]], stream: Literal[True, False] = False, options: Optional[Union[Mapping[str, Any], Options]] = None) -> Union[ChatResponse, Iterator[ChatResponse]]`
  - Have a chat conversation
  - Returns `ChatResponse` or `Iterator[ChatResponse]` based on `stream`

- `list_models() -> ListResponse`
  - List available models

- `pull_model(model: str) -> None`
  - Pull a model from Ollama library

## Requirements

- Python 3.8+
- ollama Python package
- Local Ollama instance running
