from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.concept import Concept
from app.models.constants import LOCAL_USER_ID
from app.models.enums import ContentStatus, Difficulty, LearningSignalType, SearchResourceType
from app.models.learning_signal import LearningSignal
from app.models.question import Question
from app.models.topic import Topic
from app.routers.concepts import _topic_scope_ids
from app.search.fts import concept_search_vector, plainto_tsquery, question_search_vector


@dataclass(frozen=True, slots=True)
class SearchResults:
    questions: list[Question]
    concepts: list[Concept]


def _resolve_topic_id(session: Session, slug: str) -> int | None:
    return session.scalar(select(Topic.id).where(Topic.slug == slug))


def search_questions(
    session: Session,
    query: str,
    *,
    topic_slug: str | None,
    difficulty: Difficulty | None,
    limit: int,
) -> list[Question]:
    tsquery = plainto_tsquery(query)
    ts_rank = func.ts_rank(question_search_vector(), tsquery)
    statement = (
        select(Question)
        .options(
            joinedload(Question.topic),
            joinedload(Question.subtopic),
        )
        .where(Question.status == ContentStatus.APPROVED)
        .where(question_search_vector().op("@@")(tsquery))
        .order_by(ts_rank.desc(), Question.id)
        .limit(limit)
    )

    if topic_slug is not None:
        topic_id = _resolve_topic_id(session, topic_slug)
        if topic_id is None:
            return []
        statement = statement.where(Question.topic_id == topic_id)

    if difficulty is not None:
        statement = statement.where(Question.difficulty == difficulty)

    return list(session.scalars(statement).unique().all())


def search_concepts(
    session: Session,
    query: str,
    *,
    topic_slug: str | None,
    limit: int,
) -> list[Concept]:
    tsquery = plainto_tsquery(query)
    ts_rank = func.ts_rank(concept_search_vector(), tsquery)
    statement = (
        select(Concept)
        .options(joinedload(Concept.topic))
        .where(concept_search_vector().op("@@")(tsquery))
        .order_by(ts_rank.desc(), Concept.id)
        .limit(limit)
    )

    if topic_slug is not None:
        topic_ids = _topic_scope_ids(session, topic_slug)
        if topic_ids is None:
            return []
        statement = statement.where(Concept.topic_id.in_(topic_ids))

    return list(session.scalars(statement).unique().all())


def search_content(
    session: Session,
    query: str,
    *,
    types: list[SearchResourceType],
    topic_slug: str | None,
    difficulty: Difficulty | None,
    limit: int,
) -> SearchResults:
    questions: list[Question] = []
    concepts: list[Concept] = []

    if SearchResourceType.QUESTIONS in types:
        questions = search_questions(
            session,
            query,
            topic_slug=topic_slug,
            difficulty=difficulty,
            limit=limit,
        )
    if SearchResourceType.CONCEPTS in types:
        concepts = search_concepts(
            session,
            query,
            topic_slug=topic_slug,
            limit=limit,
        )

    return SearchResults(questions=questions, concepts=concepts)


def record_search_miss(
    session: Session,
    *,
    query: str,
    types: list[SearchResourceType],
    topic_slug: str | None,
    result_count: int,
) -> None:
    if result_count > 0:
        return

    topic_id = _resolve_topic_id(session, topic_slug) if topic_slug is not None else None
    session.add(
        LearningSignal(
            user_id=LOCAL_USER_ID,
            signal_type=LearningSignalType.SEARCH_MISS,
            topic_id=topic_id,
            question_id=None,
            payload_json={
                "query": query,
                "types": [resource_type.value for resource_type in types],
                "topic_slug": topic_slug,
                "result_count": result_count,
            },
        )
    )
    session.commit()
