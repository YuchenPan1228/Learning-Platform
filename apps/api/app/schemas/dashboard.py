from pydantic import BaseModel

from app.schemas.study_plan import DailyStudyPlanRead


class TopicMasteryRead(BaseModel):
    topic_id: int
    slug: str
    name: str
    mastery_score: float
    attempts_count: int
    solved_count: int
    total_questions: int


class WeakPrerequisiteRead(BaseModel):
    concept_slug: str
    concept_name: str
    prerequisite_slug: str
    prerequisite_name: str
    prerequisite_mastery_score: float


class DashboardRead(BaseModel):
    user_id: str
    topic_mastery: list[TopicMasteryRead]
    subtopic_mastery: list[TopicMasteryRead]
    weak_prerequisites: list[WeakPrerequisiteRead]
    daily_plan: DailyStudyPlanRead
