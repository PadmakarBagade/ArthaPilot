import pytest

from app.categorise.cleaner import clean_merchant


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ("UPI/SWIGGY/123456789012", "SWIGGY"),
        ("upi/123456789012/ZOMATO", "ZOMATO"),
        ("AMAZON *ORDER 4482", "AMAZON"),
        ("  netflix  /  REF-ABC123456  ", "NETFLIX"),
        ("salary credit", "SALARY CREDIT"),
    ],
)
def test_clean_merchant_removes_noise_and_extracts_token(description, expected):
    assert clean_merchant(description) == expected


def test_clean_merchant_requires_text():
    with pytest.raises(TypeError, match="description must be a string"):
        clean_merchant(None)
