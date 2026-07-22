from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.topic import Topic


class ImportTopicError(ValueError):
    """Raised when import topic metadata is invalid."""


def validate_import_topics(
    session: Session,
    *,
    topic_slug: str,
    subtopic_slug: str | None = None,
) -> None:
    topic = session.scalar(select(Topic).where(Topic.slug == topic_slug))
    if topic is None:
        raise ImportTopicError(f"unknown topic_slug '{topic_slug}'")

    if topic.parent_topic_id is not None:
        raise ImportTopicError("topic_slug must be a top-level topic, not a subtopic")

    if subtopic_slug is None:
        return

    subtopic = session.scalar(select(Topic).where(Topic.slug == subtopic_slug))
    if subtopic is None:
        raise ImportTopicError(f"unknown subtopic_slug '{subtopic_slug}'")
    if subtopic.parent_topic_id != topic.id:
        raise ImportTopicError(
            f"subtopic_slug '{subtopic_slug}' is not a subtopic of '{topic_slug}'",
        )
