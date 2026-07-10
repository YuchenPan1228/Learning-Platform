from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session_factory
from app.dedup.fingerprints import apply_question_fingerprints
from app.models.question import Question
from app.models.topic import Topic
from app.seeds.data.mvp import ALL_MVP_QUESTIONS
from app.seeds.data.question_seed import QuestionSeed, seed_extraction_method


@dataclass(frozen=True, slots=True)
class MvpContentSummary:
    probability_questions: int
    mental_math_questions: int
    coding_questions: int
    finance_questions: int
    market_game_questions: int

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

    session.commit()
    return MvpContentSummary(
        probability_questions=counts["probability"],
        mental_math_questions=counts["mental_math"],
        coding_questions=counts["coding"],
        finance_questions=counts["finance"],
        market_game_questions=counts["market_game"],
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
        f"{summary.market_game_questions} market games",
        f"({summary.total} total).",
    )


if __name__ == "__main__":
    main()
