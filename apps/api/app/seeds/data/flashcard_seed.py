from dataclasses import dataclass

from app.models.enums import Difficulty


@dataclass(frozen=True, slots=True)
class FlashcardSeed:
    seed_key: str
    front: str
    back: str
    topic_slug: str
    difficulty: Difficulty | None = None


def flashcard_source_id(seed_key: str) -> int:
    suffix = seed_key.rsplit("-", maxsplit=1)[-1]
    return 900_000 + int(suffix)
