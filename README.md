# Zeta

A collection of AI-powered tools and utilities.

## Structure

- `llm/`: Lightweight Ollama API wrapper
- `modules/`: Task-specific AI-powered utilities
  - `passwords/`: Password categorization using LLMs
  - `emails/`: Email categorization (planned)
- `tasks.py`: Invoke tasks for common operations

## Development Setup

This project uses Python 3.12 and uv for dependency management.

1. Install uv:
    ```bash
    pip install uv
    ```

2. Install dependencies (creates venv automatically):
    ```bash
    uv sync
    ```

3. Set up pre-commit hooks:
    ```bash
    uv run pre-commit install
    ```

## Usage

Common tasks are managed with invoke. You can use either the bootstrap script or uv directly:

```bash
# Using bootstrap script (recommended)
./inv passwords path/to/passwords.csv --dry-run
./inv test
./inv lint
./inv format

# Or using uv directly
uv run inv passwords path/to/passwords.csv --dry-run
uv run inv test
uv run inv lint
uv run inv format
```

### Code Quality Tools

This project uses several tools to ensure code quality:

- `ruff`: Code formatting, linting, and import sorting
- `mypy`: Static type checking

You can run these manually:
```bash
./inv lint
./inv format
```

Or let pre-commit run them automatically on `git commit`. If any check fails:
1. The commit will be aborted
2. The tools will make the necessary changes (if possible)
3. Stage the changes (`git add`) and try the commit again

To run all checks manually:
```bash
uv run pre-commit run --all-files
```

> [!IMPORTANT]
> When using third-party packages, you'll need to add their type stubs to the mypy pre-commit hook. For example:
> ```yaml
> - repo: https://github.com/pre-commit/mirrors-mypy
>   hooks:
>     - id: mypy
>       additional_dependencies:
>         - types-requests  # for requests
>         - types-PyYAML   # for pyyaml
> ```

### Project Structure
```
.
├── llm/                    # Ollama API wrapper
│   ├── __init__.py
│   └── api.py
├── modules/                # Task-specific modules
│   ├── passwords/          # Password categorization
│   │   ├── categorize.py
│   │   └── models.py
│   └── emails/             # Email categorization (planned)
├── scripts/                # Utility scripts
│   └── sync_versions.py
├── tasks.py                # Invoke tasks
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── pyproject.toml
└── README.md
```

### Configuration Files
- `pyproject.toml`: Project metadata, dependencies (using [dependency-groups]), and tool settings
- `.pre-commit-config.yaml`: Pre-commit hook configurations
- `.python-version`: Python version (3.12)
- `uv.lock`: Dependency lock file

### Version Syncing

The project includes automatic version syncing between dev dependencies in `pyproject.toml` and pre-commit hooks. When you update a version in `pyproject.toml`, the corresponding pre-commit hook will be updated automatically on the next commit.

For example, if you update the ruff version:
```toml
[dependency-groups]
dev = [
    "ruff>=0.9.0",  # Update this version
    # ...
]
```

The pre-commit hook will be automatically updated to match:
```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.9.0  # This will be updated automatically
```

## Using direnv (optional)

direnv automatically activates your virtual environment when entering the project directory.

1. Install direnv:
    ```bash
    # macOS
    brew install direnv

    # Ubuntu/Debian
    sudo apt install direnv
    ```

2. Add to your shell's rc file (.bashrc, .zshrc, etc.):
    ```bash
    eval "$(direnv hook bash)"  # for bash
    eval "$(direnv hook zsh)"   # for zsh
    ```

3. Create .envrc file:
    ```bash
    echo 'source .venv/bin/activate' > .envrc
    direnv allow
    ```

The venv will be created automatically by `uv sync`.
