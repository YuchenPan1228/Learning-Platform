from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Load example defaults first; `.env` must win on key collisions.
        env_file=(REPO_ROOT / ".env.example", REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="local", alias="APP_ENV")
    api_host: str = Field(default="127.0.0.1", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:3000",
            "http://localhost:3000",
        ],
        alias="CORS_ORIGINS",
    )
    database_url: str = Field(
        default="postgresql+psycopg://quant_prep:quant_prep@localhost:5432/quant_prep",
        alias="DATABASE_URL",
    )
    ai_provider: str = Field(default="ollama", alias="AI_PROVIDER")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_chat_model: str = Field(default="", alias="OLLAMA_CHAT_MODEL")
    ollama_model_general: str = Field(default="", alias="OLLAMA_MODEL_GENERAL")
    # Deprecated alias for OLLAMA_MODEL_GENERAL (still accepted).
    ollama_model_tutor: str = Field(default="", alias="OLLAMA_MODEL_TUTOR")
    ollama_model_coding: str = Field(default="", alias="OLLAMA_MODEL_CODING")
    ollama_model_reasoning: str = Field(default="", alias="OLLAMA_MODEL_REASONING")
    ollama_embedding_model: str = Field(default="", alias="OLLAMA_EMBEDDING_MODEL")
    ollama_request_timeout_seconds: float = Field(
        default=120.0,
        alias="OLLAMA_REQUEST_TIMEOUT_SECONDS",
        gt=0,
    )
    ai_json_repair_attempts: int = Field(
        default=0,
        alias="AI_JSON_REPAIR_ATTEMPTS",
        ge=0,
    )
    ai_warmup_on_startup: bool = Field(default=True, alias="AI_WARMUP_ON_STARTUP")
    ai_warmup_specialized_models: bool = Field(
        default=False,
        alias="AI_WARMUP_SPECIALIZED_MODELS",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
