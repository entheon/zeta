"""Shared models for categorization modules."""

from enum import Enum


class Category(str, Enum):
    """Shared category enum for all categorization tasks.

    Used by both password and email categorization modules.
    """

    FINANCE = "Finance"
    SHOPPING = "Shopping"
    SOCIAL = "Social"
    ENTERTAINMENT = "Entertainment"
    WORK = "Work"
    EDUCATION = "Education"
    TRAVEL = "Travel"
    HEALTH = "Health"
    UNCATEGORIZED = "Uncategorized"

    @classmethod
    def values(cls) -> list[str]:
        """Return all category values as a flat string list.

        Returns:
            List of category value strings.
        """
        return [item.value for item in cls]

    @classmethod
    def descriptions(cls) -> dict[str, str]:
        """Return category-to-description mapping for prompt generation.

        Returns:
            Dict mapping each category value to a comma-separated
            description of what it covers.
        """
        return {
            cls.FINANCE.value: "banking, investments, bills, statements, credit cards",
            cls.SHOPPING.value: "retail, e-commerce, orders, shipping, returns",
            cls.SOCIAL.value: "social media, messaging, forums, personal email",
            cls.ENTERTAINMENT.value: "streaming, games, media, newsletters",
            cls.WORK.value: "business tools, productivity, HR, payroll",
            cls.EDUCATION.value: "learning platforms, academic, courses",
            cls.TRAVEL.value: "airlines, hotels, booking, itineraries",
            cls.HEALTH.value: "medical, fitness, wellness, pharmacy",
            cls.UNCATEGORIZED.value: "insufficient information or no confident match",
        }

    @classmethod
    def format_for_prompt(cls) -> str:
        """Format categories as a bulleted list for LLM system prompts.

        Each line is formatted as "- Category (description)",
        excluding the UNCATEGORIZED category.

        Returns:
            Multi-line string of formatted category entries.
        """
        descriptions = cls.descriptions()
        return "\n".join(
            f"- {category} ({descriptions[category]})"
            for category in cls.values()
            if category != cls.UNCATEGORIZED.value
        )

    @classmethod
    def build_system_prompt(cls, task: str) -> str:
        """Build the system prompt for a categorization task.

        Args:
            task: Description of what is being categorized, e.g.
                "a password entry (URL and name)" or
                "an email (subject and sender address)".

        Returns:
            Complete system prompt with category definitions.
        """
        return (
            f"You are a categorization assistant.\n"
            f"Given {task}, categorize it into exactly one category.\n"
            f"Respond with ONLY valid JSON:\n"
            f'  {{"category": "<category>", "confidence": <0.0-1.0>}}\n'
            f"\n"
            f"Categories:\n"
            f"{cls.format_for_prompt()}\n"
            f"\n"
            f'Use "{cls.UNCATEGORIZED.value}" only when there is truly '
            f"insufficient information to categorize."
        )
