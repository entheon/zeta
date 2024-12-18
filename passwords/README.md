# Password Categorizer

An AI-powered tool that helps categorize and organize login credentials by identifying the service or website they belong to.

## Features

- Uses Ollama's local LLM to categorize login credentials
- Handles various login formats and patterns
- Privacy-focused: all processing done locally
- Custom-trained model for credential classification
- Type-safe category handling using Python Enums

## Categories

The tool categorizes passwords into the following categories:
- Finance (banking, investments, money management)
- Shopping (retail, e-commerce, marketplaces)
- Social (social media, messaging, forums)
- Entertainment (streaming, games, media)
- Work (business tools, productivity)
- Education (learning platforms, academic)
- Travel (airlines, hotels, booking)
- Health (medical, fitness, wellness)
- No Folder (when no match or insufficient information)

## Usage

### Python API

```python
from passwords.categorize_passwords import categorize_password
from ollama.api import OllamaAPI

# Create API instance (reusable)
api = OllamaAPI()

# Example login data
login = {
    "login_uri": "https://github.com",
    "name": "Work Repository"
}

# Categorize the login
category = categorize_password(login, api=api)
print(f"This login belongs to: {category}")
```

### Command Line Interface

```bash
# Show help
python -m passwords.categorize_passwords --help

# Dry run to preview categorization
python -m passwords.categorize_passwords input.csv --dry-run

# Process and write categorized CSV
python -m passwords.categorize_passwords input.csv
```

## Model Training

The model is trained using a custom Modelfile that specializes in identifying services from login information. To build the model:

```bash
# From the passwords directory
ollama create login-classifier -f Modelfile
```

## Privacy & Security

- All processing is done locally using Ollama
- No credentials are sent to external services
- The model is trained to identify services without storing sensitive information
- Input data integrity is verified before writing any changes

## Requirements

- Python 3.8+
- ollama Python package
- Local Ollama instance running
- Custom login-classifier model (built from provided Modelfile)
- click (for CLI functionality)

## Input CSV Format

The tool expects a CSV file with at least these columns:
- `login_uri`: The URL or domain of the login
- `name`: Name or description of the login
- Additional columns are preserved in the output

The categorized output will be written to a new file with `_categorized` appended to the original filename.
