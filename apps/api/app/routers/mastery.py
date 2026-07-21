from fastapi import APIRouter

from app.dependencies import SessionDep
from app.schemas.mastery import MasteryRead
from app.services.mastery import get_mastery

router = APIRouter(prefix="/mastery", tags=["mastery"])


@router.get("")
def read_mastery(session: SessionDep) -> MasteryRead:
    return get_mastery(session)
