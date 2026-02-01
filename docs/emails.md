# Emails Module

Email categorization and filter suggestion using LLMs.

## Usage

```bash
uv run inv emails path/to/emails/ --dry-run
```

## How It Works

Reads JSON files from a directory (each paired with a `.eml` file), uses the Ollama API to categorize each email based on `subject` and `from_address` into one of:

- **Finance** - banks, investments, bills, credit cards, financial statements
- **Shopping** - e-commerce, orders, shipping notifications, product updates
- **Social** - social networks, messaging platforms, friend notifications
- **Promotions** - marketing emails, deals, sales, promotional offers
- **Newsletters** - subscriptions, digests, regular content updates
- **Updates** - account notifications, alerts, service updates
- **Travel** - flights, hotels, bookings, travel confirmations
- **Work** - professional communications, work-related emails
- **Security** - password resets, 2FA codes, security alerts
- **Uncategorized** - anything that doesn't fit the above

Outputs a JSON file with:
- `categorized_emails`: List of emails with their categories and confidence scores
- `suggested_rules`: Auto-generated filter suggestions based on sender domains and subject patterns
