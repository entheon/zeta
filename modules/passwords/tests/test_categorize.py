from unittest.mock import MagicMock

import pytest

from modules.passwords.apply import verify_data
from modules.passwords.categorize import categorize_with_ollama
from modules.shared import Category


@pytest.fixture
def mock_api() -> MagicMock:
    return MagicMock()


def test_categorize_with_ollama(mock_api: MagicMock) -> None:
    mock_api.categorize.return_value = {
        "category": "Finance",
        "confidence": 0.9,
    }

    entry = {"login_uri": "https://bank.com", "name": "My Bank"}
    result = categorize_with_ollama(entry, api=mock_api)

    assert result == {"category": "Finance", "confidence": 0.9}
    mock_api.categorize.assert_called_once()


def test_categorize_with_ollama_empty_entry(mock_api: MagicMock) -> None:
    entry = {"login_uri": "", "name": ""}
    result = categorize_with_ollama(entry, api=mock_api)

    assert result["category"] == Category.UNCATEGORIZED.value
    assert result["confidence"] == 0.0
    mock_api.categorize.assert_not_called()


def test_categorize_with_ollama_uncategorized(mock_api: MagicMock) -> None:
    mock_api.categorize.return_value = {
        "category": Category.UNCATEGORIZED.value,
        "confidence": 0.0,
    }

    entry = {"login_uri": "https://example.com", "name": "Example"}
    result = categorize_with_ollama(entry, api=mock_api)

    assert result["category"] == Category.UNCATEGORIZED.value


@pytest.mark.parametrize(
    ("original", "new", "expected"),
    [
        pytest.param(
            [
                {"name": "A", "login_uri": "https://a.com", "folder": ""},
                {"name": "B", "login_uri": "https://b.com", "folder": ""},
            ],
            [
                {"name": "A", "login_uri": "https://a.com", "folder": "Finance"},
                {"name": "B", "login_uri": "https://b.com", "folder": "Shopping"},
            ],
            True,
            id="valid",
        ),
        pytest.param(
            [{"name": "A", "login_uri": "https://a.com", "folder": ""}],
            [
                {"name": "A", "login_uri": "https://a.com", "folder": "Finance"},
                {"name": "B", "login_uri": "https://b.com", "folder": "Shopping"},
            ],
            False,
            id="count_mismatch",
        ),
        pytest.param(
            [{"name": "A", "login_uri": "https://a.com", "folder": ""}],
            [{"name": "Changed", "login_uri": "https://a.com", "folder": "Finance"}],
            False,
            id="field_mismatch",
        ),
    ],
)
def test_verify_data(
    original: list[dict[str, str]],
    new: list[dict[str, str]],
    expected: bool,
) -> None:
    assert verify_data(original, new) is expected
