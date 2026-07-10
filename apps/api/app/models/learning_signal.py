from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.constants import LOCAL_USER_ID
from app.models.enums import LearningSignalType, enum_values

if TYPE_CHECKING:
    from app.models.question import Question
    from app.models.topic import Topic


class LearningSignal(Base):
    __tablename__ = "learning_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(64),
        default=LOCAL_USER_ID,
        nullable=False,
        index=True,
    )
    signal_type: Mapped[LearningSignalType] = mapped_column(
        SAEnum(
            LearningSignalType,
            name="learning_signal_type",
            values_callable=enum_values,
        ),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[int | None] = mapped_column(
        ForeignKey("topics.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    question_id: Mapped[int | None] = mapped_column(
        ForeignKey("questions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    topic: Mapped[Topic | None] = relationship()
    question: Mapped[Question | None] = relationship()
