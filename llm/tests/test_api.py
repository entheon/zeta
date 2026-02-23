import json
from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from llm.api import OllamaAPI
from llm.constants import MODEL
from modules.shared.models import CategorizeResult


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


def test_model_default(api: OllamaAPI) -> None:
    assert api.model == MODEL


@patch.dict("os.environ", {"ZETA_MODEL": "llama3"})
def test_model_from_envar(mock_client: MagicMock) -> None:
    import importlib

    import llm.api
    import llm.constants

    importlib.reload(llm.constants)
    importlib.reload(llm.api)
    api = llm.api.OllamaAPI()
    assert api.model == "llama3"

    importlib.reload(llm.constants)
    importlib.reload(llm.api)


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
        keep_alive=None,
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
        keep_alive=None,
    )
    assert list(response) == mock_chunks


def test_categorize_success(api: OllamaAPI, mock_client: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.message.content = json.dumps(
        {"category": "Finance", "confidence": 0.9}
    )
    mock_client.return_value.chat.return_value = mock_response

    result = api.categorize(
        data={"url": "https://bank.com"},
        system_prompt="Test prompt",
        valid_categories=["Finance", "Shopping"],
        default_category="Uncategorized",
    )

    assert result == CategorizeResult(category="Finance", confidence=0.9)


def test_categorize_invalid_category(api: OllamaAPI, mock_client: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.message.content = json.dumps(
        {"category": "InvalidCategory", "confidence": 0.9}
    )
    mock_client.return_value.chat.return_value = mock_response

    result = api.categorize(
        data={"url": "https://example.com"},
        system_prompt="Test prompt",
        valid_categories=["Finance", "Shopping"],
        default_category="Uncategorized",
    )

    assert result == CategorizeResult(category="Uncategorized", confidence=0.0)


def test_categorize_invalid_json(api: OllamaAPI, mock_client: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.message.content = "not valid json"
    mock_client.return_value.chat.return_value = mock_response

    result = api.categorize(
        data={"url": "https://example.com"},
        system_prompt="Test prompt",
        valid_categories=["Finance"],
        default_category="Uncategorized",
    )

    assert result == CategorizeResult(category="Uncategorized", confidence=0.0)


def test_categorize_empty_response(api: OllamaAPI, mock_client: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.message.content = ""
    mock_client.return_value.chat.return_value = mock_response

    result = api.categorize(
        data={"url": "https://example.com"},
        system_prompt="Test prompt",
        valid_categories=["Finance"],
        default_category="Uncategorized",
    )

    assert result == CategorizeResult(category="Uncategorized", confidence=0.0)


def test_categorize_api_exception(api: OllamaAPI, mock_client: MagicMock) -> None:
    mock_client.return_value.chat.side_effect = Exception("Connection failed")

    result = api.categorize(
        data={"url": "https://example.com"},
        system_prompt="Test prompt",
        valid_categories=["Finance"],
        default_category="Uncategorized",
    )

    assert result == CategorizeResult(category="Uncategorized", confidence=0.0)
