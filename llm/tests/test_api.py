from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from llm import OllamaAPI


@pytest.fixture
def mock_client() -> Iterator[MagicMock]:
    with patch("llm.api.Client") as mock:
        yield mock


@pytest.fixture
def api(mock_client: MagicMock) -> OllamaAPI:
    return OllamaAPI()


def test_init(mock_client: MagicMock) -> None:
    api = OllamaAPI()

    mock_client.assert_called_once_with(host="http://localhost:11434")
    assert api.client == mock_client.return_value


def test_init_custom_host(mock_client: MagicMock) -> None:
    api = OllamaAPI(host="http://custom:8080")

    mock_client.assert_called_once_with(host="http://custom:8080")
    assert api.client == mock_client.return_value


def test_generate(api: OllamaAPI, mock_client: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.response = "Generated text"
    mock_client.return_value.generate.return_value = mock_response

    response = api.generate(model="llama2", prompt="Hello")

    mock_client.return_value.generate.assert_called_once_with(
        model="llama2",
        prompt="Hello",
        system="",
        options={},
        stream=False,
    )
    assert response == mock_response


def test_generate_with_options(api: OllamaAPI, mock_client: MagicMock) -> None:
    mock_response = MagicMock()
    mock_client.return_value.generate.return_value = mock_response
    options = {"temperature": 0.7}

    response = api.generate(
        model="llama2",
        prompt="Hello",
        system="Be helpful",
        options=options,
    )

    mock_client.return_value.generate.assert_called_once_with(
        model="llama2",
        prompt="Hello",
        system="Be helpful",
        options=options,
        stream=False,
    )
    assert response == mock_response


def test_chat(api: OllamaAPI, mock_client: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.message.content = "Chat response"
    mock_client.return_value.chat.return_value = mock_response
    messages = [{"role": "user", "content": "Hello"}]

    response = api.chat(model="llama2", messages=messages)

    mock_client.return_value.chat.assert_called_once_with(
        model="llama2",
        messages=messages,
        stream=False,
        options={},
    )
    assert response == mock_response


def test_chat_streaming(api: OllamaAPI, mock_client: MagicMock) -> None:
    mock_chunks = [MagicMock(), MagicMock()]
    mock_client.return_value.chat.return_value = iter(mock_chunks)
    messages = [{"role": "user", "content": "Hello"}]

    response = api.chat(model="llama2", messages=messages, stream=True)

    mock_client.return_value.chat.assert_called_once_with(
        model="llama2",
        messages=messages,
        stream=True,
        options={},
    )
    assert list(response) == mock_chunks
