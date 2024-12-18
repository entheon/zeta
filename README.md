# Zeta

A collection of AI-powered tools and utilities.

## Projects

- `ollama/`: Python wrapper for Ollama API
- `passwords/`: AI-powered password categorization tools

## Setup

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

## Development

Format and lint code before committing:
```bash
isort .
black .
flake8
```

## Using direnv (recommended)

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
        }

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

Now whenever you enter the project directory, direnv will:
- Automatically activate the virtual environment
- Create the venv and install dependencies if they don't exist
- Set up any environment variables

## Project Structure
```
.
├── ollama/
│   └── api.py
├── passwords/
│   ├── categorize_passwords.py
│   ├── Modelfile
│   ├── categorize.modelfile
│   └── README.md
├── .flake8
├── .gitignore
├── .envrc
├── pyproject.toml
└── README.md
```
