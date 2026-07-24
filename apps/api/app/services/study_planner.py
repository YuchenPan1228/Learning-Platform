from collections import defaultdict
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.concept import Concept, ConceptEdge
from app.models.constants import LOCAL_USER_ID
from app.models.enums import ConceptEdgeRelationshipType
from app.models.flashcard import Flashcard
from app.models.topic import Topic
from app.models.user_flashcard_progress import UserFlashcardProgress
from app.schemas.study_plan import (
    DailyStudyPlanRead,
    StudyPlanItemKind,
    StudyPlanItemRead,
)
from app.services.progress import get_topic_progress_stats

TARGET_MINUTES = 90
MAX_ITEMS = 5
MAX_FLASHCARD_ITEMS = 2
MAX_PREREQ_ITEMS = 1
MAX_PRACTICE_ITEMS = 2
WEAK_MASTERY_THRESHOLD = 50.0
MINUTES_PER_FLASHCARD = 1
FLASHCARD_BLOCK_CAP = 15
PREREQUISITE_BLOCK_MINUTES = 20
PRACTICE_BLOCK_MINUTES = 20


def _remaining(budget_used: int) -> int:
    return max(TARGET_MINUTES - budget_used, 0)


def _due_flashcard_items(
    session: Session,
    *,
    budget_used: int,
    max_items: int,
) -> list[StudyPlanItemRead]:
    remaining = _remaining(budget_used)
    if remaining <= 0 or max_items <= 0:
        return []

    now = datetime.now(UTC)
    progress_rows = session.scalars(
        select(UserFlashcardProgress).where(UserFlashcardProgress.user_id == LOCAL_USER_ID),
    ).all()
    progress_by_id = {row.flashcard_id: row for row in progress_rows}

    flashcards = (
        session.scalars(
            select(Flashcard).options(joinedload(Flashcard.topic)).order_by(Flashcard.id),
        )
        .unique()
        .all()
    )

    due_by_topic: dict[int, list[Flashcard]] = defaultdict(list)
    for flashcard in flashcards:
        progress = progress_by_id.get(flashcard.id)
        if progress is None or progress.next_review_at <= now:
            due_by_topic[flashcard.topic_id].append(flashcard)

    items: list[StudyPlanItemRead] = []
    # Prefer topics with earliest next_review_at, then more due cards.
    ranked_topics = sorted(
        due_by_topic.items(),
        key=lambda entry: (
            min(
                (
                    progress_by_id[card.id].next_review_at
                    for card in entry[1]
                    if card.id in progress_by_id
                ),
                default=now,
            ),
            -len(entry[1]),
            entry[0],
        ),
    )

    for _topic_id, cards in ranked_topics:
        if len(items) >= max_items or _remaining(budget_used) <= 0:
            break
        topic = cards[0].topic
        duration = min(
            len(cards) * MINUTES_PER_FLASHCARD,
            FLASHCARD_BLOCK_CAP,
            _remaining(budget_used),
        )
        if duration <= 0:
            break
        items.append(
            StudyPlanItemRead(
                kind=StudyPlanItemKind.FLASHCARD_REVIEW,
                title=f"{topic.name} flashcards",
                description=f"Review {len(cards)} due card{'s' if len(cards) != 1 else ''}",
                duration_minutes=duration,
                href=f"/flashcards?topic={topic.slug}",
                topic_slug=topic.slug,
            ),
        )
        budget_used += duration
    return items


def _prerequisite_items(
    session: Session,
    *,
    budget_used: int,
    max_items: int,
) -> list[StudyPlanItemRead]:
    remaining = _remaining(budget_used)
    if remaining <= 0 or max_items <= 0:
        return []

    topic_stats = get_topic_progress_stats(session)
    edges = (
        session.scalars(
            select(ConceptEdge)
            .where(ConceptEdge.relationship_type == ConceptEdgeRelationshipType.REQUIRES)
            .options(
                joinedload(ConceptEdge.source_concept),
                joinedload(ConceptEdge.target_concept),
            ),
        )
        .unique()
        .all()
    )

    candidates: list[tuple[float, Concept, Concept]] = []
    seen_prereq_ids: set[int] = set()
    for edge in edges:
        prereq = edge.target_concept
        if prereq.id in seen_prereq_ids:
            continue
        stats = topic_stats.get(prereq.topic_id)
        score = stats.mastery_score if stats is not None else 0.0
        if score >= WEAK_MASTERY_THRESHOLD:
            continue
        seen_prereq_ids.add(prereq.id)
        candidates.append((score, edge.source_concept, prereq))

    candidates.sort(key=lambda item: (item[0], item[2].id))
    items: list[StudyPlanItemRead] = []
    for score, dependent, prereq in candidates:
        if len(items) >= max_items or _remaining(budget_used) < PREREQUISITE_BLOCK_MINUTES:
            break
        duration = min(PREREQUISITE_BLOCK_MINUTES, _remaining(budget_used))
        items.append(
            StudyPlanItemRead(
                kind=StudyPlanItemKind.PREREQUISITE_REPAIR,
                title=prereq.name,
                description=(f"Prerequisite repair before {dependent.name} (mastery {score:.0f}%)"),
                duration_minutes=duration,
                href=f"/concepts/{prereq.slug}",
                concept_slug=prereq.slug,
            ),
        )
        budget_used += duration
    return items


