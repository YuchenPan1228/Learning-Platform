from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.dependencies import SessionDep
from app.models.learning_path import LearningPath, LearningPathStep
from app.schemas.learning_path import (
    LearningPathDetailRead,
    LearningPathStepRead,
    LearningPathSummaryRead,
)

router = APIRouter(prefix="/learning-paths", tags=["learning-paths"])


def _learning_path_summary(
    learning_path: LearningPath,
    step_count: int,
) -> LearningPathSummaryRead:
    return LearningPathSummaryRead(
        id=learning_path.id,
        slug=learning_path.slug,
        name=learning_path.name,
        description=learning_path.description,
        target_user_level=learning_path.target_user_level,
        estimated_hours=learning_path.estimated_hours,
        step_count=step_count,
    )


def _learning_path_detail(learning_path: LearningPath) -> LearningPathDetailRead:
    steps = [
        LearningPathStepRead(
            order_index=step.order_index,
            concept_id=step.concept_id,
            concept_slug=step.concept.slug,
            concept_name=step.concept.name,
            required_mastery_score=step.required_mastery_score,
        )
        for step in learning_path.steps
    ]
    return LearningPathDetailRead(
        **_learning_path_summary(learning_path, step_count=len(steps)).model_dump(),
        steps=steps,
    )


@router.get("")
def list_learning_paths(session: SessionDep) -> list[LearningPathSummaryRead]:
    rows = session.execute(
        select(LearningPathStep.learning_path_id, func.count()).group_by(
            LearningPathStep.learning_path_id
        ),
    ).all()
    step_counts: dict[int, int] = {path_id: count for path_id, count in rows}
    learning_paths = session.scalars(
        select(LearningPath).order_by(LearningPath.name, LearningPath.id),
    ).all()
    return [
        _learning_path_summary(learning_path, step_counts.get(learning_path.id, 0))
        for learning_path in learning_paths
    ]


@router.get("/{slug}")
def get_learning_path(slug: str, session: SessionDep) -> LearningPathDetailRead:
    learning_path = session.scalar(
        select(LearningPath)
        .where(LearningPath.slug == slug)
        .options(
            selectinload(LearningPath.steps).joinedload(LearningPathStep.concept),
        ),
    )
    if learning_path is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return _learning_path_detail(learning_path)
