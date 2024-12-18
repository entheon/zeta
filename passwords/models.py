from enum import Enum
from typing import Set


class Category(str, Enum):
    """Categories for password entries.

    Inherits from str to make it JSON serializable and easier to use in string comparisons.
    """
    FINANCE = "Finance"
    SHOPPING = "Shopping"
    SOCIAL = "Social"
    ENTERTAINMENT = "Entertainment"
    WORK = "Work"
    EDUCATION = "Education"
    TRAVEL = "Travel"
    HEALTH = "Health"
    NO_FOLDER = "No Folder"

    @classmethod
    def values(cls) -> Set[str]:
        """Get all category values as a set."""
        return {category.value for category in cls}

    @classmethod
    def descriptions(cls) -> dict[str, str]:
        """Get category descriptions."""
        return {
            cls.FINANCE.value: "banking, investments, money management",
            cls.SHOPPING.value: "retail, e-commerce, marketplaces",
            cls.SOCIAL.value: "social media, messaging, forums",
            cls.ENTERTAINMENT.value: "streaming, games, media",
            cls.WORK.value: "business tools, productivity",
            cls.EDUCATION.value: "learning platforms, academic",
            cls.TRAVEL.value: "airlines, hotels, booking",
            cls.HEALTH.value: "medical, fitness, wellness",
            cls.NO_FOLDER.value: "when no match or insufficient information"
        }

    @classmethod
    def format_for_prompt(cls) -> str:
        """Format categories for use in model prompts."""
        descriptions = cls.descriptions()
        return "\n".join(
            f"- {category} ({descriptions[category]})"
            for category in cls.values()
            if category != cls.NO_FOLDER.value
        ) + f"\n- {cls.NO_FOLDER.value} ({descriptions[cls.NO_FOLDER.value]})"
