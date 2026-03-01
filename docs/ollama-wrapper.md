# Ollama API Wrapper

A Python wrapper for the Ollama API.

## Usage

```python
from llm import OllamaAPI

api = OllamaAPI()

# Generate text
response = api.generate(model="qwen3", prompt="Write a haiku about coding")
print(response.response)

# Chat conversation
messages = [{"role": "user", "content": "What is the capital of France?"}]
response = api.chat(model="qwen3", messages=messages)
print(response.message.content)

# Streaming chat
for chunk in api.chat(model="qwen3", messages=messages, stream=True):
    print(chunk.message.content, end="")
```

## Requirements

- Local Ollama instance running at `http://localhost:11434`
