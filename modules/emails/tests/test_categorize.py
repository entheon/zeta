import json
from unittest.mock import MagicMock

import pytest

from modules.emails.categorize import (
    categorize_email,
    extract_domain,
    generate_filter_suggestions,
)
from modules.emails.models import EmailCategory


@pytest.fixture
def mock_api() -> MagicMock:
    return MagicMock()


def test_categorize_email(mock_api: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.message.content = json.dumps(
        {"category": "Finance", "confidence": 0.9}
    )
    mock_api.chat.return_value = mock_response

    email_data = {
        "subject": "Your bank statement is ready",
        "from_address": "noreply@bank.com",
    }
    result = categorize_email(email_data, api=mock_api)

    assert result["category"] == "Finance"
    assert result["confidence"] == 0.9
    mock_api.chat.assert_called_once()


def test_categorize_email_empty_data(mock_api: MagicMock) -> None:
    email_data = {"subject": "", "from_address": ""}
    result = categorize_email(email_data, api=mock_api)

    assert result["category"] == EmailCategory.UNCATEGORIZED.value
    assert result["confidence"] == 1.0
    mock_api.chat.assert_not_called()


def test_categorize_email_invalid_category(mock_api: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.message.content = json.dumps(
        {"category": "InvalidCategory", "confidence": 0.9}
    )
    mock_api.chat.return_value = mock_response

    email_data = {
        "subject": "Test subject",
        "from_address": "test@example.com",
    }
    result = categorize_email(email_data, api=mock_api)

    assert result["category"] == EmailCategory.UNCATEGORIZED.value
    assert result["confidence"] == 0.0


def test_categorize_email_invalid_json(mock_api: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.message.content = "not valid json"
    mock_api.chat.return_value = mock_response

    email_data = {
        "subject": "Test subject",
        "from_address": "test@example.com",
    }
    result = categorize_email(email_data, api=mock_api)

    assert result["category"] == EmailCategory.UNCATEGORIZED.value
    assert result["confidence"] == 0.0


def test_categorize_email_empty_response(mock_api: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.message.content = ""
    mock_api.chat.return_value = mock_response

    email_data = {
        "subject": "Test subject",
        "from_address": "test@example.com",
    }
    result = categorize_email(email_data, api=mock_api)

    assert result["category"] == EmailCategory.UNCATEGORIZED.value
    assert result["confidence"] == 0.0


def test_categorize_email_api_exception(mock_api: MagicMock) -> None:
    mock_api.chat.side_effect = Exception("Connection failed")

    email_data = {
        "subject": "Test subject",
        "from_address": "test@example.com",
    }
    result = categorize_email(email_data, api=mock_api)

    assert result["category"] == EmailCategory.UNCATEGORIZED.value
    assert result["confidence"] == 0.0


def test_extract_domain() -> None:
    assert extract_domain("user@example.com") == "example.com"
    assert extract_domain("noreply@bank.co.uk") == "bank.co.uk"
    assert extract_domain("invalid-email") is None


def test_generate_filter_suggestions() -> None:
    categorized_emails = [
        {
            "subject": "Your order has shipped",
            "from": "orders@amazon.com",
            "category": "Shopping",
            "confidence": 0.9,
        },
        {
            "subject": "Order confirmation",
            "from": "noreply@amazon.com",
            "category": "Shopping",
            "confidence": 0.85,
        },
        {
            "subject": "Daily newsletter",
            "from": "hello@newsletter.com",
            "category": "Newsletters",
            "confidence": 0.95,
        },
    ]

    suggestions = generate_filter_suggestions(categorized_emails)

    assert len(suggestions) > 0

    domain_suggestions = [s for s in suggestions if "from_domain" in s]
    assert len(domain_suggestions) > 0

    amazon_suggestion = next(
        (s for s in domain_suggestions if s.get("from_domain") == "amazon.com"),
        None,
    )
    assert amazon_suggestion is not None
    assert amazon_suggestion["category"] == "Shopping"
    assert amazon_suggestion["count"] == 2


def test_generate_filter_suggestions_empty() -> None:
    suggestions = generate_filter_suggestions([])
    assert suggestions == []


def test_generate_filter_suggestions_insufficient_data() -> None:
    categorized_emails = [
        {
            "subject": "Single email",
            "from": "single@example.com",
            "category": "Updates",
            "confidence": 0.8,
        }
    ]

    suggestions = generate_filter_suggestions(categorized_emails)
    assert suggestions == []
