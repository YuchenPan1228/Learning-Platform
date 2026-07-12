from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.concept import ConceptEdge
from app.models.constants import LOCAL_USER_ID
from app.models.enums import ConceptEdgeRelationshipType
from app.models.topic import Topic
from app.schemas.dashboard import DashboardRead, TopicMasteryRead, WeakPrerequisiteRead
from app.services.progress import (
    attempts_count_for_root_topic,
    get_question_progress_map,
    mastery_for_topic_ids,
    question_ids_for_root_topic,
    question_ids_for_topic_scope,
)

WEAK_MASTERY_THRESHOLD = 50.0


def _topic_mastery_score(
    session: Session,
    topic_id: int,
    progress_map: dict,
) -> float:
    question_ids = question_ids_for_root_topic(session, topic_id)
    return mastery_for_topic_ids(question_ids, progress_map)


def _topic_mastery_cards(session: Session) -> list[TopicMasteryRead]:
    progress_map = get_question_progress_map(session)
    root_topics = session.scalars(
        select(Topic).where(Topic.parent_topic_id.is_(None)).order_by(Topic.order_index, Topic.id),
    ).all()
    cards: list[TopicMasteryRead] = []
    for topic in root_topics:
        cards.append(
            TopicMasteryRead(
                topic_id=topic.id,
                slug=topic.slug,
                name=topic.name,
                mastery_score=_topic_mastery_score(session, topic.id, progress_map),
                attempts_count=attempts_count_for_root_topic(session, topic.id),
            )
        )
    return cards


def _weak_prerequisites(session: Session) -> list[WeakPrerequisiteRead]:
    progress_map = get_question_progress_map(session)
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
        prerequisite_score = mastery_for_topic_ids(
            question_ids_for_topic_scope(session, prerequisite_topic_id),
            progress_map,
        )
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
    return DashboardRead(
        user_id=LOCAL_USER_ID,
        topic_mastery=_topic_mastery_cards(session),
        weak_prerequisites=_weak_prerequisites(session),
    )
