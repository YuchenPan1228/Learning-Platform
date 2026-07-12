from fastapi import APIRouter

from app.dependencies import SessionDep
from app.schemas.dashboard import DashboardRead
from app.services.dashboard import get_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def read_dashboard(session: SessionDep) -> DashboardRead:
    return get_dashboard(session)
