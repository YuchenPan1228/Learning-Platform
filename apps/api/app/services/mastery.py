from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.concept import Concept
from app.models.constants import LOCAL_USER_ID
from app.models.question import Question
from app.models.topic import Topic
from app.models.user_topic_mastery import UserTopicMastery
from app.schemas.mastery import (
    ConceptMasterySnapshot,
    MasteryRead,
    TopicMasterySnapshot,
)
from app.services.progress import get_topic_progress_stats


def _last_practiced_by_topic_id(session: Session) -> dict[int, datetime]:
    topic_rows = session.execute(
        select(Question.topic_id, func.max(Attempt.created_at))
        .join(Question, Question.id == Attempt.question_id)
        .where(Attempt.user_id == LOCAL_USER_ID)
        .group_by(Question.topic_id),
    ).all()
    subtopic_rows = session.execute(
        select(Question.subtopic_id, func.max(Attempt.created_at))
        .join(Question, Question.id == Attempt.question_id)
        .where(
            Attempt.user_id == LOCAL_USER_ID,
            Question.subtopic_id.is_not(None),
        )
        .group_by(Question.subtopic_id),
    ).all()

    last_practiced: dict[int, datetime] = {}
    for topic_id, practiced_at in topic_rows:
        if topic_id is None or practiced_at is None:
            continue
        last_practiced[int(topic_id)] = practiced_at
    for subtopic_id, practiced_at in subtopic_rows:
        if subtopic_id is None or practiced_at is None:
            continue
        key = int(subtopic_id)
        existing = last_practiced.get(key)
        if existing is None or practiced_at > existing:
            last_practiced[key] = practiced_at
    return last_practiced


def recalculate_user_topic_mastery(session: Session) -> list[UserTopicMastery]:
    """Deterministically recompute and persist topic mastery from attempts."""
    topic_stats = get_topic_progress_stats(session)
    last_practiced = _last_practiced_by_topic_id(session)
    existing_rows = {
        row.topic_id: row
        for row in session.scalars(
            select(UserTopicMastery).where(UserTopicMastery.user_id == LOCAL_USER_ID),
        ).all()
    }

    upserted: list[UserTopicMastery] = []
    for topic_id, stats in topic_stats.items():
        row = existing_rows.get(topic_id)
        if row is None:
            row = UserTopicMastery(
                user_id=LOCAL_USER_ID,
                topic_id=topic_id,
            )
            session.add(row)
        row.mastery_score = stats.mastery_score
        row.attempts_count = stats.attempts_count
        row.last_practiced_at = last_practiced.get(topic_id)
        # next_review_at is owned by spaced repetition (QP-029).
        upserted.append(row)

    stale_ids = set(existing_rows) - set(topic_stats)
    for topic_id in stale_ids:
        session.delete(existing_rows[topic_id])

    session.commit()
    for row in upserted:
        session.refresh(row)
    return upserted


def get_persisted_topic_mastery(session: Session) -> dict[int, UserTopicMastery]:
    rows = session.scalars(
        select(UserTopicMastery).where(UserTopicMastery.user_id == LOCAL_USER_ID),
    ).all()
    return {row.topic_id: row for row in rows}


def get_mastery(session: Session) -> MasteryRead:
    topics = session.scalars(select(Topic).order_by(Topic.order_index, Topic.id)).all()
    topics_by_id = {topic.id: topic for topic in topics}
    persisted = get_persisted_topic_mastery(session)

    topic_mastery: list[TopicMasterySnapshot] = []
    for topic in topics:
        row = persisted.get(topic.id)
        topic_mastery.append(
            TopicMasterySnapshot(
                topic_id=topic.id,
                slug=topic.slug,
                name=topic.name,
                mastery_score=row.mastery_score if row is not None else 0.0,
                attempts_count=row.attempts_count if row is not None else 0,
                last_practiced_at=row.last_practiced_at if row is not None else None,
                next_review_at=row.next_review_at if row is not None else None,
            ),
        )

    concepts = session.scalars(select(Concept).order_by(Concept.id)).all()
    concept_mastery: list[ConceptMasterySnapshot] = []
    for concept in concepts:
        concept_topic = topics_by_id.get(concept.topic_id)
        if concept_topic is None:
            continue
        row = persisted.get(concept.topic_id)
        concept_mastery.append(
            ConceptMasterySnapshot(
                concept_id=concept.id,
                slug=concept.slug,
                name=concept.name,
                topic_id=concept.topic_id,
                topic_slug=concept_topic.slug,
                mastery_score=row.mastery_score if row is not None else 0.0,
                attempts_count=row.attempts_count if row is not None else 0,
                last_practiced_at=row.last_practiced_at if row is not None else None,
            ),
        )

    return MasteryRead(
        user_id=LOCAL_USER_ID,
        topic_mastery=topic_mastery,
        concept_mastery=concept_mastery,
    )
