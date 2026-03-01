# Zeta

A collection of Python utility scripts, separated by category.
Some leverage local LLMs via [Ollama](https://ollama.ai), some do not.

## Quick Start

```bash
git clone <repo-url> ~/dev/zeta && cd ~/dev/zeta
./scripts/bootstrap
```

## Commands

Run `inv help` to see all available commands.

### PDF Utilities

```bash
# Merge all PDFs in a directory
inv pdf.combine path/to/pdfs/
inv pdf.combine path/to/pdfs/ --output merged.pdf
inv pdf.combine path/to/pdfs/ --dry-run

# Convert images to a single PDF
inv pdf.images path/to/images/
inv pdf.images path/to/images/ --output document.pdf
inv pdf.images path/to/images/ --dry-run
```

### File-System Utilities

```bash
# Delete directories that contain no media files
inv files.clean-empty path/to/media/
inv files.clean-empty path/to/media/ --dry-run

# Walk a directory and display all files with sizes
inv files.explore path/to/dir/
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

### Model Warmup

First run after a while can be slow (~1 min) while the model loads into memory.

```bash
inv warmup
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
pdf/                     PDF manipulation utilities
  combine.py             Merge PDFs in a directory
  images.py              Convert images to a single PDF
files/                   File-system exploration + cleanup
  clean_empty_media.py   Delete dirs without media files
  explore.py             Walk a tree and list file sizes
llm/                     Ollama API wrapper and constants
modules/
  shared/                Category enum, pydantic models, categorization logic, HTML report
  passwords/             Bitwarden suggest + apply commands
  emails/                Email categorization + filter suggestion report
```
