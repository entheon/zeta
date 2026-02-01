#!/usr/bin/env python3

import re
from pathlib import Path
from typing import Any, cast

import tomli
import tomli_w
import yaml


def read_pyproject(path: Path) -> dict[str, Any]:
    return tomli.loads(path.read_text())


def write_pyproject(path: Path, data: dict[str, Any]) -> None:
    path.write_text(tomli_w.dumps(data))


def load_yaml(file_path: Path) -> dict[str, Any]:
    with open(file_path) as f:
        return cast(dict[str, Any], yaml.safe_load(f))


def write_precommit(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def get_dev_dependency_version(pyproject: dict[str, Any], package: str) -> str:
    if "dependency-groups" in pyproject:
        dev_deps = pyproject["dependency-groups"]["dev"]
    else:
        dev_deps = pyproject["project"]["optional-dependencies"]["dev"]

    for dep in dev_deps:
        if dep.startswith(package):
            match = re.match(rf"{package}>=(\d+\.\d+\.\d+)", dep)
            if match:
                return match.group(1)
    raise ValueError(f"Package {package} not found in dev dependencies")


def update_precommit_rev(
    precommit: dict[str, Any], repo_url: str, version: str
) -> None:
    for repo in precommit["repos"]:
        if repo["repo"] == repo_url:
            repo["rev"] = f"v{version}"


def main() -> None:
    root = Path(__file__).parent.parent
    pyproject_path = root / "pyproject.toml"
    precommit_path = root / ".pre-commit-config.yaml"

    pyproject = read_pyproject(pyproject_path)
    precommit = load_yaml(precommit_path)

    # Map of pre-commit repo URLs to their package names in pyproject.toml
    PACKAGE_MAP = {
        "https://github.com/astral-sh/ruff-pre-commit": "ruff",
        "https://github.com/pre-commit/mirrors-mypy": "mypy",
    }

    # Update pre-commit revisions based on dev dependencies
    for repo_url, package in PACKAGE_MAP.items():
        try:
            version = get_dev_dependency_version(pyproject, package)
            update_precommit_rev(precommit, repo_url, version)
        except ValueError as e:
            print(f"Warning: {e}")

    write_precommit(precommit_path, precommit)
    print("Successfully synced versions!")


if __name__ == "__main__":
    main()
