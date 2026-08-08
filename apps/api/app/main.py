import logging
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai.warmup import warmup_configured_models
from app.config import get_settings
from app.db import get_engine
from app.routers import (
    admin_concepts,
    admin_import,
    admin_questions,
    admin_review,
    admin_topic_jobs,
    analytics,
    attempts,
    concepts,
    dashboard,
    health,
    mastery,
    questions,
    search,
    study_plan,
    tags,
    topics,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    get_engine()
    settings = get_settings()
    # Skip warmup under pytest to avoid Ollama calls and shared-thread teardown races.
    if settings.ai_warmup_on_startup and settings.app_env != "test":
        thread = threading.Thread(
            target=_safe_warmup,
            name="ai-warmup",
            daemon=True,
        )
        thread.start()
    yield


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
    application.include_router(mastery.router)
    application.include_router(study_plan.router)
    application.include_router(analytics.router)
    application.include_router(search.router)
    application.include_router(admin_import.router)
    application.include_router(admin_review.router)
    application.include_router(admin_topic_jobs.router)
    application.include_router(admin_concepts.router)
    application.include_router(admin_questions.router)
    # Flashcard learner + admin APIs are paused product-side; routers remain in repo.
    application.state.settings = settings
    return application


app = create_app()
