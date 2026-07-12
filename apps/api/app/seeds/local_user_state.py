from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.constants import LOCAL_USER_ID
from app.models.topic import Topic
from app.models.user_topic_mastery import UserTopicMastery
from app.seeds.data.local_user_state import SUBTOPIC_MASTERY_SCORES, TOPIC_MASTERY_SCORES


@dataclass(frozen=True, slots=True)
class LocalUserStateSummary:
    mastery_rows: int


def _upsert_topic_mastery(
    session: Session,
    *,
    topic: Topic,
    mastery_score: float,
) -> None:
    mastery = session.scalar(
        select(UserTopicMastery).where(
            UserTopicMastery.user_id == LOCAL_USER_ID,
            UserTopicMastery.topic_id == topic.id,
        )
    )
    if mastery is None:
        session.add(
            UserTopicMastery(
                user_id=LOCAL_USER_ID,
                topic_id=topic.id,
                mastery_score=mastery_score,
            )
        )
    else:
        mastery.mastery_score = mastery_score


def seed_local_user_state(session: Session) -> LocalUserStateSummary:
    topics = session.scalars(select(Topic)).all()
    topics_by_slug = {topic.slug: topic for topic in topics}
    seeded = 0

    for slug, score in TOPIC_MASTERY_SCORES.items():
        topic = topics_by_slug.get(slug)
        if topic is None:
            continue
        _upsert_topic_mastery(session, topic=topic, mastery_score=score)
        seeded += 1

    for slug, score in SUBTOPIC_MASTERY_SCORES.items():
        topic = topics_by_slug.get(slug)
        if topic is None:
            continue
        _upsert_topic_mastery(session, topic=topic, mastery_score=score)
        seeded += 1

    session.commit()
    return LocalUserStateSummary(mastery_rows=seeded)
