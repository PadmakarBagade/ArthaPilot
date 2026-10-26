from copy import deepcopy

from scripts.generate_personas import generate_rahul
from scripts.scenarios import add_big_purchase, add_emi, raise_expenses, stop_income


def test_scenarios_do_not_mutate_original_data():
    original = generate_rahul(seed=42)
    original_copy = deepcopy(original)

    stopped = stop_income(original, 2)
    with_emi = add_emi(original, 100_000)
    raised = raise_expenses(original, 10)
    purchased = add_big_purchase(original, 500_000, "2024-06-15")

    assert original == original_copy
    assert stopped is not original
    assert with_emi is not original
    assert raised is not original
    assert purchased is not original
    assert len(stopped) == len(original) - 2
    assert len(with_emi) == len(original) + 12
    assert any(row["description"] == "SCENARIO BIG PURCHASE" for row in purchased)


def test_scenarios_apply_expected_changes():
    original = generate_rahul(seed=42)
    stopped = stop_income(original, 2)
    assert sum(row["amount_paise"] > 0 for row in stopped) == 10

    raised = raise_expenses(original, 10)
    original_expense = next(row["amount_paise"] for row in original if row["description"] == "RENT PAYMENT")
    raised_expense = next(row["amount_paise"] for row in raised if row["description"] == "RENT PAYMENT")
    assert raised_expense == -1_980_000
