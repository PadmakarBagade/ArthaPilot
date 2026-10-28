import re
from dataclasses import dataclass, field


@dataclass
class _TokenState:
    tokens: dict[tuple[str, str], str] = field(default_factory=dict)
    counters: dict[str, int] = field(default_factory=dict)

    def token(self, kind: str, value: str, prefix: str | None = None) -> str:
        key = (kind, value.lower())
        if key not in self.tokens:
            self.counters[kind] = self.counters.get(kind, 0) + 1
            self.tokens[key] = f"{prefix or kind.upper()}_{self.counters[kind]}"
        return self.tokens[key]


def _replace(pattern: str, text: str, state: _TokenState, kind: str, prefix: str) -> str:
    return re.sub(
        pattern,
        lambda match: state.token(kind, match.group(0), prefix),
        text,
        flags=re.IGNORECASE,
    )


def anonymise_text(text: str) -> str:
    """Mask sensitive text using stable PERSON/ACCOUNT/PHONE/UPI_ID/EMAIL tokens."""
    state = _TokenState()
    return _anonymise_text(text, state)


def _anonymise_text(text: str, state: _TokenState) -> str:
    text = _replace(r"\b[\w.+-]+@[\w.-]+\.\w+\b", text, state, "email", "EMAIL")
    text = _replace(
        r"\b(?:UPI[/:_-])?[a-z0-9._-]+@[a-z0-9._-]+\b",
        text,
        state,
        "upi",
        "UPI_ID",
    )
    text = _replace(
        r"\b(?:\+?91[\s-]?)?[6-9]\d{9}\b",
        text,
        state,
        "phone",
        "PHONE",
    )
    text = _replace(
        r"(?<!\d)(?:\d[ ]?){8,}(?!\d)",
        text,
        state,
        "account",
        "ACCOUNT",
    )
    return re.sub(
        r"(?i)(\b(?:name|account holder|customer)\s*[:=-]\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        lambda match: match.group(1)
        + state.token("person", match.group(2), "PERSON"),
        text,
    )


def anonymise_rows(rows: list[dict]) -> list[dict]:
    state = _TokenState()
    result = []
    for row in rows:
        copy = dict(row)
        for key, value in copy.items():
            if value is not None:
                copy[key] = _anonymise_text(str(value), state)
        result.append(copy)
    return result
