from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.concept import Concept, ConceptEdge
from app.models.topic import Topic
from app.schemas.admin_concepts import ConceptUpdate
from app.schemas.concept import (
    ConceptDetailRead,
    ConceptNeighborRead,
    ConceptRead,
    ConceptSummaryRead,
)
from app.seeds.utils import slugify


class ConceptEditorError(ValueError):
    """Raised when a concept editor mutation is invalid."""


def list_concepts_for_editor(
    session: Session,
    *,
    topic_slug: str | None = None,
) -> list[ConceptSummaryRead]:
    query = select(Concept).options(joinedload(Concept.topic)).order_by(Concept.name, Concept.id)
    if topic_slug is not None:
        topic_ids = _topic_scope_ids(session, topic_slug)
        if topic_ids is None:
            return []
        query = query.where(Concept.topic_id.in_(topic_ids))

    concepts = session.scalars(query).unique().all()
    return [_concept_summary(concept) for concept in concepts]


def get_concept_for_editor(session: Session, slug: str) -> ConceptDetailRead:
    concept = _get_concept_by_slug(session, slug)
    return _concept_detail(concept)


def update_concept(
    session: Session,
    slug: str,
    payload: ConceptUpdate,
) -> ConceptDetailRead:
    concept = _get_concept_by_slug(session, slug)
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise ConceptEditorError("no fields provided to update")

    # Graph edges are intentionally never mutated by this editor.
    if "name" in updates and updates["name"] is not None:
        name = updates["name"].strip()
        if not name:
            raise ConceptEditorError("name must not be blank")
        concept.name = name

    if "slug" in updates and updates["slug"] is not None:
        new_slug = slugify(updates["slug"])
        if not new_slug:
            raise ConceptEditorError("slug must not be blank")
        if new_slug != concept.slug:
            conflict = session.scalar(select(Concept.id).where(Concept.slug == new_slug))
            if conflict is not None:
                raise ConceptEditorError(f"slug '{new_slug}' is already in use")
            concept.slug = new_slug[:120]

    for field in (
        "definition",
        "formula",
        "intuition",
        "worked_example",
        "common_mistakes",
        "interview_tips",
        "prerequisites",
    ):
        if field in updates:
            concept.__setattr__(field, _blank_to_none(updates[field]))

    session.add(concept)
    session.commit()
    return get_concept_for_editor(session, concept.slug)


def _get_concept_by_slug(session: Session, slug: str) -> Concept:
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
        raise LookupError(f"concept '{slug}' not found")
    return concept


def _topic_scope_ids(session: Session, topic_slug: str) -> list[int] | None:
    topic = session.scalar(
        select(Topic).where(Topic.slug == topic_slug).options(selectinload(Topic.subtopics)),
    )
    if topic is None:
        return None
    topic_ids = [topic.id]
    topic_ids.extend(subtopic.id for subtopic in topic.subtopics)
    return topic_ids


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
        worked_example=concept.worked_example,
        common_mistakes=concept.common_mistakes,
        interview_tips=concept.interview_tips,
        prerequisites=concept.prerequisites,
    )


def _concept_detail(concept: Concept) -> ConceptDetailRead:
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
    base = _concept_read(concept)
    return ConceptDetailRead(**base.model_dump(), neighbors=neighbors)


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
