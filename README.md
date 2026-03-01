# Zeta

AI-powered categorization tools using local LLMs via [Ollama](https://ollama.ai).

## Quick Start

```bash
git clone <repo-url> ~/dev/zeta && cd ~/dev/zeta
./scripts/bootstrap
```

## Commands

Run `inv help` to see all available commands.

### Model Warmup

First run after a while can be slow (~1 min) while the model loads into memory.

```bash
inv warmup
```

### Password Categorization

Two-step flow: **suggest** then **apply**.

Reads a [Bitwarden / Vaultwarden unencrypted JSON export](https://bitwarden.com/help/export-your-data/)
and categorizes login entries into folders using a local LLM.
All fields — including passkeys (fido2Credentials), TOTP, notes, etc. — are preserved.

```bash
# 1. Generate suggestions (HTML report + JSON)
inv categorize.passwords path/to/export.json

# 2. Review passwords_report.html, then apply
inv apply.passwords passwords_suggestions.json

# Options
inv categorize.passwords export.json --recategorize  # re-process all entries
inv categorize.passwords export.json --dry-run
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
```

### Development

```bash
inv test              # Run test suite (-v for verbose)
inv lint              # Run ruff + mypy
inv format            # Auto-fix + format
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ZETA_MODEL` | `qwen3:8b` | Ollama model to use |

## Structure

```
llm/                     Ollama API wrapper and constants
modules/
  shared/                Category enum, pydantic models, categorization logic, HTML report
  passwords/             Bitwarden suggest + apply commands
  emails/                Email categorization + filter suggestion report
```
