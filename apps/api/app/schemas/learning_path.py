from pydantic import BaseModel, ConfigDict


class LearningPathSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: str | None
    target_user_level: str | None
    estimated_hours: float | None
    step_count: int


class LearningPathStepRead(BaseModel):
    order_index: int
    concept_id: int
    concept_slug: str
    concept_name: str
    required_mastery_score: float | None


class LearningPathDetailRead(LearningPathSummaryRead):
    steps: list[LearningPathStepRead]
