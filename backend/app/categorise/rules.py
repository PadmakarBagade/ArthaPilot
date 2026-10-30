import re


RULE_CONFIDENCE = 0.95
UNCATEGORISED = "Uncategorised"

MERCHANT_RULES = {
    "MEDICAL": "Health", "MEDICO": "Health", "CHEMIST": "Health",
    "PHARMACY": "Health", "HOSPITAL": "Health", "CLINIC": "Health",
    "PATHOLOGY": "Health", "DOCTOR": "Health",
    "PETROLEUM": "Transport", "FUEL": "Transport", "PETROL": "Transport",
    "SWEETS": "Dining", "HOTEL": "Dining", "CAFE": "Dining", "CHAHA": "Dining",
    "MISAL": "Dining", "WADAPAV": "Dining", "MOMO": "Dining", "RESTAURANT": "Dining",
    "SUPER MARKET": "Groceries", "SUPERMARKET": "Groceries", "KIRANA": "Groceries",
    "DAIRY": "Groceries", "VEGETABLE": "Groceries", "MART": "Groceries", "BAZAAR": "Groceries",
    "ZEPTO": "Groceries",
    "SWIGGY": "Food Delivery",
    "ZOMATO": "Food Delivery",
    "PREPAID": "Utilities", "RECHARGE": "Utilities", "GAS": "Utilities",
    "MSRTC": "Travel", "METRO": "Travel", "RAILWAYS": "Travel",
    "XEROX": "Education", "STATIONERS": "Education", "TAILORING": "Shopping",
    "UNIVERSITY": "Education", "POLYTECHNIC": "Education", "COLLEGE": "Education",
    "SCHOOL FEES": "Education", "SCHOOL": "Education",
    "INSURANCE": "Insurance",
    "NETFLIX": "Subscriptions",
    "SPOTIFY": "Subscriptions",
    "HOTSTAR": "Subscriptions",
    "IRCTC": "Travel",
    "UBER": "Travel",
    "OLA": "Travel",
    "AMAZON": "Shopping",
    "FLIPKART": "Shopping",
    "LIC": "Insurance",
    "HDFC LIFE": "Insurance",
    "ELECTRICITY": "Utilities",
    "BESCOM": "Utilities",
    "MSEB": "Utilities",
    "ELECTRIC": "Utilities", "BESCOM": "Utilities",
    "RENT": "Rent", "EMI": "EMI/Loan", "LOAN": "EMI/Loan",
    "CREDIT CARD": "Credit Card Payment", "SIP": "Investment/SIP",
    "SALARY": "Salary", "PAYROLL": "Salary", "DIVIDEND": "Other Income",
    "CASH WITHDRAWAL": "Cash Withdrawal", "ATM": "Cash Withdrawal",
    "FEE": "Fees and Charges", "CHARGE": "Fees and Charges",
}


def categorise_by_rules(merchant: str) -> tuple[str, float]:
    """Categorise a merchant using the fixed Phase 2 keyword rules."""
    if not isinstance(merchant, str):
        raise TypeError("merchant must be a string")

    normalized = re.sub(r"[_\s]+", " ", merchant.strip().upper())
    for keyword, category in MERCHANT_RULES.items():
        if re.search(rf"\b{re.escape(keyword)}\b", normalized):
            return category, RULE_CONFIDENCE
    return UNCATEGORISED, 0.0
