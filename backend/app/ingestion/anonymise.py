import hashlib
import re


def anonymise_text(text: str) -> str:
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w+\b", "[EMAIL]", text)
    text = re.sub(r"\b(?:\+?91[ -]?)?[6-9]\d{9}\b", "[PHONE]", text)
    text = re.sub(r"\b(?:\d[ -]?){8,}\b", "[ACCOUNT]", text)
    return text


def anonymise_rows(rows: list[dict]) -> list[dict]:
    result = []
    for row in rows:
        copy = dict(row)
        for key in ("raw_description", "merchant"):
            if key in copy:
                copy[key] = anonymise_text(str(copy[key]))
        if "user_id" in copy:
            copy["user_id"] = "user-" + hashlib.sha256(
                str(copy["user_id"]).encode()
            ).hexdigest()[:12]
        result.append(copy)
    return result
