from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.dedup.fingerprints import apply_question_fingerprints
from app.models.enums import ContentStatus
from app.models.question import Question
from app.models.tag import QuestionTag, Tag
from app.models.topic import Topic
from app.schemas.admin_questions import QuestionUpdate
from app.schemas.question import QuestionDetailRead, QuestionSummaryRead
from app.schemas.tag import TagRead


class QuestionEditorError(ValueError):
    """Raised when a practice-question editor mutation is invalid."""


def list_questions_for_editor(
    session: Session,
    *,
    topic_slug: str | None = None,
    status: ContentStatus | None = None,
) -> list[QuestionSummaryRead]:
    query = (
        select(Question)
        .options(
            joinedload(Question.topic),
            joinedload(Question.subtopic),
            selectinload(Question.question_tags).joinedload(QuestionTag.tag),
        )
        .order_by(Question.id.desc())
    )
    if topic_slug is not None:
        topic_ids = _topic_scope_ids(session, topic_slug)
        if topic_ids is None:
            return []
        query = query.where(Question.topic_id.in_(topic_ids))
    if status is not None:
        query = query.where(Question.status == status)

    questions = session.scalars(query).unique().all()
    return [_question_summary(question) for question in questions]


def get_question_for_editor(session: Session, question_id: int) -> QuestionDetailRead:
    question = _get_question(session, question_id)
    return _question_detail(question)


def update_question(
    session: Session,
    question_id: int,
    payload: QuestionUpdate,
) -> QuestionDetailRead:
    question = _get_question(session, question_id)
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise QuestionEditorError("no fields provided to update")

    text_changed = False

    if "title" in updates and updates["title"] is not None:
        title = updates["title"].strip()
        if not title:
            raise QuestionEditorError("title must not be blank")
        question.title = title
        text_changed = True

    if "body" in updates and updates["body"] is not None:
        body = updates["body"].strip()
        if not body:
            raise QuestionEditorError("body must not be blank")
        question.body = body
        text_changed = True

    if "difficulty" in updates and updates["difficulty"] is not None:
        question.difficulty = updates["difficulty"]

    if "status" in updates and updates["status"] is not None:
        question.status = updates["status"]

    if "estimated_time_seconds" in updates:
        question.estimated_time_seconds = updates["estimated_time_seconds"]

    if "topic_slug" in updates and updates["topic_slug"] is not None:
        topic_id = session.scalar(select(Topic.id).where(Topic.slug == updates["topic_slug"]))
        if topic_id is None:
            raise QuestionEditorError(f"unknown topic_slug '{updates['topic_slug']}'")
        question.topic_id = topic_id

    if "subtopic_slug" in updates:
        subtopic_slug = updates["subtopic_slug"]
        if subtopic_slug is None or (isinstance(subtopic_slug, str) and not subtopic_slug.strip()):
            question.subtopic_id = None
        else:
            subtopic_id = session.scalar(select(Topic.id).where(Topic.slug == subtopic_slug))
            if subtopic_id is None:
                raise QuestionEditorError(f"unknown subtopic_slug '{subtopic_slug}'")
            question.subtopic_id = subtopic_id

    for field in (
        "canonical_solution",
        "short_answer",
        "company_hint",
        "expected_solution_pattern",
        "source_attribution",
    ):
        if field in updates:
            question.__setattr__(field, _blank_to_none(updates[field]))

    if "common_mistakes" in updates:
        question.common_mistakes = _normalize_string_list(updates["common_mistakes"])
    if "prerequisites" in updates:
        question.prerequisites = _normalize_string_list(updates["prerequisites"])

    if text_changed:
        apply_question_fingerprints(question)

    session.add(question)
    session.commit()
    return get_question_for_editor(session, question.id)


def delete_question(session: Session, question_id: int) -> int:
    question = session.get(Question, question_id)
    if question is None:
        raise LookupError(f"question {question_id} not found")
    session.delete(question)
    session.commit()
    return question_id


def _get_question(session: Session, question_id: int) -> Question:
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
        raise LookupError(f"question {question_id} not found")
    return question


def _topic_scope_ids(session: Session, topic_slug: str) -> list[int] | None:
    topic = session.scalar(
        select(Topic).where(Topic.slug == topic_slug).options(selectinload(Topic.subtopics)),
    )
    if topic is None:
        return None
    topic_ids = [topic.id]
    topic_ids.extend(subtopic.id for subtopic in topic.subtopics)
    return topic_ids


def _tag_read(tag: Tag) -> TagRead:
    return TagRead(id=tag.id, slug=tag.slug, name=tag.name, category=tag.category)


def _question_summary(question: Question) -> QuestionSummaryRead:
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


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _normalize_string_list(value: list[str] | None) -> list[str] | None:
    if value is None:
        return None
    items = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return items or None
