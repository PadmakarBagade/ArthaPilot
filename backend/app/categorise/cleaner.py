import re


_UPI_PREFIX = re.compile(r"\bUPI(?:[/_\-:\s]+)", re.IGNORECASE)
_REFERENCE = re.compile(
    r"\b(?:REF(?:ERENCE)?|TXN|TRANSACTION|UPI)\s*[:/#_\-]?\s*[A-Z0-9]{6,}\b",
    re.IGNORECASE,
)
_ORDER = re.compile(r"\*?\s*(?:ORDER|ORDR)\s*\d+\b", re.IGNORECASE)
_PAID_RECEIVED = re.compile(r"^\s*(?:PAID\s+TO|RECEIVED\s+FROM|SELF\s+TRANSFER\s+TO)\s*[:\-]?\s*", re.IGNORECASE)
_LEADING_STORE = re.compile(r"^\s*\d{1,4}\s+(?=[A-Za-z])")
_SEPARATOR = re.compile(r"[/|]")
_WHITESPACE = re.compile(r"\s+")
_NOISE = re.compile(r"^\d{6,}$")


def clean_merchant(description: str) -> str:
    """Return a stable uppercase merchant token from a transaction description."""
    if not isinstance(description, str):
        raise TypeError("description must be a string")

    cleaned = description.replace("_", " ")
    cleaned = _PAID_RECEIVED.sub("", cleaned)
    cleaned = _UPI_PREFIX.sub("", cleaned)
    cleaned = _REFERENCE.sub("", cleaned)
    cleaned = _ORDER.sub("", cleaned)
    segments = _SEPARATOR.split(cleaned)
    candidates = []
    for segment in segments:
        segment = _LEADING_STORE.sub("", segment)
        segment = _WHITESPACE.sub(" ", segment).strip(" -*:_")
        if segment and not _NOISE.fullmatch(segment):
            candidates.append(segment)
    return (candidates[0] if candidates else "").upper()
