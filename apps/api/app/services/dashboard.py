from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.concept import ConceptEdge
from app.models.constants import LOCAL_USER_ID
from app.models.enums import ConceptEdgeRelationshipType
from app.models.topic import Topic
from app.models.user_topic_mastery import UserTopicMastery
from app.schemas.dashboard import DashboardRead, TopicMasteryRead, WeakPrerequisiteRead

WEAK_MASTERY_THRESHOLD = 50.0


def _mastery_by_topic_id(session: Session) -> dict[int, UserTopicMastery]:
    rows = session.scalars(
        select(UserTopicMastery).where(UserTopicMastery.user_id == LOCAL_USER_ID),
    ).all()
    return {row.topic_id: row for row in rows}


def _topic_mastery_cards(
    session: Session,
    mastery_by_topic_id: dict[int, UserTopicMastery],
) -> list[TopicMasteryRead]:
    root_topics = session.scalars(
        select(Topic).where(Topic.parent_topic_id.is_(None)).order_by(Topic.order_index, Topic.id),
    ).all()
    cards: list[TopicMasteryRead] = []
    for topic in root_topics:
        mastery = mastery_by_topic_id.get(topic.id)
        cards.append(
            TopicMasteryRead(
                topic_id=topic.id,
                slug=topic.slug,
                name=topic.name,
                mastery_score=mastery.mastery_score if mastery is not None else 0.0,
                attempts_count=mastery.attempts_count if mastery is not None else 0,
            )
        )
    return cards


def _weak_prerequisites(
    session: Session,
    mastery_by_topic_id: dict[int, UserTopicMastery],
) -> list[WeakPrerequisiteRead]:
    edges = (
        session.scalars(
            select(ConceptEdge)
            .where(ConceptEdge.relationship_type == ConceptEdgeRelationshipType.REQUIRES)
            .options(
                joinedload(ConceptEdge.source_concept),
                joinedload(ConceptEdge.target_concept),
            ),
        )
        .unique()
        .all()
    )

    weak_items: list[WeakPrerequisiteRead] = []
    for edge in edges:
        prerequisite_topic_id = edge.target_concept.topic_id
        mastery = mastery_by_topic_id.get(prerequisite_topic_id)
        prerequisite_score = mastery.mastery_score if mastery is not None else 0.0
        if prerequisite_score >= WEAK_MASTERY_THRESHOLD:
            continue

        weak_items.append(
            WeakPrerequisiteRead(
                concept_slug=edge.source_concept.slug,
                concept_name=edge.source_concept.name,
                prerequisite_slug=edge.target_concept.slug,
                prerequisite_name=edge.target_concept.name,
                prerequisite_mastery_score=prerequisite_score,
            )
        )

    weak_items.sort(key=lambda item: item.prerequisite_mastery_score)
    return weak_items


def get_dashboard(session: Session) -> DashboardRead:
    mastery_by_topic_id = _mastery_by_topic_id(session)
    return DashboardRead(
        user_id=LOCAL_USER_ID,
        topic_mastery=_topic_mastery_cards(session, mastery_by_topic_id),
        weak_prerequisites=_weak_prerequisites(session, mastery_by_topic_id),
    )
