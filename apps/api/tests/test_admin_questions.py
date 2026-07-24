from unittest.mock import MagicMock

import pytest
from app.models.enums import ContentStatus, Difficulty
from app.models.question import Question
from app.models.topic import Topic
from app.schemas.admin_questions import QuestionUpdate
from app.services.admin_questions import (
    QuestionEditorError,
    delete_question,
    update_question,
)
from fastapi.testclient import TestClient


def _question(*, question_id: int = 1) -> Question:
    topic = Topic(id=10, slug="probability", name="Probability", order_index=0)
    question = Question(
        title="Old title",
        body="Old body",
        difficulty=Difficulty.EASY,
        topic_id=10,
        status=ContentStatus.APPROVED,
        short_answer="1/2",
        canonical_solution="Use Bayes.",
    )
    question.id = question_id
    question.topic = topic
    question.subtopic = None
    question.question_tags = []
    return question


def test_update_question_edits_content_and_refreshes_fingerprints() -> None:
    session = MagicMock()
    question = _question()
    session.scalar.side_effect = [question, question]

    result = update_question(
        session,
        1,
        QuestionUpdate(
            title="New title",
            body="New body about conditional probability",
            short_answer="2/3",
            difficulty=Difficulty.MEDIUM,
        ),
    )

    assert question.title == "New title"
    assert question.body == "New body about conditional probability"
    assert question.short_answer == "2/3"
    assert question.difficulty is Difficulty.MEDIUM
    assert question.raw_text_hash is not None
    assert question.normalized_text_hash is not None
    assert result.title == "New title"
    session.commit.assert_called_once()


def test_update_question_rejects_empty_patch() -> None:
    session = MagicMock()
    session.scalar.return_value = _question()

    with pytest.raises(QuestionEditorError, match="no fields"):
        update_question(session, 1, QuestionUpdate())


def test_delete_question_removes_row() -> None:
    session = MagicMock()
    question = _question(question_id=7)
    session.get.return_value = question

    deleted_id = delete_question(session, 7)
    assert deleted_id == 7
    session.delete.assert_called_once_with(question)
    session.commit.assert_called_once()


@pytest.mark.integration
def test_admin_question_editor_update_and_delete(
    migrated_database: None,
    require_postgres: None,
    client: TestClient,
) -> None:
    from app.db import get_session_factory
    from app.models.attempt import Attempt
    from app.models.question import Question
    from sqlalchemy import select

    session = get_session_factory()()
    try:
        topic = Topic(slug="admin-question-topic", name="Admin Question Topic", order_index=0)
        session.add(topic)
        session.flush()

        question = Question(
            title="Editable question",
            body="What is P(A|B)?",
            difficulty=Difficulty.EASY,
            topic_id=topic.id,
            status=ContentStatus.APPROVED,
            short_answer="depends",
        )
        session.add(question)
        session.flush()

        session.add(
            Attempt(
                question_id=question.id,
                answer="guess",
                time_spent_seconds=5,
            )
        )
        session.commit()
        question_id = question.id
        topic_slug = topic.slug
    finally:
        session.close()

    list_response = client.get(
        "/admin/questions",
        params={"topic_slug": topic_slug, "status": "approved"},
    )
    assert list_response.status_code == 200
    ids = {item["id"] for item in list_response.json()["items"]}
    assert question_id in ids

    patch_response = client.patch(
        f"/admin/questions/{question_id}",
        json={
            "title": "Edited question",
            "body": "Define conditional probability carefully.",
            "difficulty": "hard",
            "canonical_solution": "P(A|B)=P(A and B)/P(B)",
            "common_mistakes": ["Ignoring the given event"],
        },
    )
    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched["title"] == "Edited question"
    assert patched["difficulty"] == "hard"
    assert patched["canonical_solution"] == "P(A|B)=P(A and B)/P(B)"

    delete_response = client.delete(f"/admin/questions/{question_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted_id"] == question_id

    session = get_session_factory()()
    try:
        assert session.get(Question, question_id) is None
        attempts = session.scalars(select(Attempt).where(Attempt.question_id == question_id)).all()
        assert attempts == []
    finally:
        session.close()

    missing = client.get(f"/admin/questions/{question_id}")
    assert missing.status_code == 404
