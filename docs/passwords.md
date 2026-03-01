# Passwords Module

Categorize password vault entries using local LLMs.

## Input Format

Accepts a **Bitwarden / Vaultwarden unencrypted JSON export** (`.json`).
To export from Bitwarden: *Settings → Export vault → File format: `.json`*.

> **Important:** Use the **unencrypted** JSON format. Encrypted exports are not supported.

All fields are preserved through the categorization pipeline, including:
- Passkeys (`fido2Credentials`)
- TOTP secrets
- Notes, custom fields, password history
- Collection IDs

## Usage

```bash
# Generate suggestions
inv categorize.passwords path/to/export.json

# Preview without writing
inv categorize.passwords export.json --dry-run

# Apply suggestions
inv apply.passwords passwords_suggestions.json
```

## How It Works

Reads the Bitwarden JSON export and extracts `name` and `login.uris` from each
login item. Uses the Ollama API to categorize each entry into one of:

- **Finance** — banking, investments, money management
- **Shopping** — retail, e-commerce, marketplaces
- **Social** — social media, messaging, forums, email
- **Entertainment** — streaming, games, media
- **Work** — business tools, productivity, work email
- **Education** — learning platforms, academic
- **Travel** — airlines, hotels, booking
- **Health** — medical, fitness, wellness
- **No folder** — when no match or insufficient information

The apply step sets each item's `folderId` to the matching folder,
creating new folder entries as needed. Output is a `_categorized.json`
file in the same Bitwarden format, ready for re-import.
