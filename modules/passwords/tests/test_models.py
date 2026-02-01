from modules.passwords.models import Category


def test_values():
    values = Category.values()

    assert isinstance(values, set)
    assert "Finance" in values
    assert "Shopping" in values
    assert "No folder" in values
    assert len(values) == 9


def test_descriptions():
    descriptions = Category.descriptions()

    assert isinstance(descriptions, dict)
    assert "Finance" in descriptions
    assert "banking" in descriptions["Finance"]
    assert len(descriptions) == 9


def test_format_for_prompt():
    prompt = Category.format_for_prompt()

    assert isinstance(prompt, str)
    assert "Finance" in prompt
    assert "banking" in prompt
    assert "No folder" in prompt


def test_category_enum_values():
    assert Category.FINANCE.value == "Finance"
    assert Category.SHOPPING.value == "Shopping"
    assert Category.SOCIAL.value == "Social"
    assert Category.ENTERTAINMENT.value == "Entertainment"
    assert Category.WORK.value == "Work"
    assert Category.EDUCATION.value == "Education"
    assert Category.TRAVEL.value == "Travel"
    assert Category.HEALTH.value == "Health"
    assert Category.NO_FOLDER.value == "No folder"


def test_category_is_str():
    assert isinstance(Category.FINANCE, str)
    assert Category.FINANCE == "Finance"
