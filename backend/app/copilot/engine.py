from __future__ import annotations

from datetime import date, timedelta
import re
from typing import Any

from pydantic import BaseModel, Field

from app.simulate.engine import affordability, goal_plan, rank_actions


class Fact(BaseModel):
    text: str
    evidence_ids: list[str] = Field(default_factory=list)


class Prediction(BaseModel):
    text: str
    confidence: int
    confidence_reasons: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    text: str
    impact: dict[str, Any] = Field(default_factory=dict)


class Answer(BaseModel):
    summary: str
    facts: list[Fact]
    predictions: list[Prediction]
    recommendations: list[Recommendation]
    verdict: str | None = None
    follow_ups: list[str] = Field(default_factory=list)


def _numbers(value: str) -> set[str]:
    # Extract digit strings, ignoring commas
    cleaned = value.replace(",", "")
    return set(re.findall(r"(?<![A-Za-z])\d+(?:\.\d+)?", cleaned))


def validate_numbers(answer: Answer, tool_results: list[dict[str, Any]]) -> bool:
    allowed = set()
    for result in tool_results:
        allowed.update(_numbers(str(result)))
    texts = [answer.summary]
    texts.extend(item.text for item in answer.facts)
    texts.extend(item.text for item in answer.predictions)
    texts.extend(item.text for item in answer.recommendations)
    for text in texts:
        for number in _numbers(text):
            # Allow common integers like 0, 1, 2, 3, 30, 90, 100 for counts and percentages
            if number in allowed or number in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "30", "90", "100"}:
                continue
            return False
    return True


def _translate_if_needed(text: str, language: str) -> str:
    """Translates common phrases to Hindi or Marathi while keeping numbers and currencies untouched."""
    if language == "en":
        return text

    translations_hi = {
        "You have": "आपके पास",
        "recurring obligation(s) were detected": "आवर्ती देनदारियां पाई गईं",
        "Your current financial health result is": "आपका वर्तमान वित्तीय स्वास्थ्य स्कोर है",
        "Confidence in this analysis is": "इस विश्लेषण में विश्वास स्कोर है",
        "Health score coverage is": "स्वास्थ्य स्कोर कवरेज है",
        "Affordable": "सस्ती और वहनीय",
        "Risky": "जोखिम भरा",
        "Not affordable": "वहनीय नहीं",
        "Observed Fact": "अवलोकित तथ्य",
        "Prediction": "अनुमान",
        "Recommendation": "सलाह",
        "Guidance, not regulated financial advice": "यह मार्गदर्शन है, वित्तीय सलाह नहीं",
    }
    translations_mr = {
        "You have": "तुमच्याकडे",
        "recurring obligation(s) were detected": "नियमित बिले आढळली आहेत",
        "Your current financial health result is": "तुमचा सध्याचा आर्थिक आरोग्य स्कोअर आहे",
        "Confidence in this analysis is": "या विश्लेषणाचा विश्वासार्हता स्कोअर आहे",
        "Health score coverage is": "आरोग्य स्कोअर कव्हरेज आहे",
        "Affordable": "परवडणारे",
        "Risky": "धोकादायक",
        "Not affordable": "परवडणारे नाही",
        "Observed Fact": "निरीक्षण केलेले तथ्य",
        "Prediction": "अंदाज",
        "Recommendation": "शिफारस",
        "Guidance, not regulated financial advice": "हे केवळ मार्गदर्शन आहे, आर्थिक सल्ला नाही",
    }

    t_map = translations_hi if language == "hi" else translations_mr
    result = text
    for eng, local in t_map.items():
        result = result.replace(eng, local)
    return result


def _check_guardrails(question: str, language: str = "en") -> Answer | None:
    q_lower = question.lower()
    unsafe_patterns = [
        "which stock",
        "buy stock",
        "stock tip",
        "guaranteed return",
        "crypto to buy",
        "evade tax",
        "tax evasion",
        "cheat tax",
    ]
    for pattern in unsafe_patterns:
        if pattern in q_lower:
            summary = "I cannot provide specific stock picking, guaranteed return promises, or tax evasion advice."
            fact = "ArthaPilot provides objective health analytics based on verified transaction records."
            pred = "High-risk speculative investments and irregular filings endanger financial runway."
            rec = "Focus on building a 6-month liquid emergency runway and repaying high-interest debt first."
            return Answer(
                summary=_translate_if_needed(summary, language),
                facts=[Fact(text=_translate_if_needed(fact, language), evidence_ids=["guardrail"])],
                predictions=[Prediction(text=_translate_if_needed(pred, language), confidence=100, confidence_reasons=["Safety policy"])],
                recommendations=[Recommendation(text=_translate_if_needed(rec, language), impact={"action": "build_buffer"})],
                verdict=None,
                follow_ups=["How healthy are my finances?", "What recurring bills do I have?"],
            )
    return None


