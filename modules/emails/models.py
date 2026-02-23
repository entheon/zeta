"""Models for the email categorization module."""

from pydantic import BaseModel


class CategorizedEmail(BaseModel):
    """A categorized email record.

    Attributes:
        file: The file stem identifier for the email.
        subject: The email subject line.
        from_address: The sender's email address.
        category: The assigned category string.
        confidence: Confidence score between 0.0 and 1.0.
    """

    file: str
    subject: str
    from_address: str
    category: str
    confidence: float
