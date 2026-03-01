import json
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock

import pytest

from modules.emails.categorize import (
    _load_existing_results,
    _save_results,
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


def test_generate_filter_suggestions_subject_pattern() -> None:
    categorized_emails = [
        CategorizedEmail(
            file=f"email{i}",
            subject="invoice ready download",
            from_address=f"billing{i}@different.com",
            category="Finance",
            confidence=0.9,
        )
        for i in range(3)
    ]
    suggestions = generate_filter_suggestions(categorized_emails)
    subject_suggestions = [s for s in suggestions if s.subject_pattern is not None]
    assert len(subject_suggestions) > 0


def test_load_existing_results_missing_file(tmp_path: Path) -> None:
    emails, processed = _load_existing_results(tmp_path / "nonexistent.json")
    assert emails == []
    assert processed == set()


def test_load_existing_results(tmp_path: Path) -> None:
    data = {
        "categorized_emails": [
            {
                "file": "email1",
                "subject": "Test",
                "from_address": "a@b.com",
                "category": "Work",
                "confidence": 0.9,
            }
        ]
    }
    output = tmp_path / "results.json"
    output.write_text(json.dumps(data), encoding="utf-8")
    emails, processed = _load_existing_results(output)
    assert len(emails) == 1
    assert "email1" in processed


def test_load_existing_results_corrupt_file(tmp_path: Path) -> None:
    output = tmp_path / "bad.json"
    output.write_text("not valid json", encoding="utf-8")
    emails, processed = _load_existing_results(output)
    assert emails == []
    assert processed == set()


def test_save_results(tmp_path: Path) -> None:
    emails = [
        CategorizedEmail(
            file="email1",
            subject="Your invoice",
            from_address="billing@shop.com",
            category="Finance",
            confidence=0.9,
        )
    ]
    output = tmp_path / "out.json"
    _save_results(output, emails)
    assert output.exists()
    data = json.loads(output.read_text())
    assert len(data["categorized_emails"]) == 1
