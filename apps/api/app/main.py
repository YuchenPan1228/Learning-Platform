from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.db import get_engine
from app.routers import health


@asynccontextmanager
async def lifespan(_: FastAPI):
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
    application.state.settings = settings
    return application


app = create_app()
