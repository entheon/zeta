# Passwords Module

Password categorization using LLMs.

## Usage

```bash
uv run inv passwords path/to/passwords.csv --dry-run
```

## How It Works

Reads a CSV file with `name` and `login_uri` columns, uses the Ollama API to categorize each entry into one of:

- **Finance** - banking, investments, money management
- **Shopping** - retail, e-commerce, marketplaces
- **Social** - social media, messaging, forums, email
- **Entertainment** - streaming, games, media
- **Work** - business tools, productivity, work email
- **Education** - learning platforms, academic
- **Travel** - airlines, hotels, booking
- **Health** - medical, fitness, wellness
- **No folder** - when no match or insufficient information

Outputs a new CSV file with a `folder` column added.
