from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session_factory
from app.dedup.fingerprints import apply_question_fingerprints
from app.models.enums import TagCategory
from app.models.flashcard import Flashcard
from app.models.question import Question
from app.models.tag import QuestionTag, Tag
from app.models.topic import Topic
from app.seeds.data.flashcard_seed import FlashcardSeed, flashcard_source_id
from app.seeds.data.mvp import ALL_MVP_FLASHCARDS, ALL_MVP_QUESTIONS
from app.seeds.data.question_seed import QuestionSeed, seed_extraction_method
from app.seeds.utils import slugify


@dataclass(frozen=True, slots=True)
class MvpContentSummary:
    probability_questions: int
    mental_math_questions: int
    coding_questions: int
    finance_questions: int
    market_game_questions: int
    flashcards: int
    tags: int

    @property
    def total(self) -> int:
        return (
            self.probability_questions
            + self.mental_math_questions
            + self.coding_questions
            + self.finance_questions
            + self.market_game_questions
        )


def _load_topics_by_slug(session: Session) -> dict[str, Topic]:
    topics = session.scalars(select(Topic)).all()
    return {topic.slug: topic for topic in topics}


def _upsert_tag(
    session: Session,
    *,
    slug: str,
    name: str,
    category: TagCategory,
) -> Tag:
    tag = session.scalar(select(Tag).where(Tag.slug == slug))
    if tag is None:
        tag = Tag(slug=slug, name=name, category=category)
        session.add(tag)
        session.flush()
    else:
        tag.name = name
        tag.category = category
    return tag


def _ensure_question_tag(session: Session, *, question: Question, tag: Tag) -> None:
    existing = session.scalar(
        select(QuestionTag).where(
            QuestionTag.question_id == question.id,
            QuestionTag.tag_id == tag.id,
        )
    )
    if existing is None:
        session.add(QuestionTag(question_id=question.id, tag_id=tag.id))


def _sync_question_tags(
    session: Session,
    *,
    question: Question,
    seed: QuestionSeed,
    topics_by_slug: dict[str, Topic],
) -> None:
    desired_tag_ids: set[int] = set()

    if seed.subtopic_slug is not None:
        subtopic = topics_by_slug.get(seed.subtopic_slug)
        if subtopic is not None:
            tag = _upsert_tag(
                session,
                slug=subtopic.slug,
                name=subtopic.name,
                category=TagCategory.CONCEPT,
            )
            desired_tag_ids.add(tag.id)
            _ensure_question_tag(session, question=question, tag=tag)

    if seed.company_hint is not None and seed.company_hint.strip():
        company_slug = slugify(seed.company_hint)
        tag = _upsert_tag(
            session,
            slug=company_slug,
            name=seed.company_hint.strip(),
            category=TagCategory.COMPANY,
        )
        desired_tag_ids.add(tag.id)
        _ensure_question_tag(session, question=question, tag=tag)

    existing_links = session.scalars(
        select(QuestionTag).where(QuestionTag.question_id == question.id)
    ).all()
    for link in existing_links:
        if link.tag_id not in desired_tag_ids:
            session.delete(link)


