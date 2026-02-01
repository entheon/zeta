import json
from unittest.mock import MagicMock

import pytest

from modules.passwords.categorize import categorize_with_ollama, verify_data
from modules.passwords.models import Category


@pytest.fixture
def mock_api():
    return MagicMock()


def test_categorize_with_ollama(mock_api):
    mock_response = MagicMock()
    mock_response.message.content = json.dumps({
        "category": "Finance",
        "confidence": 0.9
    })
    mock_api.chat.return_value = mock_response

    entry = {"login_uri": "https://bank.com", "name": "My Bank"}
    result = categorize_with_ollama(entry, api=mock_api)

    assert result == "Finance"
    mock_api.chat.assert_called_once()


def test_categorize_with_ollama_empty_entry(mock_api):
    entry = {"login_uri": "", "name": ""}
    result = categorize_with_ollama(entry, api=mock_api)

    assert result == Category.NO_FOLDER.value
    mock_api.chat.assert_not_called()


def test_categorize_with_ollama_low_confidence(mock_api):
    mock_response = MagicMock()
    mock_response.message.content = json.dumps({
        "category": "Finance",
        "confidence": 0.3
    })
    mock_api.chat.return_value = mock_response

    entry = {"login_uri": "https://unknown.com", "name": "Unknown"}
    result = categorize_with_ollama(entry, api=mock_api)

    assert result == Category.NO_FOLDER.value


def test_categorize_with_ollama_invalid_category(mock_api):
    mock_response = MagicMock()
    mock_response.message.content = json.dumps({
        "category": "InvalidCategory",
        "confidence": 0.9
    })
    mock_api.chat.return_value = mock_response

    entry = {"login_uri": "https://example.com", "name": "Example"}
    result = categorize_with_ollama(entry, api=mock_api)

    assert result == Category.NO_FOLDER.value


def test_categorize_with_ollama_invalid_json(mock_api):
    mock_response = MagicMock()
    mock_response.message.content = "not valid json"
    mock_api.chat.return_value = mock_response

    entry = {"login_uri": "https://example.com", "name": "Example"}
    result = categorize_with_ollama(entry, api=mock_api)

    assert result == Category.NO_FOLDER.value


def test_categorize_with_ollama_empty_response(mock_api):
    mock_response = MagicMock()
    mock_response.message.content = ""
    mock_api.chat.return_value = mock_response

    entry = {"login_uri": "https://example.com", "name": "Example"}
    result = categorize_with_ollama(entry, api=mock_api)

    assert result == Category.NO_FOLDER.value


def test_verify_data():
    original = [
        {"name": "Test1", "login_uri": "https://a.com", "folder": ""},
        {"name": "Test2", "login_uri": "https://b.com", "folder": ""},
    ]
    new = [
        {"name": "Test1", "login_uri": "https://a.com", "folder": "Finance"},
        {"name": "Test2", "login_uri": "https://b.com", "folder": "Shopping"},
    ]

    assert verify_data(original, new) is True


def test_verify_data_count_mismatch():
    original = [{"name": "Test1", "login_uri": "https://a.com", "folder": ""}]
    new = [
        {"name": "Test1", "login_uri": "https://a.com", "folder": "Finance"},
        {"name": "Test2", "login_uri": "https://b.com", "folder": "Shopping"},
    ]

    assert verify_data(original, new) is False


def test_verify_data_field_mismatch():
    original = [{"name": "Test1", "login_uri": "https://a.com", "folder": ""}]
    new = [{"name": "Changed", "login_uri": "https://a.com", "folder": "Finance"}]

    assert verify_data(original, new) is False
