# Zeta

A collection of AI-powered tools and utilities.

## Structure

- `llm/`: Lightweight Ollama API wrapper
- `modules/`: Task-specific AI-powered utilities
  - `passwords/`: Password categorization using LLMs
- `scripts/`: Utility scripts

## Development Setup

This project uses Python 3.12 and uv for dependency management.

```bash
pip install uv
uv sync
uv run pre-commit install
```

## Usage

Common tasks are managed with invoke:

```bash
uv run inv passwords path/to/passwords.csv --dry-run
uv run inv test
uv run inv lint
uv run inv format
```

## Code Quality

- `ruff`: Formatting, linting, and import sorting
- `mypy`: Static type checking

Pre-commit hooks run automatically on `git commit`. To run manually:

```bash
uv run pre-commit run --all-files
```

## Version Syncing

Dev dependency versions in `pyproject.toml` automatically sync to pre-commit hooks on commit.
