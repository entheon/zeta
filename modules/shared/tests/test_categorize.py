import time
from unittest.mock import MagicMock, patch

import pytest

from modules.shared.categorize import categorize_item, log_progress
from modules.shared.models import CategorizeResult, Category


def test_log_progress(capsys: pytest.CaptureFixture[str]) -> None:
    start = time.time() - 10
    log_progress(5, 10, start, "items")
    out = capsys.readouterr().out
    assert "5/10" in out
    assert "50.0%" in out


def test_log_progress_eta_minutes(capsys: pytest.CaptureFixture[str]) -> None:
    start = time.time() - 120
    log_progress(1, 100, start, "emails")
    out = capsys.readouterr().out
    assert "1/100" in out
    assert "m " in out


def test_categorize_item_creates_api() -> None:
    with patch("modules.shared.categorize.OllamaAPI") as mock_cls:
        mock_api = MagicMock()
        mock_cls.return_value = mock_api
        mock_api.categorize.return_value = CategorizeResult(
            category="Finance", confidence=0.9
        )
        result = categorize_item({"name": "bank"}, "a password entry", ["name"])
        mock_cls.assert_called_once()
        assert result.category == "Finance"


def test_categorize_item_empty_fields() -> None:
    mock_api = MagicMock()
    result = categorize_item({}, "a password entry", ["name", "url"], api=mock_api)
    assert result.category == Category.UNCATEGORIZED.value
    mock_api.categorize.assert_not_called()
