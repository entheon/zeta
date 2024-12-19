from enum import Enum
from typing import Set


class Category(str, Enum):
    """Categories for password organization."""

    FINANCE = "Finance"
    SHOPPING = "Shopping"
    SOCIAL = "Social"
    ENTERTAINMENT = "Entertainment"
    WORK = "Work"
    EDUCATION = "Education"
    TRAVEL = "Travel"
    HEALTH = "Health"
    NO_FOLDER = "No folder"

    @classmethod
    def values(cls) -> Set[str]:
        """Get all valid category values."""
        return {item.value for item in cls}

    @classmethod
    def descriptions(cls) -> dict[str, str]:
        """Get category descriptions."""
        return {
            cls.FINANCE.value: "banking, investments, money management",
            cls.SHOPPING.value: "retail, e-commerce, marketplaces",
            cls.SOCIAL.value: "social media, messaging, forums, email",
            cls.ENTERTAINMENT.value: "streaming, games, media",
            cls.WORK.value: "business tools, productivity, work email",
            cls.EDUCATION.value: "learning platforms, academic",
            cls.TRAVEL.value: "airlines, hotels, booking",
            cls.HEALTH.value: "medical, fitness, wellness",
            cls.NO_FOLDER.value: "when no match or insufficient information",
        }

    @classmethod
    def format_for_prompt(cls) -> str:
        """Format categories for use in model prompts."""
        descriptions = cls.descriptions()
        return (
            "\n".join(
                f"- {category} ({descriptions[category]})"
                for category in cls.values()
                if category != cls.NO_FOLDER.value
            )
            + f"\n- {cls.NO_FOLDER.value} ({descriptions[cls.NO_FOLDER.value]})"
        )
