# Zeta

AI-powered tools and utilities.

## Quick Start

```bash
# 1. Clone and bootstrap
git clone <repo-url> ~/dev/zeta && cd ~/dev/zeta
./scripts/bootstrap

# 2. Setup direnv for automatic venv activation
echo "layout uv" > .envrc && direnv allow

# 3. Run tools
inv passwords path/to/passwords.csv --dry-run
inv emails path/to/emails --dry-run
```

> **Tip:** For a complete shell setup with direnv + uv integration, see [RyanLiu6/setup](https://github.com/RyanLiu6/setup).

## Usage

```bash
# Categorize passwords
inv passwords path/to/passwords.csv [--dry-run]

# Categorize emails
inv emails path/to/emails [--output file.json] [--dry-run]

# Set custom model (default: qwen3)
ZETA_MODEL=llama3 inv passwords path/to/passwords.csv

# Testing and linting
inv test
inv lint
inv format
```

## Structure

- `llm/` - Ollama API wrapper
- `modules/passwords/` - Password categorization
- `modules/emails/` - Email categorization
- `docs/` - Documentation
