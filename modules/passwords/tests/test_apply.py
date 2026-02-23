import csv
import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    csv_path = tmp_path / "passwords.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["name", "login_uri", "folder", "password"]
        )
        writer.writeheader()
        writer.writerows(
            [
                {
                    "name": "My Bank",
                    "login_uri": "https://bank.com",
                    "folder": "",
                    "password": "secret1",
                },
                {
                    "name": "Amazon",
                    "login_uri": "https://amazon.com",
                    "folder": "",
                    "password": "secret2",
                },
                {
                    "name": "Netflix",
                    "login_uri": "https://netflix.com",
                    "folder": "",
                    "password": "secret3",
                },
            ]
        )
    return csv_path


@pytest.fixture
def suggestions_file(tmp_path: Path, sample_csv: Path) -> Path:
    suggestions = {
        "csv_file": str(sample_csv),
        "suggestions": [
            {
                "name": "My Bank",
                "login_uri": "https://bank.com",
                "current_folder": "",
                "suggested_folder": "Finance",
                "confidence": 0.92,
            },
            {
                "name": "Amazon",
                "login_uri": "https://amazon.com",
                "current_folder": "",
                "suggested_folder": "Shopping",
                "confidence": 0.88,
            },
            {
                "name": "Netflix",
                "login_uri": "https://netflix.com",
                "current_folder": "",
                "suggested_folder": "Entertainment",
                "confidence": 0.3,
            },
        ],
    }

    json_path = tmp_path / "suggestions.json"
    with open(json_path, "w") as f:
        json.dump(suggestions, f)
    return json_path


def _read_csv(path: Path) -> list[dict[str, str]]:
    with open(path) as f:
        return list(csv.DictReader(f))


def test_apply(suggestions_file: Path, sample_csv: Path) -> None:
    """Verify apply writes categorized CSV with suggestions above threshold."""
    from click.testing import CliRunner

    from modules.passwords.apply import apply

    runner = CliRunner()
    result = runner.invoke(apply, [str(suggestions_file)])

    assert result.exit_code == 0
    assert "2 entries categorized" in result.output
    assert "1 skipped" in result.output

    output_csv = sample_csv.with_name("passwords_categorized.csv")
    assert output_csv.exists()

    rows = _read_csv(output_csv)
    assert len(rows) == 3
    assert rows[0]["folder"] == "Finance"
    assert rows[1]["folder"] == "Shopping"
    assert rows[2]["folder"] == ""


def test_apply_custom_min_confidence(suggestions_file: Path, sample_csv: Path) -> None:
    """Verify --min-confidence=0.0 applies all suggestions."""
    from click.testing import CliRunner

    from modules.passwords.apply import apply

    runner = CliRunner()
    result = runner.invoke(apply, [str(suggestions_file), "--min-confidence", "0.0"])

    assert result.exit_code == 0
    assert "3 entries categorized" in result.output

    output_csv = sample_csv.with_name("passwords_categorized.csv")
    rows = _read_csv(output_csv)
    assert rows[2]["folder"] == "Entertainment"


def test_apply_dry_run(suggestions_file: Path, sample_csv: Path) -> None:
    from click.testing import CliRunner

    from modules.passwords.apply import apply

    runner = CliRunner()
    result = runner.invoke(apply, [str(suggestions_file), "--dry-run"])

    assert result.exit_code == 0
    assert "My Bank" in result.output
    assert "Finance" in result.output

    output_csv = sample_csv.with_name("passwords_categorized.csv")
    assert not output_csv.exists()


def test_apply_no_csv_in_suggestions(tmp_path: Path) -> None:
    """Verify error when suggestions file has no csv_file and none provided."""
    from click.testing import CliRunner

    from modules.passwords.apply import apply

    json_path = tmp_path / "bad_suggestions.json"
    with open(json_path, "w") as f:
        json.dump({"suggestions": []}, f)

    runner = CliRunner()
    result = runner.invoke(apply, [str(json_path)])

    assert result.exit_code == 0
    assert "No CSV file specified" in result.output
