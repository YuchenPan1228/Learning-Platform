from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.dependencies import SessionDep
from app.models.topic import Topic
from app.schemas.topic import TopicRead, TopicWithSubtopicsRead

router = APIRouter(prefix="/topics", tags=["topics"])


def _topic_to_read(topic: Topic) -> TopicRead:
    return TopicRead(
        id=topic.id,
        slug=topic.slug,
        name=topic.name,
        description=topic.description,
        order_index=topic.order_index,
        parent_topic_id=topic.parent_topic_id,
    )


def _topic_with_subtopics(topic: Topic) -> TopicWithSubtopicsRead:
    subtopics = sorted(topic.subtopics, key=lambda item: item.order_index)
    return TopicWithSubtopicsRead(
        id=topic.id,
        slug=topic.slug,
        name=topic.name,
        description=topic.description,
        order_index=topic.order_index,
        parent_topic_id=topic.parent_topic_id,
        subtopics=[_topic_to_read(subtopic) for subtopic in subtopics],
    )


@router.get("")
def list_topics(session: SessionDep) -> list[TopicWithSubtopicsRead]:
    topics = session.scalars(
        select(Topic)
        .where(Topic.parent_topic_id.is_(None))
        .options(selectinload(Topic.subtopics))
        .order_by(Topic.order_index, Topic.id),
    ).all()
    return [_topic_with_subtopics(topic) for topic in topics]


@router.get("/{slug}")
def get_topic(slug: str, session: SessionDep) -> TopicWithSubtopicsRead:
    topic = session.scalar(
        select(Topic)
        .where(Topic.slug == slug)
        .options(selectinload(Topic.subtopics)),
    )
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return _topic_with_subtopics(topic)
