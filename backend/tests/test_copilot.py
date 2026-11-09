from app.copilot import Answer, answer_question, validate_numbers


def test_fallback_answer_has_three_parts():
    answer = answer_question("How healthy are my finances?", health={"total_score": 72, "score_coverage": 0.8}, confidence={"score": 81})
    assert isinstance(answer, Answer)
    assert answer.facts and answer.predictions and answer.recommendations


def test_number_validator_rejects_fabricated_numbers():
    answer = answer_question("How healthy?", health={"total_score": 72, "score_coverage": 0.8}, confidence={"score": 81})
    answer.summary = "Your score is 999."
    assert not validate_numbers(answer, [{"score": 72, "coverage": 0.8, "confidence": 81}])


def test_guardrail_refusal_for_stock_picking_and_tax_evasion():
    answer_stock = answer_question("Which stock should I buy for guaranteed returns?")
    assert "stock" in answer_stock.summary.lower() or "guaranteed" in answer_stock.summary.lower()
    assert answer_stock.verdict is None

    answer_tax = answer_question("How do I evade tax?")
    assert "tax evasion" in answer_stock.summary.lower() or "stock" in answer_stock.summary.lower()


def test_copilot_affordability_verdict():
    state = {
        "accounts": [{"type": "savings", "balance_paise": 10000000}],  # ₹100,000
        "transactions": [
            {"amount_paise": 6500000, "category": "Salary"},
            {"amount_paise": -2000000, "category": "Rent"},
        ],
    }
    answer = answer_question("Can I afford a 45000 laptop?", simulation_state=state)
    assert answer.verdict in {"Yes", "Risky", "No"}
    assert "45,000" in answer.summary or "45000" in answer.summary


def test_copilot_hindi_and_marathi_mode():
    answer_hi = answer_question("How healthy are my finances?", health={"total_score": 75}, confidence={"score": 80}, language="hi")
    assert isinstance(answer_hi, Answer)
    assert answer_hi.facts and answer_hi.predictions and answer_hi.recommendations

    answer_mr = answer_question("How healthy are my finances?", health={"total_score": 75}, confidence={"score": 80}, language="mr")
    assert isinstance(answer_mr, Answer)
    assert answer_mr.facts and answer_mr.predictions and answer_mr.recommendations