def _upsert_question(
    session: Session,
    seed: QuestionSeed,
    topics_by_slug: dict[str, Topic],
) -> None:
    parent_topic = topics_by_slug.get(seed.topic_slug)
    if parent_topic is None:
        msg = f"Missing topic slug '{seed.topic_slug}' for seed {seed.seed_key}"
        raise ValueError(msg)

    subtopic = None
    if seed.subtopic_slug is not None:
        subtopic = topics_by_slug.get(seed.subtopic_slug)
        if subtopic is None:
            msg = f"Missing subtopic slug '{seed.subtopic_slug}' for seed {seed.seed_key}"
            raise ValueError(msg)

    extraction_method = seed_extraction_method(seed.seed_key)
    question = session.scalar(
        select(Question).where(Question.extraction_method == extraction_method)
    )

    payload = {
        "title": seed.title,
        "body": seed.body,
        "canonical_solution": seed.canonical_solution,
        "short_answer": seed.short_answer,
        "difficulty": seed.difficulty,
        "estimated_time_seconds": seed.estimated_time_seconds,
        "topic_id": parent_topic.id,
        "subtopic_id": subtopic.id if subtopic is not None else None,
        "company_hint": seed.company_hint,
        "expected_solution_pattern": seed.expected_solution_pattern,
        "common_mistakes": list(seed.common_mistakes) or None,
        "prerequisites": list(seed.prerequisites) or None,
        "status": seed.status,
        "source_attribution": "hand-authored MVP seed",
        "extraction_method": extraction_method,
    }

    if question is None:
        question = Question(**payload)
        session.add(question)
    else:
        for field, value in payload.items():
            setattr(question, field, value)

    apply_question_fingerprints(question)
    session.flush()
    _sync_question_tags(session, question=question, seed=seed, topics_by_slug=topics_by_slug)


def _upsert_flashcard(
    session: Session,
    seed: FlashcardSeed,
    topics_by_slug: dict[str, Topic],
) -> None:
    topic = topics_by_slug.get(seed.topic_slug)
    if topic is None:
        msg = f"Missing topic slug '{seed.topic_slug}' for flashcard seed {seed.seed_key}"
        raise ValueError(msg)

    source_id = flashcard_source_id(seed.seed_key)
    flashcard = session.scalar(select(Flashcard).where(Flashcard.source_id == source_id))
    payload = {
        "front": seed.front,
        "back": seed.back,
        "topic_id": topic.id,
        "source_id": source_id,
        "difficulty": seed.difficulty,
    }

    if flashcard is None:
        session.add(Flashcard(**payload))
    else:
        for field, value in payload.items():
            setattr(flashcard, field, value)


def seed_mvp_content(session: Session) -> MvpContentSummary:
    topics_by_slug = _load_topics_by_slug(session)
    if not topics_by_slug:
        msg = "Topic hierarchy must be seeded before MVP content."
        raise RuntimeError(msg)

    counts = {
        "probability": 0,
        "mental_math": 0,
        "coding": 0,
        "finance": 0,
        "market_game": 0,
    }

    for seed in ALL_MVP_QUESTIONS:
        _upsert_question(session, seed, topics_by_slug)
        if seed.seed_key.startswith("prob-"):
            counts["probability"] += 1
        elif seed.seed_key.startswith("mm-"):
            counts["mental_math"] += 1
        elif seed.seed_key.startswith("code-"):
            counts["coding"] += 1
        elif seed.seed_key.startswith("fin-"):
            counts["finance"] += 1
        elif seed.seed_key.startswith("game-"):
            counts["market_game"] += 1

    for flashcard_seed in ALL_MVP_FLASHCARDS:
        _upsert_flashcard(session, flashcard_seed, topics_by_slug)

    session.commit()
    tag_count = len(session.scalars(select(Tag)).all())
    return MvpContentSummary(
        probability_questions=counts["probability"],
        mental_math_questions=counts["mental_math"],
        coding_questions=counts["coding"],
        finance_questions=counts["finance"],
        market_game_questions=counts["market_game"],
        flashcards=len(ALL_MVP_FLASHCARDS),
        tags=tag_count,
    )


def main() -> None:
    session = get_session_factory()()
    try:
        summary = seed_mvp_content(session)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(
        "Seeded MVP content:",
        f"{summary.probability_questions} probability,",
        f"{summary.mental_math_questions} mental math,",
        f"{summary.coding_questions} coding,",
        f"{summary.finance_questions} finance,",
        f"{summary.market_game_questions} market games,",
        f"{summary.flashcards} flashcards,",
        f"{summary.tags} tags",
        f"({summary.total} questions).",
    )


if __name__ == "__main__":
    main()
