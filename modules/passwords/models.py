"""Models for the password categorization module."""

from pydantic import BaseModel


class PasswordSuggestion(BaseModel):
    """A suggested folder assignment for a password entry.

    Attributes:
        item_id: Bitwarden item ID.
        name: Display name of the password entry.
        login_uri: First login URI associated with the entry.
        current_folder: Existing folder name, if any.
        suggested_folder: Recommended folder based on categorization.
        confidence: Confidence score between 0.0 and 1.0.
    """

    item_id: str
    name: str
    login_uri: str
    current_folder: str
    suggested_folder: str
    confidence: float
