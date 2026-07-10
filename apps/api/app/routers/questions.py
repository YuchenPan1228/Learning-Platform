from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.dependencies import SessionDep
from app.models.enums import ContentStatus, Difficulty
from app.models.question import Question
from app.models.topic import Topic
from app.schemas.question import QuestionDetailRead, QuestionSummaryRead

router = APIRouter(prefix="/questions", tags=["questions"])

DifficultyQuery = Annotated[Difficulty | None, Query()]
StatusQuery = Annotated[ContentStatus, Query()]
LimitQuery = Annotated[int, Query(ge=1, le=100)]
OffsetQuery = Annotated[int, Query(ge=0)]
TopicSlugQuery = Annotated[str | None, Query()]
SubtopicSlugQuery = Annotated[str | None, Query()]


def _question_summary(question: Question) -> QuestionSummaryRead:
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


@router.get("")
def list_questions(
    session: SessionDep,
    topic_slug: TopicSlugQuery = None,
    subtopic_slug: SubtopicSlugQuery = None,
    difficulty: DifficultyQuery = None,
    status: StatusQuery = ContentStatus.APPROVED,
    limit: LimitQuery = 50,
    offset: OffsetQuery = 0,
) -> list[QuestionSummaryRead]:
    query = (
        select(Question)
        .options(
            joinedload(Question.topic),
            joinedload(Question.subtopic),
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

    if difficulty is not None:
        query = query.where(Question.difficulty == difficulty)

    questions = session.scalars(query).unique().all()
    return [_question_summary(question) for question in questions]


@router.get("/{question_id}")
def get_question(question_id: int, session: SessionDep) -> QuestionDetailRead:
    question = session.scalar(
        select(Question)
        .where(Question.id == question_id)
        .options(
            joinedload(Question.topic),
            joinedload(Question.subtopic),
        ),
    )
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return _question_detail(question)
