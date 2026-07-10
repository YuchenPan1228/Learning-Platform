import hashlib
import re
import unicodedata

_WHITESPACE_RE = re.compile(r"\s+")
_PUNCTUATION_RE = re.compile(r"[^\w\s]", re.UNICODE)


def question_canonical_text(title: str, body: str) -> str:
    return f"{title.strip()}\n{body.strip()}"


def normalize_question_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.lower()
    normalized = _WHITESPACE_RE.sub(" ", normalized)
    return normalized.strip()


def aggressively_normalize_question_text(text: str) -> str:
    normalized = normalize_question_text(text)
    normalized = _PUNCTUATION_RE.sub(" ", normalized)
    normalized = _WHITESPACE_RE.sub(" ", normalized)
    return normalized.strip()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
