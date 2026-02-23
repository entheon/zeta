"""Email categorization models and enums."""

from enum import Enum


class EmailLabel(str, Enum):
    RECEIPT = "RECEIPT"
    URGENT = "URGENT"
    IMPORTANT = "IMPORTANT"
    STATEMENT = "STATEMENT"

    @classmethod
    def values(cls) -> list[str]:
        return [label.value for label in cls]

    @classmethod
    def descriptions(cls) -> dict[str, str]:
        return {
            cls.RECEIPT.value: (
                "Purchase receipts, payment confirmations, warranties, "
                "subscription proofs"
            ),
            cls.URGENT.value: (
                "Time-sensitive emails requiring immediate attention or response"
            ),
            cls.IMPORTANT.value: (
                "Tax documents, legal contracts, critical records to keep"
            ),
            cls.STATEMENT.value: (
                "Bank statements, credit card statements, financial reports"
            ),
        }


def build_categorization_prompt() -> str:
    """Build the system prompt for email categorization.

    Returns:
        Complete system prompt for hierarchical categorization with labels.
    """
    labels_list = "\n".join(
        f"- {label}: {EmailLabel.descriptions()[label]}"
        for label in EmailLabel.values()
    )

    return f"""You are an email categorization assistant. Analyze the email \
subject and sender to:
1. Determine a logical top-level category (e.g., Finance, Shopping, Travel, \
Work, Personal, etc.)
2. Determine a specific subcategory that describes the email's purpose
3. Assign relevant labels from the predefined list (can be multiple or none)

Examples of category/subcategory:
- Finance -> Bills (utility bills, phone bills)
- Finance -> Housing (rent, mortgage, property management)
- Finance -> Banking (statements, transfers, INTERAC e-Transfer)
- Finance -> Credit Cards (statements, payments)
- Finance -> Investments (brokerage, portfolio updates)
- Shopping -> Orders (order confirmations)
- Shopping -> Shipping (tracking, delivery)
- Shopping -> Returns (refunds, return confirmations)
- Travel -> Bookings (flight, hotel confirmations)
- Travel -> Itineraries (trip details)
- Work -> Internal (company communications)
- Work -> HR (payroll, benefits)

Available labels (use when applicable):
{labels_list}

Respond with JSON in this format:
{{"category": "TopLevelCategory", "subcategory": "SpecificSubcategory", \
"labels": ["LABEL1", "LABEL2"], "confidence": 0.0-1.0}}

Guidelines:
- Be specific with subcategories - they should describe the email's purpose
- Only use labels when they truly apply (labels list can be empty)
- Use "Uncategorized" as category if unsure
- Be conservative with confidence scores (0.9+ only when very certain)"""
