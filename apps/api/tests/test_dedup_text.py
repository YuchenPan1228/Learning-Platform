from app.dedup.fingerprints import compute_question_fingerprints
from app.dedup.text import normalize_question_text, question_canonical_text, text_hash


def test_normalize_question_text_collapses_whitespace_and_case() -> None:
    assert normalize_question_text("  Hello   WORLD  ") == "hello world"


def test_same_normalized_text_produces_same_hash() -> None:
    first = compute_question_fingerprints("Coin Flip", "What is P(heads)?")
    second = compute_question_fingerprints("coin flip", "what is p(heads)?")

    assert first[0] != second[0]
    assert first[1] == second[1]
    assert first[2] == second[2]


def test_question_canonical_text_joins_title_and_body() -> None:
    assert question_canonical_text("Title", "Body") == "Title\nBody"


def test_text_hash_is_stable_sha256_hex() -> None:
    digest = text_hash("example")
    assert len(digest) == 64
    assert digest == text_hash("example")
