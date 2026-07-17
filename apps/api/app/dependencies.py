from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.ai.factory import get_ai_provider as get_base_ai_provider
from app.ai.provider import AIProvider
from app.ai.tracking import TrackingAIProvider
from app.db import get_db

SessionDep = Annotated[Session, Depends(get_db)]


def get_ai_provider(session: SessionDep) -> AIProvider:
    return TrackingAIProvider(get_base_ai_provider(), session)


AIProviderDep = Annotated[AIProvider, Depends(get_ai_provider)]
