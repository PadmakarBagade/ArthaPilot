"""Provider-neutral, opt-in LLM categorisation boundary."""

import os
import re
from dataclasses import dataclass

from .rules import UNCATEGORISED


@dataclass(frozen=True)
class LLMResult:
    category: str
    confidence: float
    layer: str = "llm"


class LLMClient:
    def __init__(self, provider: str | None = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "none")
        self.cache: dict[str, LLMResult] = {}
        self.calls = 0

    def categorise(self, cleaned_merchant: str) -> LLMResult:
        if not isinstance(cleaned_merchant, str):
            raise TypeError("cleaned_merchant must be a string")
        if re.search(r"\d|@|[+]", cleaned_merchant):
            raise ValueError("LLM input must be a cleaned merchant without personal data")
        key = cleaned_merchant.strip().upper()
        if key in self.cache:
            return self.cache[key]
        if self.provider == "none":
            result = LLMResult(UNCATEGORISED, 0.0)
        else:
            raise RuntimeError(f"Unsupported LLM provider: {self.provider}")
        self.calls += 1
        self.cache[key] = result
        return result
