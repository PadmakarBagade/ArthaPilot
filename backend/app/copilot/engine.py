from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field


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
    return set(re.findall(r"(?<![A-Za-z])\d+(?:\.\d+)?", value))


def validate_numbers(answer: Answer, tool_results: list[dict[str, Any]]) -> bool:
    allowed = set()
    for result in tool_results:
        allowed.update(_numbers(str(result)))
    texts = [answer.summary]
    texts.extend(item.text for item in answer.facts)
    texts.extend(item.text for item in answer.predictions)
    texts.extend(item.text for item in answer.recommendations)
    return all(number in allowed for text in texts for number in _numbers(text))


def answer_question(
    question: str,
    *,
    health: dict[str, Any] | None = None,
    confidence: dict[str, Any] | None = None,
    recurring: list[dict[str, Any]] | None = None,
) -> Answer:
    health = health or {}
    confidence = confidence or {}
    recurring = recurring or []
    score = health.get("total_score")
    confidence_score = confidence.get("score", 0)
    if "recurr" in question.lower() or "bill" in question.lower():
        count = len(recurring)
        evidence = [
            str(item.get("id") or txn_id)
            for item in recurring
            for txn_id in (item.get("txn_ids") or [item.get("merchant", "recurring")])
        ]
        return Answer(
            summary=f"You have {count} recurring obligation(s) identified from your transaction history.",
            facts=[Fact(text=f"{count} recurring obligation(s) were detected.", evidence_ids=evidence)],
            predictions=[Prediction(text="Upcoming due dates depend on the detected recurring schedule.", confidence=confidence_score, confidence_reasons=confidence.get("reasons", []))],
            recommendations=[Recommendation(text="Review each upcoming obligation before its next due date.", impact={"formula": "review does not change balances"})],
            follow_ups=["Show the transactions behind these obligations"],
        )
    return Answer(
        summary=f"Your current financial health result is {score if score is not None else 'not available'}.",
        facts=[Fact(text=f"Health score coverage is {health.get('score_coverage', 0):.0%}.", evidence_ids=[])],
        predictions=[Prediction(text=f"Confidence in this analysis is {confidence_score}%.", confidence=confidence_score, confidence_reasons=confidence.get("reasons", []))],
        recommendations=[Recommendation(text="Add more complete account history if confidence is not High.", impact={"formula": "confidence is reduced by data-quality penalties"})],
        follow_ups=["Show my recurring obligations", "Explain my score"],
    )
