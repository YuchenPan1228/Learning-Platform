from app.ai.prompt_hash import compute_prompt_hash


def test_compute_prompt_hash_is_stable_for_dict_payload() -> None:
    first = compute_prompt_hash(
        prompt_template_version="explanation:v1",
        prompt_payload={"question_id": 12, "answer": "1/2"},
    )
    second = compute_prompt_hash(
        prompt_template_version="explanation:v1",
        prompt_payload={"answer": "1/2", "question_id": 12},
    )

    assert first == second
    assert len(first) == 64


def test_compute_prompt_hash_changes_with_template_version() -> None:
    base = compute_prompt_hash(
        prompt_template_version="explanation:v1",
        prompt_payload="Explain Bayes.",
    )
    bumped = compute_prompt_hash(
        prompt_template_version="explanation:v2",
        prompt_payload="Explain Bayes.",
    )

    assert base != bumped


def test_compute_prompt_hash_accepts_string_payload() -> None:
    digest = compute_prompt_hash(
        prompt_template_version="summary:v1",
        prompt_payload="raw prompt text",
    )

    assert len(digest) == 64
