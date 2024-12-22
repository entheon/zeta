# Zeta

A collection of AI-powered tools and utilities.

## Projects

- `ollama/`: Python wrapper for Ollama API
- `passwords/`: AI-powered password categorization tools

## Development Setup

1. Install uv:
    ```bash
    pip install uv
    ```

2. Create and activate virtual environment:
    ```bash
    uv venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    uv pip install -e ".[dev]"
    ```

4. Set up pre-commit hooks:
    ```bash
    pip install pre-commit
    pre-commit install
    ```

### Code Quality Tools

This project uses several tools to ensure code quality:

- `ruff`: Code formatting, linting, and import sorting
- `mypy`: Static type checking

You can run these manually:
```bash
ruff check .
ruff format .
mypy .
```

Or let pre-commit run them automatically on `git commit`. If any check fails:
1. The commit will be aborted
2. The tools will make the necessary changes (if possible)
3. Stage the changes (`git add`) and try the commit again

To run all checks manually:
```bash
pre-commit run --all-files
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
├── src/
│   └── __init__.py
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
└── README.md
```

### Configuration Files
- `pyproject.toml`: Project metadata, dependencies, and tool settings (ruff, mypy)
- `.pre-commit-config.yaml`: Pre-commit hook configurations

### Version Syncing

The project includes automatic version syncing between dev dependencies in `pyproject.toml` and pre-commit hooks in `.pre-commit-config.yaml`. When you update a version in `pyproject.toml`, the corresponding pre-commit hook will be updated automatically on the next commit.

For example, if you update the ruff version in `pyproject.toml`:
```toml
dev = [
    "ruff>=0.3.1",  # Update this version
    # ...
]
```

The pre-commit hook will be automatically updated to match:
```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.3.1  # This will be updated automatically
```

This ensures that the versions stay in sync and prevents version mismatch issues.

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

3. Create a layout file for python-venv:
    ```bash
    # Create the direnv layouts directory
    mkdir -p ~/.config/direnv/lib

    # Create the layout file
    cat > ~/.config/direnv/lib/python-venv.sh << 'EOF'
    layout_python-venv() {
        if ! has uv; then
            log_error "uv not found. Please install uv first."
            return 1
        fi

        local venv=.venv
        if [[ ! -d $venv ]]; then
            log_status "creating python venv"
            uv venv
            log_status "installing dependencies"
            uv pip install -e ".[dev]"
        fi

        source $venv/bin/activate
    }
    EOF
    ```

4. Create .envrc file:
    ```bash
    echo 'layout python-venv' > .envrc
    direnv allow
    ```
