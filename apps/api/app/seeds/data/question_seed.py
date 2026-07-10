from dataclasses import dataclass

from app.models.enums import ContentStatus, Difficulty


@dataclass(frozen=True, slots=True)
class QuestionSeed:
    seed_key: str
    title: str
    body: str
    topic_slug: str
    difficulty: Difficulty
    subtopic_slug: str | None = None
    canonical_solution: str | None = None
    short_answer: str | None = None
    estimated_time_seconds: int | None = None
    company_hint: str | None = None
    common_mistakes: tuple[str, ...] = ()
    prerequisites: tuple[str, ...] = ()
    expected_solution_pattern: str | None = None
    status: ContentStatus = ContentStatus.APPROVED


def seed_extraction_method(seed_key: str) -> str:
    return f"hand_seed:{seed_key}"
