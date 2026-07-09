from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.constants import LOCAL_USER_ID

if TYPE_CHECKING:
    from app.models.topic import Topic


class UserTopicMastery(Base):
    __tablename__ = "user_topic_mastery"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=LOCAL_USER_ID)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True,
    )
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_practiced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    topic: Mapped[Topic] = relationship(back_populates="user_masteries")
