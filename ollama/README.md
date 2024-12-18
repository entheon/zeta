# Ollama API

A Python wrapper for the Ollama API, providing a simple interface to interact with local Ollama models.

## Features

- Simple interface for text generation and chat
- Model management (listing and pulling models)
- Support for streaming responses
- Built on the official Ollama Python client

## Usage

### Basic Generation

```python
from ollama.api import OllamaAPI

api = OllamaAPI()

# Generate text
response = api.generate(
    model="llama2",
    prompt="Write a haiku about coding",
)
print(response.response)
```

### Chat Conversations

```python
# Have a chat conversation
messages = [
    {"role": "user", "content": "What is the capital of France?"}
]
response = api.chat(
    model="llama2",
    messages=messages
)
print(response.message.content)
```

### Streaming Responses

```python
# Stream a generation
for chunk in api.generate(
    model="llama2",
    prompt="Tell me a story",
    stream=True
):
    print(chunk.response, end="", flush=True)
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

- `generate(model: str, prompt: str, system: Optional[str] = None, options: Optional[Dict] = None, stream: bool = False)`
  - Generate text from a prompt
  - Returns `GenerateResponse` or list of `GenerateResponse` if streaming

- `chat(model: str, messages: List[Dict[str, str]], stream: bool = False, options: Optional[Dict] = None)`
  - Have a chat conversation
  - Returns `ChatResponse` or list of `ChatResponse` if streaming

- `list_models() -> List[Dict]`
  - List available models

- `pull_model(model: str) -> None`
  - Pull a model from Ollama library

## Requirements

- Python 3.8+
- ollama Python package
- Local Ollama instance running
