from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import AICacheResultKind, enum_values


class AICacheEntry(Base):
    __tablename__ = "ai_cache_entries"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "model",
            "result_kind",
            "prompt_template_version",
            "prompt_hash",
            "input_object_version",
            name="uq_ai_cache_entries_lookup",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    result_kind: Mapped[AICacheResultKind] = mapped_column(
        SAEnum(
            AICacheResultKind,
            name="ai_cache_result_kind",
            values_callable=enum_values,
        ),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    prompt_template_version: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    input_object_version: Mapped[str] = mapped_column(String(64), nullable=False)
    response_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
