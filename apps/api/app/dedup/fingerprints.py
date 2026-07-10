from app.dedup.text import (
    normalize_question_text,
    question_canonical_text,
    text_hash,
)
from app.models.question import Question

NEAR_DUPLICATE_THRESHOLD = 0.92


def compute_question_fingerprints(title: str, body: str) -> tuple[str, str, str]:
    canonical = question_canonical_text(title, body)
    normalized = normalize_question_text(canonical)
    return (
        text_hash(canonical),
        text_hash(normalized),
        normalized,
    )


def apply_question_fingerprints(question: Question) -> None:
    raw_hash, normalized_hash, normalized_text = compute_question_fingerprints(
        question.title,
        question.body,
    )
    question.raw_text_hash = raw_hash
    question.normalized_text_hash = normalized_hash
    question.normalized_text = normalized_text
