from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.dependencies import SessionDep
from app.models.concept import Concept, ConceptEdge
from app.models.topic import Topic
from app.schemas.concept import (
    ConceptDetailRead,
    ConceptNeighborRead,
    ConceptRead,
    ConceptSummaryRead,
)

router = APIRouter(prefix="/concepts", tags=["concepts"])


def _concept_summary(concept: Concept) -> ConceptSummaryRead:
    return ConceptSummaryRead(
        id=concept.id,
        slug=concept.slug,
        name=concept.name,
        topic_id=concept.topic_id,
        topic_slug=concept.topic.slug,
    )


def _concept_read(concept: Concept) -> ConceptRead:
    return ConceptRead(
        id=concept.id,
        slug=concept.slug,
        name=concept.name,
        topic_id=concept.topic_id,
        topic_slug=concept.topic.slug,
        definition=concept.definition,
        formula=concept.formula,
        intuition=concept.intuition,
        common_mistakes=concept.common_mistakes,
        interview_tips=concept.interview_tips,
        prerequisites=concept.prerequisites,
    )


def _concept_neighbors(concept: Concept) -> list[ConceptNeighborRead]:
    neighbors: list[ConceptNeighborRead] = []
    for edge in concept.outgoing_edges:
        neighbors.append(
            ConceptNeighborRead(
                slug=edge.target_concept.slug,
                name=edge.target_concept.name,
                relationship_type=edge.relationship_type,
                direction="outgoing",
            )
        )
    for edge in concept.incoming_edges:
        neighbors.append(
            ConceptNeighborRead(
                slug=edge.source_concept.slug,
                name=edge.source_concept.name,
                relationship_type=edge.relationship_type,
                direction="incoming",
            )
        )
    return neighbors


def _topic_scope_ids(session: Session, topic_slug: str) -> list[int] | None:
    topic = session.scalar(
        select(Topic)
        .where(Topic.slug == topic_slug)
        .options(selectinload(Topic.subtopics)),
    )
    if topic is None:
        return None
    topic_ids = [topic.id]
    topic_ids.extend(subtopic.id for subtopic in topic.subtopics)
    return topic_ids


@router.get("")
def list_concepts(
    session: SessionDep,
    topic_slug: str | None = Query(default=None),
) -> list[ConceptSummaryRead]:
    query = select(Concept).options(joinedload(Concept.topic)).order_by(Concept.name, Concept.id)
    if topic_slug is not None:
        topic_ids = _topic_scope_ids(session, topic_slug)
        if topic_ids is None:
            return []
        query = query.where(Concept.topic_id.in_(topic_ids))
    concepts = session.scalars(query).unique().all()
    return [_concept_summary(concept) for concept in concepts]


@router.get("/{slug}")
def get_concept(slug: str, session: SessionDep) -> ConceptDetailRead:
    concept = session.scalar(
        select(Concept)
        .where(Concept.slug == slug)
        .options(
            joinedload(Concept.topic),
            selectinload(Concept.outgoing_edges).joinedload(ConceptEdge.target_concept),
            selectinload(Concept.incoming_edges).joinedload(ConceptEdge.source_concept),
        ),
    )
    if concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")

    base = _concept_read(concept)
    return ConceptDetailRead(
        **base.model_dump(),
        neighbors=_concept_neighbors(concept),
    )
