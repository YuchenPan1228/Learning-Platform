from fastapi import APIRouter

from app.dependencies import SessionDep
from app.schemas.study_plan import DailyStudyPlanRead
from app.services.study_planner import build_daily_study_plan

router = APIRouter(prefix="/study-plan", tags=["study-plan"])


@router.get("")
def read_daily_study_plan(session: SessionDep) -> DailyStudyPlanRead:
    return build_daily_study_plan(session)
