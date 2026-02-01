"""Email categorization models and enums."""

from enum import Enum


class EmailCategory(str, Enum):
    FINANCE = "Finance"
    SHOPPING = "Shopping"
    SOCIAL = "Social"
    PROMOTIONS = "Promotions"
    NEWSLETTERS = "Newsletters"
    UPDATES = "Updates"
    TRAVEL = "Travel"
    WORK = "Work"
    SECURITY = "Security"
    UNCATEGORIZED = "Uncategorized"

    @classmethod
    def values(cls) -> list[str]:
        return [category.value for category in cls]

    @classmethod
    def build_system_prompt(cls) -> str:
        categories_list = "\n".join([f"- {cat.value}" for cat in cls])
        return f"""You are an email categorization assistant. Analyze the email \
subject and sender to categorize it into one of these categories:

{categories_list}

Category descriptions:
- Finance: Banks, investments, bills, credit cards, financial statements
- Shopping: E-commerce, orders, shipping notifications, product updates
- Social: Social networks, messaging platforms, friend notifications
- Promotions: Marketing emails, deals, sales, promotional offers
- Newsletters: Subscriptions, digests, regular content updates
- Updates: Account notifications, alerts, service updates
- Travel: Flights, hotels, bookings, travel confirmations
- Work: Professional communications, work-related emails
- Security: Password resets, 2FA codes, security alerts
- Uncategorized: Anything that doesn't fit the above

Respond with JSON in this format:
{{"category": "CategoryName", "confidence": 0.0-1.0}}

Be conservative with confidence scores. Use 0.9+ only when very certain."""
