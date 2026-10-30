import pytest

from app.categorise.rules import categorise_by_rules


@pytest.mark.parametrize(
    ("merchant", "category"),
    [
        ("SWIGGY", "Food Delivery"),
        ("ZOMATO ORDER", "Food Delivery"),
        ("NETFLIX.COM", "Subscriptions"),
        ("spotify premium", "Subscriptions"),
        ("IRCTC RAIL", "Travel"),
        ("UBER INDIA", "Travel"),
        ("OLA CABS", "Travel"),
        ("AMAZON PAY", "Shopping"),
        ("FLIPKART INTERNET", "Shopping"),
        ("LIC PREMIUM", "Insurance"),
        ("HDFC LIFE", "Insurance"),
        ("ELECTRICITY BILL", "Utilities"),
        ("BESCOM PAYMENT", "Utilities"),
        ("MSEB", "Utilities"),
    ],
)
def test_categorise_by_rules_returns_category_and_rule_confidence(merchant, category):
    assert categorise_by_rules(merchant) == (category, 0.95)


def test_categorise_by_rules_returns_uncategorised_without_a_match():
    assert categorise_by_rules("LOCAL MARKET") == ("Uncategorised", 0.0)


def test_categorise_by_rules_does_not_match_partial_keywords():
    assert categorise_by_rules("COLA SHOP") == ("Uncategorised", 0.0)


def test_categorise_by_rules_requires_text():
    with pytest.raises(TypeError, match="merchant must be a string"):
        categorise_by_rules(None)
