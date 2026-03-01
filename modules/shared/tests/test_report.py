from pathlib import Path
from typing import Any

import pytest

from modules.shared.models import FilterSuggestion
from modules.shared.report import (
    _build_category_stats,
    _escape_html,
    _extract_domain,
    _get_color,
    _render_category_section,
    _render_distribution_bar,
    _render_rules_section,
    generate_html_report,
)


def test_get_color() -> None:
    assert _get_color("Finance") == "#4ecdc4"


def test_get_color_unknown() -> None:
    assert _get_color("Unknown") == "#94a3b8"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("user@example.com", "example.com"),
        ("https://example.com/path", "example.com"),
        ("http://www.example.com", "example.com"),
        ("", "unknown"),
    ],
)
def test_extract_domain(value: str, expected: str) -> None:
    assert _extract_domain(value) == expected


def test_escape_html() -> None:
    assert _escape_html('<b>"hello"</b>') == "&lt;b&gt;&quot;hello&quot;&lt;/b&gt;"


def test_escape_html_ampersand() -> None:
    assert _escape_html("A & B") == "A &amp; B"


def _make_items(category: str, count: int = 2) -> list[dict[str, Any]]:
    return [
        {
            "category": category,
            "confidence": 0.9,
            "from_address": f"user{i}@example.com",
            "subject": f"Subject {i}",
        }
        for i in range(count)
    ]


def test_build_category_stats() -> None:
    items = _make_items("Finance", 3)
    stats = _build_category_stats(items, "from_address", "subject")
    assert "Finance" in stats
    assert stats["Finance"]["count"] == 3
    assert len(stats["Finance"]["details"]) == 3


def test_build_category_stats_multiple_categories() -> None:
    items = _make_items("Finance", 2) + _make_items("Work", 1)
    stats = _build_category_stats(items, "from_address", "subject")
    assert stats["Finance"]["count"] == 2
    assert stats["Work"]["count"] == 1


def test_render_rules_section_empty() -> None:
    assert _render_rules_section([], "Finance") == ""


def test_render_rules_section_no_match() -> None:
    rules = [
        FilterSuggestion(
            category="Work", from_domain="work.com", count=2, confidence=0.9
        )
    ]
    assert _render_rules_section(rules, "Finance") == ""


def test_render_rules_section_domain() -> None:
    rules = [
        FilterSuggestion(
            category="Finance", from_domain="bank.com", count=3, confidence=0.85
        )
    ]
    html = _render_rules_section(rules, "Finance")
    assert "bank.com" in html
    assert "Suggested Rules" in html


def test_render_rules_section_subject_pattern() -> None:
    rules = [
        FilterSuggestion(
            category="Finance", subject_pattern="invoice", count=4, confidence=0.9
        )
    ]
    html = _render_rules_section(rules, "Finance")
    assert "invoice" in html


def test_render_distribution_bar() -> None:
    stats: dict[str, Any] = {"Finance": {"count": 8}, "Work": {"count": 2}}
    html = _render_distribution_bar(stats, 10)
    assert "distribution-bar" in html
    assert "Finance" in html


def test_render_distribution_bar_skips_small() -> None:
    stats: dict[str, Any] = {"Finance": {"count": 99}, "Work": {"count": 0}}
    html = _render_distribution_bar(stats, 100)
    assert "Work" not in html


def test_render_category_section() -> None:
    data: dict[str, Any] = {
        "count": 5,
        "sources": {"example.com": 3, "other.com": 2},
        "confidences": [0.9, 0.8, 0.85, 0.9, 0.7],
        "details": ["Subject A", "Subject B"],
    }
    html = _render_category_section(
        "Finance", data, 10, "emails", "Domains", "Subjects"
    )
    assert "Finance" in html
    assert "example.com" in html


def test_render_category_section_more_than_20_sources() -> None:
    data: dict[str, Any] = {
        "count": 25,
        "sources": {f"source{i}.com": 1 for i in range(25)},
        "confidences": [0.9] * 25,
        "details": [],
    }
    html = _render_category_section(
        "Finance", data, 100, "emails", "Domains", "Subjects"
    )
    assert "+5 more" in html


def test_render_category_section_with_rules() -> None:
    data: dict[str, Any] = {
        "count": 2,
        "sources": {"bank.com": 2},
        "confidences": [0.9, 0.9],
        "details": ["Statement ready"],
    }
    rules = [
        FilterSuggestion(
            category="Finance", from_domain="bank.com", count=2, confidence=0.9
        )
    ]
    html = _render_category_section(
        "Finance", data, 10, "emails", "Domains", "Subjects", rules
    )
    assert "bank.com" in html
    assert "Suggested Rules" in html


def test_generate_html_report(tmp_path: Path) -> None:
    items = _make_items("Finance", 3) + _make_items("Work", 2)
    output = tmp_path / "report.html"
    generate_html_report(items, output, title="Test Report", item_noun="emails")
    assert output.exists()
    content = output.read_text()
    assert "Test Report" in content
    assert "Finance" in content
    assert "Work" in content


def test_generate_html_report_with_rules(tmp_path: Path) -> None:
    items = _make_items("Finance", 2)
    rules = [
        FilterSuggestion(
            category="Finance", from_domain="example.com", count=2, confidence=0.9
        )
    ]
    output = tmp_path / "report.html"
    generate_html_report(items, output, suggested_rules=rules)
    content = output.read_text()
    assert "example.com" in content
