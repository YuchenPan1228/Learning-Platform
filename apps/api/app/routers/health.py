from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.db import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, object]:
    settings = get_settings()
    database_status = "ok"

    try:
        check_database_connection()
    except SQLAlchemyError:
        database_status = "unavailable"

    status = "ok" if database_status == "ok" else "degraded"

    return {
        "status": status,
        "app_env": settings.app_env,
        "database": database_status,
    }
