from typing import Optional
from unittest.mock import MagicMock

import pytest

from modules.emails.categorize import (
    categorize_email,
    extract_domain,
    generate_filter_suggestions,
)
from modules.emails.models import CategorizedEmail
from modules.shared.models import CategorizeResult, Category


@pytest.fixture
def mock_api() -> MagicMock:
    api = MagicMock()
    api.model = "qwen3:8b"
    return api


def test_categorize_email(mock_api: MagicMock) -> None:
    mock_api.categorize.return_value = CategorizeResult(
        category="Finance",
        confidence=0.9,
    )

    email_data = {
        "subject": "Your bank statement is ready",
        "from_address": "noreply@bank.com",
    }
    result = categorize_email(email_data, api=mock_api)

    assert result.category == "Finance"
    assert result.confidence == 0.9
    mock_api.categorize.assert_called_once()


def test_categorize_email_empty_data(mock_api: MagicMock) -> None:
    email_data = {"subject": "", "from_address": ""}
    result = categorize_email(email_data, api=mock_api)

    assert result.category == Category.UNCATEGORIZED.value
    assert result.confidence == 1.0
    mock_api.categorize.assert_not_called()


def test_categorize_email_uncategorized(mock_api: MagicMock) -> None:
    mock_api.categorize.return_value = CategorizeResult(
        category=Category.UNCATEGORIZED.value,
        confidence=0.0,
    )

    email_data = {
        "subject": "Test subject",
        "from_address": "test@example.com",
    }
    result = categorize_email(email_data, api=mock_api)

    assert result.category == Category.UNCATEGORIZED.value
    assert result.confidence == 0.0


@pytest.mark.parametrize(
    "email,expected",
    [
        ("user@example.com", "example.com"),
        ("noreply@bank.co.uk", "bank.co.uk"),
        ("invalid-email", None),
    ],
)
def test_extract_domain(email: str, expected: Optional[str]) -> None:
    assert extract_domain(email) == expected


def test_generate_filter_suggestions() -> None:
    categorized_emails = [
        CategorizedEmail(
            file="email1",
            subject="Your order has shipped",
            from_address="orders@amazon.com",
            category="Shopping",
            confidence=0.9,
        ),
        CategorizedEmail(
            file="email2",
            subject="Order confirmation",
            from_address="noreply@amazon.com",
            category="Shopping",
            confidence=0.85,
        ),
        CategorizedEmail(
            file="email3",
            subject="Daily newsletter",
            from_address="hello@newsletter.com",
            category="Entertainment",
            confidence=0.95,
        ),
    ]

    suggestions = generate_filter_suggestions(categorized_emails)

    assert len(suggestions) > 0

    domain_suggestions = [s for s in suggestions if s.from_domain is not None]
    assert len(domain_suggestions) > 0

    amazon_suggestion = next(
        (s for s in domain_suggestions if s.from_domain == "amazon.com"),
        None,
    )
    assert amazon_suggestion is not None
    assert amazon_suggestion.category == "Shopping"
    assert amazon_suggestion.count == 2


def test_generate_filter_suggestions_empty() -> None:
    suggestions = generate_filter_suggestions([])
    assert suggestions == []


def test_generate_filter_suggestions_insufficient_data() -> None:
    categorized_emails = [
        CategorizedEmail(
            file="email1",
            subject="Single email",
            from_address="single@example.com",
            category="Work",
            confidence=0.8,
        )
    ]

    suggestions = generate_filter_suggestions(categorized_emails)
    assert suggestions == []
