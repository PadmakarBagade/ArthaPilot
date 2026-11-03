from app.copilot import Answer, answer_question, validate_numbers


def test_fallback_answer_has_three_parts():
    answer = answer_question("How healthy are my finances?", health={"total_score": 72, "score_coverage": 0.8}, confidence={"score": 81})
    assert isinstance(answer, Answer)
    assert answer.facts and answer.predictions and answer.recommendations


def test_number_validator_rejects_fabricated_numbers():
    answer = answer_question("How healthy?", health={"total_score": 72, "score_coverage": 0.8}, confidence={"score": 81})
    answer.summary = "Your score is 999."
    assert not validate_numbers(answer, [{"score": 72, "coverage": 0.8, "confidence": 81}])
