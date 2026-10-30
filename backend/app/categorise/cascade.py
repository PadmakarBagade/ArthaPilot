from dataclasses import dataclass
from pathlib import Path

from .cleaner import clean_merchant
from .llm_client import LLMClient
from .model import categorise_by_model
from .rules import UNCATEGORISED, categorise_by_rules


@dataclass(frozen=True)
class Categorisation:
    category: str
    confidence: float
    layer: str
    merchant: str


def categorise(raw_description: str, model_path: str | Path | None = None,
               llm_client: LLMClient | None = None) -> Categorisation:
    merchant = clean_merchant(raw_description)
    category, confidence = categorise_by_rules(merchant)
    if category != UNCATEGORISED:
        return Categorisation(category, confidence, "rules", merchant)
    if model_path is not None:
        category, confidence = categorise_by_model(merchant, model_path)
        if category != UNCATEGORISED:
            return Categorisation(category, confidence, "ml", merchant)
    result = (llm_client or LLMClient()).categorise(merchant)
    if result.category != UNCATEGORISED:
        return Categorisation(result.category, result.confidence, result.layer, merchant)
    return Categorisation(UNCATEGORISED, result.confidence, "uncategorised", merchant)
