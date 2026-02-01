# Ollama API

A Python wrapper for the Ollama API, providing a simple interface to interact with local Ollama models.

## Features

- Text generation and chat with streaming support
- Model management (listing and pulling)
- Type-safe API with proper Literal types

## Usage

```python
from llm import OllamaAPI

api = OllamaAPI()

# Generate text
response = api.generate(model="llama2", prompt="Write a haiku about coding")
print(response.response)

# Chat conversation
messages = [{"role": "user", "content": "What is the capital of France?"}]
response = api.chat(model="llama2", messages=messages)
print(response.message.content)

# Streaming chat
for chunk in api.chat(model="llama2", messages=messages, stream=True):
    print(chunk.message.content, end="")

# Model management
models = api.list_models()
api.pull_model("llama2")
```

## Requirements

- Python 3.8+
- ollama Python package
- Local Ollama instance running
