import re
import unicodedata
from fractions import Fraction

_ABOUT_PREFIX_RE = re.compile(r"^(about|approx\.?|approximately)\s+")
_WHITESPACE_RE = re.compile(r"\s+")
_FRACTION_RE = re.compile(r"^(-?\d+)\s*/\s*(-?\d+)$")
_PERCENT_RE = re.compile(r"^(-?\d+(?:\.\d+)?)\s*%$")

_YES_VALUES = frozenset({"yes", "y", "true"})
_NO_VALUES = frozenset({"no", "n", "false"})


def normalize_answer(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).strip().lower()
    normalized = normalized.replace("'", "")
    normalized = _WHITESPACE_RE.sub(" ", normalized)
    return normalized.strip()


def _parse_fraction(value: str) -> float | None:
    match = _FRACTION_RE.match(value)
    if match is None:
        return None
    numerator = int(match.group(1))
    denominator = int(match.group(2))
    if denominator == 0:
        return None
    return numerator / denominator


def _parse_number(value: str) -> float | None:
    cleaned = value.replace(",", "").strip()
    cleaned = _ABOUT_PREFIX_RE.sub("", cleaned)

    percent_match = _PERCENT_RE.match(cleaned)
    if percent_match is not None:
        return float(percent_match.group(1)) / 100

    fraction_value = _parse_fraction(cleaned)
    if fraction_value is not None:
        return fraction_value

    try:
        return float(Fraction(cleaned))
    except (ValueError, ZeroDivisionError):
        return None


def _is_whole_number(value: float) -> bool:
    return abs(value - round(value)) < 1e-9


def _numbers_match(user_value: float, expected_value: float) -> bool:
    if _is_whole_number(user_value) and _is_whole_number(expected_value):
        return int(round(user_value)) == int(round(expected_value))
    if expected_value == 0:
        return abs(user_value) < 1e-9
    relative_error = abs(user_value - expected_value) / max(abs(expected_value), 1e-9)
    return relative_error <= 0.02


def answers_match(user_answer: str, expected_answer: str) -> bool:
    user_normalized = normalize_answer(user_answer)
    expected_normalized = normalize_answer(expected_answer)

    if user_normalized == expected_normalized:
        return True

    if expected_normalized in _YES_VALUES and user_normalized in _YES_VALUES:
        return True
    if expected_normalized in _NO_VALUES and user_normalized in _NO_VALUES:
        return True

    user_number = _parse_number(user_normalized)
    expected_number = _parse_number(expected_normalized)
    if user_number is not None and expected_number is not None:
        return _numbers_match(user_number, expected_number)

    return False


def self_check_feedback(*, supported: bool, is_correct: bool | None) -> str:
    if not supported:
        return (
            "Deterministic self-check is unavailable for this question. "
            "Reveal the solution to compare your work."
        )
    if is_correct:
        return "Your answer matches the expected result."
    return (
        "Your answer does not match the expected result. Review the solution and common mistakes."
    )


def grade_short_answer(*, short_answer: str | None, user_answer: str) -> tuple[bool, bool | None, str]:
    expected_answer = short_answer
    if expected_answer is None or not expected_answer.strip():
        return False, None, self_check_feedback(supported=False, is_correct=None)

    is_correct = answers_match(user_answer, expected_answer)
    return True, is_correct, self_check_feedback(supported=True, is_correct=is_correct)


def attempt_score(*, supported: bool, is_correct: bool | None) -> float | None:
    if not supported or is_correct is None:
        return None
    return 1.0 if is_correct else 0.0