def _practice_items(
    session: Session,
    *,
    budget_used: int,
    max_items: int,
) -> list[StudyPlanItemRead]:
    remaining = _remaining(budget_used)
    if remaining <= 0 or max_items <= 0:
        return []

    topic_stats = get_topic_progress_stats(session)
    subtopics = session.scalars(
        select(Topic)
        .where(Topic.parent_topic_id.is_not(None))
        .order_by(Topic.order_index, Topic.id),
    ).all()

    ranked = sorted(
        subtopics,
        key=lambda topic: (
            topic_stats[topic.id].mastery_score if topic.id in topic_stats else 0.0,
            -(topic_stats[topic.id].total_questions if topic.id in topic_stats else 0),
            topic.id,
        ),
    )

    items: list[StudyPlanItemRead] = []
    for topic in ranked:
        if len(items) >= max_items or _remaining(budget_used) < 10:
            break
        stats = topic_stats.get(topic.id)
        if stats is None or stats.total_questions == 0:
            continue
        if stats.mastery_score >= WEAK_MASTERY_THRESHOLD and stats.solved_count > 0:
            continue
        unsolved = max(stats.total_questions - stats.solved_count, 1)
        duration = min(PRACTICE_BLOCK_MINUTES, max(10, unsolved * 3), _remaining(budget_used))
        items.append(
            StudyPlanItemRead(
                kind=StudyPlanItemKind.PRACTICE,
                title=topic.name,
                description=(
                    f"{unsolved} unsolved question{'s' if unsolved != 1 else ''} "
                    f"(mastery {stats.mastery_score:.0f}%)"
                ),
                duration_minutes=duration,
                href=f"/practice?topic={topic.slug}",
                topic_slug=topic.slug,
            ),
        )
        budget_used += duration
    return items


def _build_detail(items: list[StudyPlanItemRead]) -> str:
    if not items:
        return "No study items scheduled yet."
    counts: dict[str, int] = defaultdict(int)
    for item in items:
        key = item.topic_slug or item.concept_slug or item.kind.value
        counts[key] += item.duration_minutes
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    parts = [f"{minutes} {label}" for label, minutes in ranked]
    return ", ".join(parts) + "."


def build_daily_study_plan(session: Session) -> DailyStudyPlanRead:
    """Deterministic daily plan from due reviews, weak prerequisites, and practice."""
    items: list[StudyPlanItemRead] = []
    budget_used = 0

    flashcard_items = _due_flashcard_items(
        session,
        budget_used=budget_used,
        max_items=MAX_FLASHCARD_ITEMS,
    )
    items.extend(flashcard_items)
    budget_used += sum(item.duration_minutes for item in flashcard_items)

    remaining_slots = MAX_ITEMS - len(items)
    if remaining_slots > 0:
        prereq_items = _prerequisite_items(
            session,
            budget_used=budget_used,
            max_items=min(MAX_PREREQ_ITEMS, remaining_slots),
        )
        items.extend(prereq_items)
        budget_used += sum(item.duration_minutes for item in prereq_items)

    remaining_slots = MAX_ITEMS - len(items)
    if remaining_slots > 0:
        practice_items = _practice_items(
            session,
            budget_used=budget_used,
            max_items=min(MAX_PRACTICE_ITEMS, remaining_slots),
        )
        items.extend(practice_items)

    items = items[:MAX_ITEMS]
    total_minutes = sum(item.duration_minutes for item in items)
    return DailyStudyPlanRead(
        user_id=LOCAL_USER_ID,
        generated_at=datetime.now(UTC),
        target_minutes=TARGET_MINUTES,
        total_minutes=total_minutes,
        summary=f"{total_minutes} min plan",
        detail=_build_detail(items),
        items=items,
    )
