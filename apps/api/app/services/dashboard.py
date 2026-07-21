from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.concept import ConceptEdge
from app.models.enums import ConceptEdgeRelationshipType
from app.models.topic import Topic
from app.schemas.dashboard import DashboardRead, TopicMasteryRead, WeakPrerequisiteRead
from app.services.progress import TopicProgressStats, get_topic_progress_stats
from app.services.study_planner import build_daily_study_plan

WEAK_MASTERY_THRESHOLD = 50.0


def _mastery_card(topic: Topic, stats: TopicProgressStats | None) -> TopicMasteryRead:
    return TopicMasteryRead(
        topic_id=topic.id,
        slug=topic.slug,
        name=topic.name,
        mastery_score=stats.mastery_score if stats is not None else 0.0,
        attempts_count=stats.attempts_count if stats is not None else 0,
        solved_count=stats.solved_count if stats is not None else 0,
        total_questions=stats.total_questions if stats is not None else 0,
    )


def _topic_mastery_cards(session: Session) -> list[TopicMasteryRead]:
    topic_stats = get_topic_progress_stats(session)
    root_topics = session.scalars(
        select(Topic).where(Topic.parent_topic_id.is_(None)).order_by(Topic.order_index, Topic.id),
    ).all()
    return [_mastery_card(topic, topic_stats.get(topic.id)) for topic in root_topics]


def _subtopic_mastery_cards(session: Session) -> list[TopicMasteryRead]:
    topic_stats = get_topic_progress_stats(session)
    root_topics = session.scalars(
        select(Topic)
        .where(Topic.parent_topic_id.is_(None))
        .options(selectinload(Topic.subtopics))
        .order_by(Topic.order_index, Topic.id),
    ).all()
    cards: list[TopicMasteryRead] = []
    for root in root_topics:
        for subtopic in sorted(root.subtopics, key=lambda item: (item.order_index, item.id)):
            cards.append(_mastery_card(subtopic, topic_stats.get(subtopic.id)))
    return cards


def _weak_prerequisites(session: Session) -> list[WeakPrerequisiteRead]:
    topic_stats = get_topic_progress_stats(session)
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
        stats = topic_stats.get(prerequisite_topic_id)
        prerequisite_score = stats.mastery_score if stats is not None else 0.0
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
    from app.models.constants import LOCAL_USER_ID

    return DashboardRead(
        user_id=LOCAL_USER_ID,
        topic_mastery=_topic_mastery_cards(session),
        subtopic_mastery=_subtopic_mastery_cards(session),
        weak_prerequisites=_weak_prerequisites(session),
        daily_plan=build_daily_study_plan(session),
    )
