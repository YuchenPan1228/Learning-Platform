from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.db import get_engine
from app.routers import (
    concepts,
    dashboard,
    flashcards,
    health,
    learning_paths,
    questions,
    search,
    topics,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    get_engine()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Quant Prep API",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.include_router(health.router)
    application.include_router(dashboard.router)
    application.include_router(topics.router)
    application.include_router(concepts.router)
    application.include_router(questions.router)
    application.include_router(flashcards.router)
    application.include_router(learning_paths.router)
    application.include_router(search.router)
    application.state.settings = settings
    return application


app = create_app()