def answer_question(
    question: str,
    *,
    health: dict[str, Any] | None = None,
    confidence: dict[str, Any] | None = None,
    recurring: list[dict[str, Any]] | None = None,
    simulation_state: dict[str, Any] | None = None,
    gaps: list[dict[str, Any]] | None = None,
    language: str = "en",
) -> Answer:
    health = health or {}
    confidence = confidence or {}
    recurring = recurring or []
    gaps = gaps or []
    simulation_state = simulation_state or {}

    # Check guardrails first
    guardrail_answer = _check_guardrails(question, language)
    if guardrail_answer:
        return guardrail_answer

    q_lower = question.lower()
    score = health.get("total_score")
    confidence_score = confidence.get("score", 0)
    conf_reasons = confidence.get("reasons", [])

    # 1. Affordability question: e.g. "Can I afford 45000", "afford laptop", "afford 50000"
    if "afford" in q_lower:
        match = re.search(r"(?:₹|rs\.?\s*)?(\d[\d,]*)", q_lower.replace(",", ""))
        amount_rs = int(match.group(1)) if match and int(match.group(1)) > 100 else 45000
        amount_paise = amount_rs * 100
        result = affordability(simulation_state, amount_paise)
        verdict = result["verdict"]

        bal_before_rs = result["balance_before_paise"] // 100
        bal_after_rs = result["balance_after_paise"] // 100
        safe_rs = result["safe_threshold_paise"] // 100

        summary = f"Affordability verdict: {verdict}. Purchasing for ₹{amount_rs:,} leaves ₹{bal_after_rs:,} (safe reserve is ₹{safe_rs:,})."
        fact_text = f"Liquid savings before purchase: ₹{bal_before_rs:,}. Safe reserve threshold is ₹{safe_rs:,}."
        pred_text = f"Post-purchase liquid balance will be ₹{bal_after_rs:,}."
        rec_text = result["safer_alternative"] or "You can proceed with this purchase without breaching your safety buffer."

        return Answer(
            summary=_translate_if_needed(summary, language),
            facts=[Fact(text=_translate_if_needed(fact_text, language), evidence_ids=["liquid_accounts"])],
            predictions=[Prediction(text=_translate_if_needed(pred_text, language), confidence=confidence_score, confidence_reasons=conf_reasons)],
            recommendations=[Recommendation(text=_translate_if_needed(rec_text, language), impact={"verdict": verdict, "amount_rs": amount_rs})],
            verdict=verdict,
            follow_ups=["What if I take a 6-month EMI?", "Show my cash-flow forecast"],
        )

    # 2. Cash gap / Shortage question: e.g. "Will I run short?", "cash gap", "deficit"
    if "short" in q_lower or "gap" in q_lower or "deficit" in q_lower or "run out" in q_lower:
        if gaps:
            gap_count = len(gaps)
            first_gap = gaps[0]
            gap_date = str(first_gap.get("date", "upcoming date"))
            dip_rs = abs(int(first_gap.get("expected_balance_paise", 0))) // 100
            summary = f"Cash-flow risk: {gap_count} danger day(s) detected, starting {gap_date}."
            fact_text = f"Forecast detects {gap_count} days falling below the safe operating buffer."
            pred_text = f"Balance likely dips near ₹{dip_rs:,} on {gap_date}."
            rec_text = "Cut non-essential discretionary spending by 20% or delay planned major purchases."
        else:
            summary = "No cash-flow gaps detected in the 90-day forecast."
            fact_text = "All projected balances remain above the safety threshold."
            pred_text = "Cash flow remains positive through your upcoming salary cycle."
            rec_text = "Continue your current savings and expense schedule."

        return Answer(
            summary=_translate_if_needed(summary, language),
            facts=[Fact(text=_translate_if_needed(fact_text, language), evidence_ids=[str(g.get("date", "")) for g in gaps[:3]])],
            predictions=[Prediction(text=_translate_if_needed(pred_text, language), confidence=confidence_score, confidence_reasons=conf_reasons)],
            recommendations=[Recommendation(text=_translate_if_needed(rec_text, language), impact={"gaps_analyzed": len(gaps)})],
            verdict="Risky" if gaps else "Yes",
            follow_ups=["What is my best next move?", "Check laptop affordability"],
        )

    # 3. Best next move / Advice question: e.g. "What should I do first?", "best move", "advice"
    if "first" in q_lower or "best move" in q_lower or "advice" in q_lower or "recommend" in q_lower:
        moves = rank_actions(simulation_state)
        best = moves.get("best_move")
        if best:
            impact_rs = best["impact_paise"] // 100
            reason = best["reason"]
            summary = f"Best Next Move: {reason} (Monthly impact: ₹{impact_rs:,})."
            fact_text = f"Top-ranked action improves monthly surplus by ₹{impact_rs:,} with effort score {best['effort_score']}/10."
            pred_text = f"Implementing this raises surplus and protects your health score."
            rec_text = reason
        else:
            summary = "Your financial profile is currently well balanced."
            fact_text = "No immediate urgent actions required."
            pred_text = "Current trajectory supports long-term wealth growth."
            rec_text = "Consider exploring systematic investment plans (SIPs)."

        return Answer(
            summary=_translate_if_needed(summary, language),
            facts=[Fact(text=_translate_if_needed(fact_text, language), evidence_ids=["simulation_ranking"])],
            predictions=[Prediction(text=_translate_if_needed(pred_text, language), confidence=confidence_score, confidence_reasons=conf_reasons)],
            recommendations=[Recommendation(text=_translate_if_needed(rec_text, language), impact=best or {})],
            verdict=None,
            follow_ups=["Show alternative actions", "How healthy are my finances?"],
        )

    # 4. Recurring bills / Subscriptions: e.g. "What bills do I have?", "recurring"
    if "recurr" in q_lower or "bill" in q_lower or "subscription" in q_lower:
        count = len(recurring)
        total_paise = sum(abs(int(i.get("amount_paise", 0))) for i in recurring)
        total_rs = total_paise // 100
        evidence = [
            str(item.get("id") or txn_id)
            for item in recurring
            for txn_id in (item.get("txn_ids") or [item.get("merchant", "recurring")])
        ]
        summary = f"You have {count} recurring obligation(s) totaling ₹{total_rs:,} per cycle."
        fact_text = f"{count} recurring obligation(s) were detected from your bank statements."
        pred_text = "Upcoming scheduled debits will proceed on their detected regular cycle."
        rec_text = "Review recurring subscriptions to cancel services you no longer actively use."

        return Answer(
            summary=_translate_if_needed(summary, language),
            facts=[Fact(text=_translate_if_needed(fact_text, language), evidence_ids=evidence[:10])],
            predictions=[Prediction(text=_translate_if_needed(pred_text, language), confidence=confidence_score, confidence_reasons=conf_reasons)],
            recommendations=[Recommendation(text=_translate_if_needed(rec_text, language), impact={"recurring_count": count, "total_rs": total_rs})],
            verdict=None,
            follow_ups=["Show the transactions behind these obligations", "Will I run short before salary?"],
        )

    # 5. Confidence question: e.g. "How sure are you?", "confidence"
    if "confiden" in q_lower or "sure" in q_lower or "accurate" in q_lower:
        level = confidence.get("level", "Medium")
        summary = f"Confidence in this analysis is {confidence_score}% ({level})."
        fact_text = f"Evaluated based on {confidence.get('months_of_data', 0)} months of statement data."
        pred_text = f"Accuracy is rated as {level} based on statement completeness."
        rec_text = (
            confidence.get("how_to_improve", ["Upload additional statements"])[0]
            if confidence.get("how_to_improve")
            else "Maintain consistent statement uploads."
        )

        return Answer(
            summary=_translate_if_needed(summary, language),
            facts=[Fact(text=_translate_if_needed(fact_text, language), evidence_ids=["confidence_model"])],
            predictions=[Prediction(text=_translate_if_needed(pred_text, language), confidence=confidence_score, confidence_reasons=conf_reasons)],
            recommendations=[Recommendation(text=_translate_if_needed(rec_text, language), impact={"confidence_level": level})],
            verdict=None,
            follow_ups=["How healthy are my finances?", "What is my best next move?"],
        )

    # 6. Default: Health score & Overview
    summary = f"Your current financial health result is {score if score is not None else 'not available'}."
    fact_text = f"Health score coverage is {health.get('score_coverage', 0):.0%}. Band is {health.get('band', 'Fair')}."
    pred_text = f"Confidence in this analysis is {confidence_score}%."
    rec_text = "Review areas with point deductions such as high DTI or low emergency runway."

    return Answer(
        summary=_translate_if_needed(summary, language),
        facts=[Fact(text=_translate_if_needed(fact_text, language), evidence_ids=["health_score"])],
        predictions=[Prediction(text=_translate_if_needed(pred_text, language), confidence=confidence_score, confidence_reasons=conf_reasons)],
        recommendations=[Recommendation(text=_translate_if_needed(rec_text, language), impact={"score": score})],
        verdict=None,
        follow_ups=["Show my recurring obligations", "Can I afford a ₹45,000 laptop?", "Will I run short before salary?"],
    )
