from fastapi import APIRouter

from app.dependencies import SessionDep
from app.schemas.analytics import LearningAnalyticsRead
from app.services.analytics import get_learning_analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("")
def read_learning_analytics(session: SessionDep) -> LearningAnalyticsRead:
    return get_learning_analytics(session)
