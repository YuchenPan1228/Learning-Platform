from collections.abc import AsyncIterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai.warmup import warmup_configured_models
from app.config import get_settings
from app.db import get_engine
from app.routers import (
    attempts,
    concepts,
    dashboard,
    flashcards,
    health,
    learning_paths,
    questions,
    search,
    tags,
    topics,
)

logger = logging.getLogger(__name__)
_warmup_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ai-warmup")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    get_engine()
    settings = get_settings()
    if settings.ai_warmup_on_startup:
        _warmup_executor.submit(_safe_warmup)
    yield
    _warmup_executor.shutdown(wait=False, cancel_futures=True)


def _safe_warmup() -> None:
    try:
        warmup_configured_models()
    except Exception:
        logger.exception("AI model warmup failed")


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Quant Prep API",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health.router)
    application.include_router(dashboard.router)
    application.include_router(topics.router)
    application.include_router(concepts.router)
    application.include_router(questions.router)
    application.include_router(attempts.router)
    application.include_router(tags.router)
    application.include_router(flashcards.router)
    application.include_router(learning_paths.router)
    application.include_router(search.router)
    application.state.settings = settings
    return application


app = create_app()
