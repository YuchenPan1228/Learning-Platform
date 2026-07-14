from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.ai.factory import get_ai_provider
from app.ai.provider import AIProvider
from app.db import get_db

SessionDep = Annotated[Session, Depends(get_db)]
AIProviderDep = Annotated[AIProvider, Depends(get_ai_provider)]
