# Zeta

AI-powered categorization tools using local LLMs via [Ollama](https://ollama.ai).

## Quick Start

```bash
# Clone and bootstrap
git clone <repo-url> ~/dev/zeta && cd ~/dev/zeta
./scripts/bootstrap

# Setup direnv for automatic venv activation
echo "layout uv" > .envrc && direnv allow
```

> **Tip:** For a complete shell setup with direnv + uv integration, see [RyanLiu6/setup](https://github.com/RyanLiu6/setup).

## Commands

Run `inv help` to see all available commands.

### Model Warmup

First run after a while can be slow (~1 min) while the model loads into memory.
Use warmup to pre-load it:

```bash
inv warmup
```

### Password Categorization

Two-step flow: **suggest** then **apply**.

```bash
# 1. Generate suggestions (HTML report + JSON)
inv categorize.passwords path/to/passwords.csv

# 2. Review passwords_report.html, then apply
inv apply.passwords passwords_suggestions.json

# Options
inv categorize.passwords passwords.csv --recategorize  # re-process all entries
inv categorize.passwords passwords.csv --dry-run       # preview without writing
inv apply.passwords suggestions.json --min-confidence 0.6
inv apply.passwords suggestions.json --dry-run
```

### Email Categorization

Categorizes emails and generates an HTML report for building email client filters.

```bash
inv categorize.emails path/to/emails/

# Options
inv categorize.emails emails/ --output results.json
inv categorize.emails emails/ --dry-run
inv categorize.emails emails/ --no-report
```

### Development

```bash
inv test              # Run test suite (-v for verbose)
inv lint              # Run ruff + mypy
inv mypy              # Run mypy only
inv format            # Auto-fix + format
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ZETA_MODEL` | `qwen3:8b` | Ollama model to use |

```bash
ZETA_MODEL=llama3 inv categorize.passwords passwords.csv
```

## Structure

```
llm/                     Ollama API wrapper
modules/
  shared/                Shared Category enum + HTML report generator
  passwords/
    categorize.py        Suggest command (LLM → JSON + HTML report)
    apply.py             Apply command (JSON → categorized CSV)
  emails/
    categorize.py        Categorize + report generation
```
