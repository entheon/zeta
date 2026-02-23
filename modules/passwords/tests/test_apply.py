import json
from pathlib import Path

import pytest


def _make_bitwarden_json(
    items: list[dict],
    folders: list[dict] | None = None,
) -> dict:
    """Helper to build a minimal Bitwarden JSON export structure."""
    return {
        "encrypted": False,
        "folders": folders or [],
        "items": items,
    }


def _make_item(
    item_id: str,
    name: str,
    uri: str,
    folder_id: str | None = None,
    fido2: list | None = None,
) -> dict:
    """Helper to build a minimal Bitwarden login item."""
    item: dict = {
        "passwordHistory": [],
        "revisionDate": "2025-01-01T00:00:00.000Z",
        "creationDate": "2025-01-01T00:00:00.000Z",
        "id": item_id,
        "type": 1,
        "reprompt": 0,
        "name": name,
        "notes": None,
        "favorite": False,
        "fields": [],
        "login": {
            "uris": [{"uri": uri}] if uri else [],
            "fido2Credentials": fido2 or [],
            "username": "user@example.com",
            "password": "secret",
            "totp": None,
        },
        "collectionIds": None,
    }
    if folder_id is not None:
        item["folderId"] = folder_id
    return item


@pytest.fixture
def sample_bitwarden_json(tmp_path: Path) -> Path:
    folders = [
        {"id": "folder-finance", "name": "Finance"},
    ]
    items = [
        _make_item("id-1", "My Bank", "https://bank.com"),
        _make_item("id-2", "Amazon", "https://amazon.com"),
        _make_item(
            "id-3",
            "Netflix",
            "https://netflix.com",
            fido2=[{"credentialId": "passkey-123", "keyType": "public-key"}],
        ),
    ]
    bw_data = _make_bitwarden_json(items, folders)
    json_path = tmp_path / "passwords.json"
    json_path.write_text(json.dumps(bw_data, indent=2), encoding="utf-8")
    return json_path


@pytest.fixture
def suggestions_file(tmp_path: Path, sample_bitwarden_json: Path) -> Path:
    suggestions = {
        "json_file": str(sample_bitwarden_json),
        "suggestions": [
            {
                "item_id": "id-1",
                "name": "My Bank",
                "login_uri": "https://bank.com",
                "current_folder": "",
                "suggested_folder": "Finance",
                "confidence": 0.92,
            },
            {
                "item_id": "id-2",
                "name": "Amazon",
                "login_uri": "https://amazon.com",
                "current_folder": "",
                "suggested_folder": "Shopping",
                "confidence": 0.88,
            },
            {
                "item_id": "id-3",
                "name": "Netflix",
                "login_uri": "https://netflix.com",
                "current_folder": "",
                "suggested_folder": "Entertainment",
                "confidence": 0.3,
            },
        ],
    }

    json_path = tmp_path / "suggestions.json"
    json_path.write_text(json.dumps(suggestions, indent=2), encoding="utf-8")
    return json_path


def test_apply(suggestions_file: Path, sample_bitwarden_json: Path) -> None:
    """Verify apply writes categorized JSON with suggestions above threshold."""
    from click.testing import CliRunner

    from modules.passwords.apply import apply

    runner = CliRunner()
    result = runner.invoke(apply, [str(suggestions_file)])

    assert result.exit_code == 0
    assert "2 entries categorized" in result.output
    assert "1 skipped" in result.output

    output_json = sample_bitwarden_json.with_name("passwords_categorized.json")
    assert output_json.exists()

    data = json.loads(output_json.read_text(encoding="utf-8"))
    items = data["items"]
    folders = {f["id"]: f["name"] for f in data["folders"]}

    assert len(items) == 3

    # Item 1: Finance (existing folder)
    assert items[0].get("folderId") is not None
    assert folders[items[0]["folderId"]] == "Finance"

    # Item 2: Shopping (new folder created)
    assert items[1].get("folderId") is not None
    assert folders[items[1]["folderId"]] == "Shopping"

    # Item 3: below threshold, no folder assigned
    assert items[2].get("folderId") is None


def test_apply_preserves_passkeys(
    suggestions_file: Path, sample_bitwarden_json: Path
) -> None:
    """Verify fido2Credentials are preserved through categorization."""
    from click.testing import CliRunner

    from modules.passwords.apply import apply

    runner = CliRunner()
    result = runner.invoke(apply, [str(suggestions_file), "--min-confidence", "0.0"])

    assert result.exit_code == 0

    output_json = sample_bitwarden_json.with_name("passwords_categorized.json")
    data = json.loads(output_json.read_text(encoding="utf-8"))

    netflix_item = data["items"][2]
    assert len(netflix_item["login"]["fido2Credentials"]) == 1
    assert netflix_item["login"]["fido2Credentials"][0]["credentialId"] == "passkey-123"


def test_apply_custom_min_confidence(
    suggestions_file: Path, sample_bitwarden_json: Path
) -> None:
    """Verify --min-confidence=0.0 applies all suggestions."""
    from click.testing import CliRunner

    from modules.passwords.apply import apply

    runner = CliRunner()
    result = runner.invoke(apply, [str(suggestions_file), "--min-confidence", "0.0"])

    assert result.exit_code == 0
    assert "3 entries categorized" in result.output

    output_json = sample_bitwarden_json.with_name("passwords_categorized.json")
    data = json.loads(output_json.read_text(encoding="utf-8"))
    folders = {f["id"]: f["name"] for f in data["folders"]}

    assert folders[data["items"][2]["folderId"]] == "Entertainment"


def test_apply_dry_run(suggestions_file: Path, sample_bitwarden_json: Path) -> None:
    from click.testing import CliRunner

    from modules.passwords.apply import apply

    runner = CliRunner()
    result = runner.invoke(apply, [str(suggestions_file), "--dry-run"])

    assert result.exit_code == 0
    assert "My Bank" in result.output
    assert "Finance" in result.output

    output_json = sample_bitwarden_json.with_name("passwords_categorized.json")
    assert not output_json.exists()


def test_apply_no_json_in_suggestions(tmp_path: Path) -> None:
    """Verify error when suggestions file has no json_file and none provided."""
    from click.testing import CliRunner

    from modules.passwords.apply import apply

    json_path = tmp_path / "bad_suggestions.json"
    json_path.write_text(json.dumps({"suggestions": []}), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(apply, [str(json_path)])

    assert result.exit_code == 0
    assert "No JSON file specified" in result.output
