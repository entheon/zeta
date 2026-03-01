# Emails Module

Hierarchical email categorization with labels using LLMs.

## Usage

```bash
uv run inv categorize.emails path/to/emails/ --dry-run
```

## How It Works

Reads JSON files from a directory (each paired with a `.eml` file), uses the Ollama API to categorize each email based on `subject` and `from_address`.

### Hierarchical Structure

The LLM determines both a **top-level category** and a **specific subcategory** for each email:

**Example category/subcategory combinations:**
- Finance → Bills, Housing, Banking, Credit Cards, Investments
- Shopping → Orders, Shipping, Returns
- Travel → Bookings, Itineraries
- Work → Internal, External, HR
- And more...

The model dynamically determines appropriate categories based on the email content.

### Folder-Agnostic Labels

In addition to categories, emails can be tagged with labels for quick access:

- **RECEIPT** - Purchase receipts, payment confirmations, warranties, subscription proofs
- **URGENT** - Time-sensitive emails requiring immediate attention or response
- **IMPORTANT** - Tax documents, legal contracts, critical records to keep
- **STATEMENT** - Bank statements, credit card statements, financial reports

### Output Format

Outputs a JSON file with:
- `categorized_emails`: List of emails with:
  - `category`: Top-level folder
  - `subcategory`: Specific subfolder
  - `labels`: List of applicable labels
  - `confidence`: Confidence score (0.0-1.0)
- `suggested_rules`: Auto-generated filter suggestions based on sender domains and subject patterns
