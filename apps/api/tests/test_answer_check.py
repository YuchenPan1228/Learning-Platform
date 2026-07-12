import pytest
from app.services.answer_check import answers_match


@pytest.mark.parametrize(
    ("user_answer", "expected_answer"),
    [
        ("15/128", "15/128"),
        ("0.1171875", "15/128"),
        ("1/3", "1/3"),
        ("0.333", "1/3"),
        ("yes", "yes"),
        ("YES", "yes"),
        ("351", "351"),
        ("about 16%", "about 16%"),
        ("16%", "about 16%"),
        ("0.16", "about 16%"),
        ("switch", "switch"),
    ],
)
def test_answers_match_supported_forms(user_answer: str, expected_answer: str) -> None:
    assert answers_match(user_answer, expected_answer)


@pytest.mark.parametrize(
    ("user_answer", "expected_answer"),
    [
        ("1/2", "1/3"),
        ("no", "yes"),
        ("350", "351"),
    ],
)
def test_answers_match_rejects_incorrect_answers(user_answer: str, expected_answer: str) -> None:
    assert not answers_match(user_answer, expected_answer)
