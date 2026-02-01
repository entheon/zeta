from enum import Enum


class Category(str, Enum):
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
    def values(cls) -> set[str]:
        return {item.value for item in cls}

    @classmethod
    def descriptions(cls) -> dict[str, str]:
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
        descriptions = cls.descriptions()
        return (
            "\n".join(
                f"- {category} ({descriptions[category]})"
                for category in cls.values()
                if category != cls.NO_FOLDER.value
            )
            + f"\n- {cls.NO_FOLDER.value} ({descriptions[cls.NO_FOLDER.value]})"
        )

    @classmethod
    def build_system_prompt(cls) -> str:
        """Build the system prompt for password categorization.

        Returns:
            Complete system prompt with all category definitions.
        """
        return f"""
            You are a password categorization assistant.
            Given a URL and name, categorize the login into exactly one category.
            Respond with ONLY valid JSON:
            {{"category": "<category>", "confidence": <0.0-1.0>}}

            Categories:
            {cls.format_for_prompt()}
        """
