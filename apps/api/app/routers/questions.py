from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.ai.errors import AIProviderRequestError
from app.dedup.detection import find_question_duplicates
from app.dependencies import AIProviderDep, SessionDep
from app.models.concept import Concept
from app.models.enums import ContentStatus, Difficulty, QuestionProgressStatus
from app.models.question import Question
from app.models.tag import QuestionTag, Tag
from app.models.topic import Topic
from app.schemas.ai_explanation import AIExplanationRequest, AIExplanationResponse
from app.schemas.duplicate import DuplicateMatchRead, QuestionDuplicatesRead
from app.schemas.practice import SelfCheckRequest, SelfCheckResponse
from app.schemas.progress import QuestionProgressRead, SetQuestionProgressRequest
from app.schemas.question import QuestionDetailRead, QuestionSummaryRead
from app.schemas.tag import TagRead
from app.services.ai_explanation import (
    AIExplanationResponseError,
    generate_question_explanation,
)
from app.services.answer_check import grade_short_answer
from app.services.progress import (
    get_progress_by_question_id,
    get_question_progress,
    set_question_progress,
)

router = APIRouter(prefix="/questions", tags=["questions"])

DifficultyQuery = Annotated[Difficulty | None, Query()]
StatusQuery = Annotated[ContentStatus, Query()]
LimitQuery = Annotated[int, Query(ge=1, le=100)]
OffsetQuery = Annotated[int, Query(ge=0)]
TopicSlugQuery = Annotated[str | None, Query()]
SubtopicSlugQuery = Annotated[str | None, Query()]
ConceptSlugQuery = Annotated[str | None, Query()]
TagSlugQuery = Annotated[str | None, Query()]
IncludeProgressQuery = Annotated[bool, Query()]


def _tag_read(tag: Tag) -> TagRead:
    return TagRead(id=tag.id, slug=tag.slug, name=tag.name, category=tag.category)


def _question_summary(
    question: Question,
    *,
    progress_status: QuestionProgressStatus | None = None,
    attempt_count: int | None = None,
) -> QuestionSummaryRead:
    tags = sorted(
        (_tag_read(question_tag.tag) for question_tag in question.question_tags),
        key=lambda item: (item.category.value, item.name, item.id),
    )
    return QuestionSummaryRead(
        id=question.id,
        title=question.title,
        difficulty=question.difficulty,
        topic_id=question.topic_id,
        topic_slug=question.topic.slug,
        subtopic_id=question.subtopic_id,
        subtopic_slug=question.subtopic.slug if question.subtopic is not None else None,
        estimated_time_seconds=question.estimated_time_seconds,
        company_hint=question.company_hint,
        status=question.status,
        tags=tags,
        progress_status=progress_status,
        attempt_count=attempt_count,
    )


def _question_detail(question: Question) -> QuestionDetailRead:
    summary = _question_summary(question)
    return QuestionDetailRead(
        **summary.model_dump(),
        body=question.body,
        canonical_solution=question.canonical_solution,
        short_answer=question.short_answer,
        expected_solution_pattern=question.expected_solution_pattern,
        common_mistakes=question.common_mistakes,
        prerequisites=question.prerequisites,
        source_attribution=question.source_attribution,
    )


def _resolve_topic_id(session: Session, slug: str) -> int | None:
    return session.scalar(select(Topic.id).where(Topic.slug == slug))


def _resolve_concept_topic_id(session: Session, slug: str) -> int | None:
    return session.scalar(select(Concept.topic_id).where(Concept.slug == slug))


def _resolve_tag_id(session: Session, slug: str) -> int | None:
    return session.scalar(select(Tag.id).where(Tag.slug == slug))


