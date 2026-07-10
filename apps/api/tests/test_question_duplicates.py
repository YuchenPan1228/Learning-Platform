import pytest
from app.config import get_settings
from app.db import get_session_factory, reset_db_state
from app.dedup.fingerprints import compute_question_fingerprints
from app.models.enums import ContentStatus, Difficulty, DuplicateMatchType
from app.models.question import Question
from app.models.topic import Topic
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session


def _create_question(
    session: Session,
    *,
    title: str,
    body: str,
    topic_id: int,
    extraction_method: str,
) -> Question:
    raw_hash, normalized_hash, normalized_text = compute_question_fingerprints(title, body)
    question = Question(
        title=title,
        body=body,
        difficulty=Difficulty.EASY,
        topic_id=topic_id,
        status=ContentStatus.APPROVED,
        extraction_method=extraction_method,
        raw_text_hash=raw_hash,
        normalized_text_hash=normalized_hash,
        normalized_text=normalized_text,
    )
    session.add(question)
    session.commit()
    session.refresh(question)
    return question


@pytest.mark.integration
def test_question_duplicates_detect_exact_and_near_matches(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    session = get_session_factory()()
    try:
        topic = session.scalar(select(Topic).where(Topic.slug == "probability"))
        assert topic is not None

        source = _create_question(
            session,
            title="Expected Value",
            body="What is the expected value of a fair die roll?",
            topic_id=topic.id,
            extraction_method="hand_seed:dedupe-source",
        )
        exact_normalized = _create_question(
            session,
            title="expected value",
            body="what is the expected value of a fair die roll?",
            topic_id=topic.id,
            extraction_method="hand_seed:dedupe-exact-normalized",
        )
        near_normalized = _create_question(
            session,
            title="Expected Value",
            body="What is the expected value of a fair dice roll?",
            topic_id=topic.id,
            extraction_method="hand_seed:dedupe-near-normalized",
        )

        response = client.get(f"/questions/{source.id}/duplicates")
        assert response.status_code == 200
        payload = response.json()
        assert payload["question_id"] == source.id

        matches = {match["question_id"]: match for match in payload["matches"]}
        assert exact_normalized.id in matches
        assert matches[exact_normalized.id]["match_type"] == DuplicateMatchType.EXACT_NORMALIZED

        assert near_normalized.id in matches
        assert matches[near_normalized.id]["match_type"] == DuplicateMatchType.NEAR_NORMALIZED
        assert matches[near_normalized.id]["similarity_score"] is not None
    finally:
        session.close()
        reset_db_state()
        get_settings.cache_clear()


@pytest.mark.integration
def test_seeded_questions_have_duplicate_fingerprints(
    seeded_database: None,
    require_postgres: None,
) -> None:
    session = get_session_factory()()
    try:
        questions = session.scalars(select(Question)).all()
        assert questions
        for question in questions:
            assert question.raw_text_hash is not None
            assert question.normalized_text_hash is not None
            assert question.normalized_text is not None
    finally:
        session.close()


@pytest.mark.integration
def test_get_question_duplicates_returns_404_for_missing_question(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    response = client.get("/questions/999999/duplicates")
    assert response.status_code == 404
