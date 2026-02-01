from textwrap import dedent

import pytest

from scripts.sync_versions import (
    get_dev_dependency_version,
    load_yaml,
    read_pyproject,
    update_precommit_rev,
)


@pytest.fixture
def sample_pyproject(tmp_path):
    content = dedent("""
        [project]
        name = "test"

        [dependency-groups]
        dev = [
            "ruff>=0.9.0",
            "mypy>=1.14.0",
            "pytest>=8.0.0",
        ]
    """).strip()
    path = tmp_path / "pyproject.toml"
    path.write_text(content)
    return path


@pytest.fixture
def sample_precommit(tmp_path):
    content = dedent("""
        repos:
          - repo: https://github.com/astral-sh/ruff-pre-commit
            rev: v0.8.0
            hooks:
              - id: ruff
          - repo: https://github.com/pre-commit/mirrors-mypy
            rev: v1.13.0
            hooks:
              - id: mypy
    """).strip()
    path = tmp_path / ".pre-commit-config.yaml"
    path.write_text(content)
    return path


def test_read_pyproject(sample_pyproject):
    result = read_pyproject(sample_pyproject)

    assert result["project"]["name"] == "test"
    assert "dependency-groups" in result


def test_load_yaml(sample_precommit):
    result = load_yaml(sample_precommit)

    assert "repos" in result
    assert len(result["repos"]) == 2


def test_get_dev_dependency_version(sample_pyproject):
    pyproject = read_pyproject(sample_pyproject)

    assert get_dev_dependency_version(pyproject, "ruff") == "0.9.0"
    assert get_dev_dependency_version(pyproject, "mypy") == "1.14.0"
    assert get_dev_dependency_version(pyproject, "pytest") == "8.0.0"


def test_get_dev_dependency_version_not_found(sample_pyproject):
    pyproject = read_pyproject(sample_pyproject)

    with pytest.raises(ValueError, match="Package unknown not found"):
        get_dev_dependency_version(pyproject, "unknown")


def test_update_precommit_rev(sample_precommit):
    precommit = load_yaml(sample_precommit)

    update_precommit_rev(
        precommit, "https://github.com/astral-sh/ruff-pre-commit", "0.9.0"
    )

    ruff_repo = next(
        r for r in precommit["repos"]
        if r["repo"] == "https://github.com/astral-sh/ruff-pre-commit"
    )
    assert ruff_repo["rev"] == "v0.9.0"


def test_update_precommit_rev_unknown_repo(sample_precommit):
    precommit = load_yaml(sample_precommit)
    original_repos = [r.copy() for r in precommit["repos"]]

    update_precommit_rev(precommit, "https://github.com/unknown/repo", "1.0.0")

    for i, repo in enumerate(precommit["repos"]):
        assert repo["rev"] == original_repos[i]["rev"]
