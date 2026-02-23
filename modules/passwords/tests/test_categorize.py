from typing import Any
from unittest.mock import MagicMock

import pytest

from modules.passwords.apply import verify_data
from modules.passwords.categorize import categorize_with_ollama
from modules.shared.models import CategorizeResult, Category


@pytest.fixture
def mock_api() -> MagicMock:
    return MagicMock()


def test_categorize_with_ollama(mock_api: MagicMock) -> None:
    mock_api.categorize.return_value = CategorizeResult(
        category="Finance",
        confidence=0.9,
    )

    entry = {"login_uri": "https://bank.com", "name": "My Bank"}
    result = categorize_with_ollama(entry, api=mock_api)

    assert result.category == "Finance"
    assert result.confidence == 0.9
    mock_api.categorize.assert_called_once()


def test_categorize_with_ollama_empty_entry(mock_api: MagicMock) -> None:
    entry = {"login_uri": "", "name": ""}
    result = categorize_with_ollama(entry, api=mock_api)

    assert result.category == Category.UNCATEGORIZED.value
    assert result.confidence == 0.0
    mock_api.categorize.assert_not_called()


def test_categorize_with_ollama_uncategorized(mock_api: MagicMock) -> None:
    mock_api.categorize.return_value = CategorizeResult(
        category=Category.UNCATEGORIZED.value,
        confidence=0.0,
    )

    entry = {"login_uri": "https://example.com", "name": "Example"}
    result = categorize_with_ollama(entry, api=mock_api)

    assert result.category == Category.UNCATEGORIZED.value


@pytest.mark.parametrize(
    ("original", "new", "expected"),
    [
        pytest.param(
            [
                {"name": "A", "login": {}, "folderId": None},
                {"name": "B", "login": {}, "folderId": None},
            ],
            [
                {"name": "A", "login": {}, "folderId": "folder-1"},
                {"name": "B", "login": {}, "folderId": "folder-2"},
            ],
            True,
            id="valid",
        ),
        pytest.param(
            [{"name": "A", "login": {}, "folderId": None}],
            [
                {"name": "A", "login": {}, "folderId": "folder-1"},
                {"name": "B", "login": {}, "folderId": "folder-2"},
            ],
            False,
            id="count_mismatch",
        ),
        pytest.param(
            [{"name": "A", "login": {}, "folderId": None}],
            [{"name": "Changed", "login": {}, "folderId": "folder-1"}],
            False,
            id="field_mismatch",
        ),
    ],
)
def test_verify_data(
    original: list[dict[str, Any]],
    new: list[dict[str, Any]],
    expected: bool,
) -> None:
    assert verify_data(original, new) is expected