@router.get("")
def list_questions(
    session: SessionDep,
    topic_slug: TopicSlugQuery = None,
    subtopic_slug: SubtopicSlugQuery = None,
    concept_slug: ConceptSlugQuery = None,
    tag_slug: TagSlugQuery = None,
    difficulty: DifficultyQuery = None,
    status: StatusQuery = ContentStatus.APPROVED,
    include_progress: IncludeProgressQuery = False,
    limit: LimitQuery = 50,
    offset: OffsetQuery = 0,
) -> list[QuestionSummaryRead]:
    query = (
        select(Question)
        .options(
            joinedload(Question.topic),
            joinedload(Question.subtopic),
            selectinload(Question.question_tags).joinedload(QuestionTag.tag),
        )
        .where(Question.status == status)
        .order_by(Question.id)
        .limit(limit)
        .offset(offset)
    )

    if topic_slug is not None:
        topic_id = _resolve_topic_id(session, topic_slug)
        if topic_id is None:
            return []
        query = query.where(Question.topic_id == topic_id)

    if subtopic_slug is not None:
        subtopic_id = _resolve_topic_id(session, subtopic_slug)
        if subtopic_id is None:
            return []
        query = query.where(Question.subtopic_id == subtopic_id)

    if concept_slug is not None:
        concept_topic_id = _resolve_concept_topic_id(session, concept_slug)
        if concept_topic_id is None:
            return []
        query = query.where(Question.subtopic_id == concept_topic_id)

    if tag_slug is not None:
        tag_id = _resolve_tag_id(session, tag_slug)
        if tag_id is None:
            return []
        query = query.join(QuestionTag).where(QuestionTag.tag_id == tag_id)

    if difficulty is not None:
        query = query.where(Question.difficulty == difficulty)

    questions = session.scalars(query).unique().all()
    progress_by_question_id = get_progress_by_question_id(session) if include_progress else None
    summaries: list[QuestionSummaryRead] = []
    for question in questions:
        progress = None
        if progress_by_question_id is not None:
            progress = progress_by_question_id.get(question.id)
        summaries.append(
            _question_summary(
                question,
                progress_status=(
                    progress.status
                    if progress is not None
                    else QuestionProgressStatus.NOT_ATTEMPTED
                )
                if include_progress
                else None,
                attempt_count=progress.attempt_count if progress is not None else None,
            ),
        )
    return summaries


@router.post("/{question_id}/explanation")
def explain_question(
    question_id: int,
    payload: AIExplanationRequest,
    session: SessionDep,
    provider: AIProviderDep,
) -> AIExplanationResponse:
    question = session.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    try:
        return generate_question_explanation(
            session,
            provider,
            question=question,
            user_answer=payload.answer,
        )
    except (AIProviderRequestError, AIExplanationResponseError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/{question_id}/duplicates")
def get_question_duplicates(question_id: int, session: SessionDep) -> QuestionDuplicatesRead:
    question = session.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    matches = find_question_duplicates(session, question_id)
    return QuestionDuplicatesRead(
        question_id=question_id,
        matches=[
            DuplicateMatchRead(
                question_id=match.question_id,
                title=match.title,
                match_type=match.match_type,
                similarity_score=match.similarity_score,
            )
            for match in matches
        ],
    )


@router.post("/{question_id}/self-check")
def self_check_question(
    question_id: int,
    payload: SelfCheckRequest,
    session: SessionDep,
) -> SelfCheckResponse:
    question = session.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    supported, is_correct, feedback = grade_short_answer(
        short_answer=question.short_answer,
        user_answer=payload.answer,
    )
    return SelfCheckResponse(
        question_id=question_id,
        supported=supported,
        is_correct=is_correct,
        feedback=feedback,
    )


@router.post("/{question_id}/progress")
def update_question_progress(
    question_id: int,
    payload: SetQuestionProgressRequest,
    session: SessionDep,
) -> QuestionProgressRead:
    question = session.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return set_question_progress(session, question_id=question_id, payload=payload)


@router.get("/{question_id}/progress")
def read_question_progress(question_id: int, session: SessionDep) -> QuestionProgressRead:
    question = session.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    progress = get_question_progress(session, question_id)
    return QuestionProgressRead(
        question_id=question_id,
        status=progress.status,
        attempt_count=progress.attempt_count,
        manually_marked=progress.manually_marked,
    )


@router.get("/{question_id}")
def get_question(question_id: int, session: SessionDep) -> QuestionDetailRead:
    question = session.scalar(
        select(Question)
        .where(Question.id == question_id)
        .options(
            joinedload(Question.topic),
            joinedload(Question.subtopic),
            selectinload(Question.question_tags).joinedload(QuestionTag.tag),
        ),
    )
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return _question_detail(question)
