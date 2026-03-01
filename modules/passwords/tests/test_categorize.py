from typing import Any
from unittest.mock import MagicMock

import pytest

from modules.passwords.apply import verify_data
from modules.passwords.categorize import (
    _build_folder_map,
    _extract_login_uri,
    categorize_with_ollama,
)
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


def test_extract_login_uri() -> None:
    item = {"login": {"uris": [{"uri": "https://bank.com"}]}}
    assert _extract_login_uri(item) == "https://bank.com"


def test_extract_login_uri_no_login() -> None:
    assert _extract_login_uri({}) == ""


def test_extract_login_uri_empty_uris() -> None:
    item: dict[str, Any] = {"login": {"uris": []}}
    assert _extract_login_uri(item) == ""


def test_build_folder_map() -> None:
    data = {"folders": [{"id": "1", "name": "Work"}, {"id": "2", "name": "Personal"}]}
    assert _build_folder_map(data) == {"1": "Work", "2": "Personal"}


def test_build_folder_map_empty() -> None:
    assert _build_folder_map({}) == {}
