from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.concept import Concept, ConceptEdge
from app.models.topic import Topic
from app.seeds.data.knowledge_graph import (
    CONCEPT_DETAILS,
    CONCEPT_EDGES,
    ConceptEdgeSeed,
    default_concept_definition,
)
from app.seeds.data.topic_hierarchy import TOPIC_TREE, SubtopicSeed, TopicSeed
from app.seeds.utils import slugify


@dataclass(frozen=True, slots=True)
class SeedSummary:
    topics: int
    concepts: int
    concept_edges: int


def _subtopic_slug(subtopic: SubtopicSeed) -> str:
    return subtopic.slug or slugify(subtopic.name)


def _upsert_topic(
    session: Session,
    *,
    slug: str,
    name: str,
    parent_topic_id: int | None,
    order_index: int,
    description: str | None,
) -> Topic:
    topic = session.scalar(select(Topic).where(Topic.slug == slug))
    if topic is None:
        topic = Topic(
            slug=slug,
            name=name,
            parent_topic_id=parent_topic_id,
            order_index=order_index,
            description=description,
        )
        session.add(topic)
    else:
        topic.name = name
        topic.parent_topic_id = parent_topic_id
        topic.order_index = order_index
        topic.description = description
    session.flush()
    return topic


def seed_topics(session: Session) -> dict[str, Topic]:
    topics_by_slug: dict[str, Topic] = {}

    for section_index, section in enumerate(TOPIC_TREE):
        parent = _upsert_topic(
            session,
            slug=section.slug,
            name=section.name,
            parent_topic_id=None,
            order_index=section_index,
            description=section.description,
        )
        topics_by_slug[section.slug] = parent

        for subtopic_index, subtopic in enumerate(section.subtopics):
            child_slug = _subtopic_slug(subtopic)
            child = _upsert_topic(
                session,
                slug=child_slug,
                name=subtopic.name,
                parent_topic_id=parent.id,
                order_index=subtopic_index,
                description=None,
            )
            topics_by_slug[child_slug] = child

    return topics_by_slug


def _concept_payload(
    *,
    subtopic: SubtopicSeed,
    section: TopicSeed,
    topic: Topic,
    child_slug: str,
) -> dict[str, str | None]:
    detailed = CONCEPT_DETAILS.get(child_slug)
    if detailed is not None:
        return {
            "name": detailed.name,
            "definition": detailed.definition,
            "formula": detailed.formula,
            "intuition": detailed.intuition,
            "common_mistakes": detailed.common_mistakes,
            "interview_tips": detailed.interview_tips,
            "prerequisites": detailed.prerequisites,
        }

    return {
        "name": subtopic.name,
        "definition": default_concept_definition(subtopic.name, section.name),
        "formula": None,
        "intuition": None,
        "common_mistakes": None,
        "interview_tips": None,
        "prerequisites": None,
    }


def seed_concepts(session: Session, topics_by_slug: dict[str, Topic]) -> dict[str, Concept]:
    concepts_by_slug: dict[str, Concept] = {}

    for section in TOPIC_TREE:
        for subtopic in section.subtopics:
            child_slug = _subtopic_slug(subtopic)
            topic = topics_by_slug[child_slug]
            payload = _concept_payload(
                subtopic=subtopic,
                section=section,
                topic=topic,
                child_slug=child_slug,
            )

            concept = session.scalar(select(Concept).where(Concept.slug == child_slug))
            if concept is None:
                concept = Concept(slug=child_slug, topic_id=topic.id, **payload)
                session.add(concept)
            else:
                concept.topic_id = topic.id
                for field, value in payload.items():
                    setattr(concept, field, value)

            session.flush()
            concepts_by_slug[child_slug] = concept

    return concepts_by_slug


def _upsert_concept_edge(
    session: Session,
    *,
    edge: ConceptEdgeSeed,
    concepts_by_slug: dict[str, Concept],
) -> None:
    source = concepts_by_slug.get(edge.source_slug)
    target = concepts_by_slug.get(edge.target_slug)
    if source is None or target is None:
        msg = f"Missing concept for edge {edge.source_slug} -> {edge.target_slug}"
        raise ValueError(msg)

    existing = session.scalar(
        select(ConceptEdge).where(
            ConceptEdge.source_concept_id == source.id,
            ConceptEdge.target_concept_id == target.id,
            ConceptEdge.relationship_type == edge.relationship_type,
        )
    )
    if existing is None:
        session.add(
            ConceptEdge(
                source_concept_id=source.id,
                target_concept_id=target.id,
                relationship_type=edge.relationship_type,
                weight=edge.weight,
            )
        )
    else:
        existing.weight = edge.weight


def seed_concept_edges(session: Session, concepts_by_slug: dict[str, Concept]) -> int:
    for edge in CONCEPT_EDGES:
        _upsert_concept_edge(session, edge=edge, concepts_by_slug=concepts_by_slug)
    session.flush()
    return len(CONCEPT_EDGES)


def seed_knowledge_graph(session: Session) -> SeedSummary:
    topics_by_slug = seed_topics(session)
    concepts_by_slug = seed_concepts(session, topics_by_slug)
    edge_count = seed_concept_edges(session, concepts_by_slug)
    session.commit()
    return SeedSummary(
        topics=len(topics_by_slug),
        concepts=len(concepts_by_slug),
        concept_edges=edge_count,
    )
