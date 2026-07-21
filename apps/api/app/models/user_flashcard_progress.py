from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.constants import LOCAL_USER_ID
from app.models.enums import FlashcardReviewRating, enum_values

if TYPE_CHECKING:
    from app.models.flashcard import Flashcard


class UserFlashcardProgress(Base):
    __tablename__ = "user_flashcard_progress"

    user_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=LOCAL_USER_ID,
    )
    flashcard_id: Mapped[int] = mapped_column(
        ForeignKey("flashcards.id", ondelete="CASCADE"),
        primary_key=True,
    )
    interval_days: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_review_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_rating: Mapped[FlashcardReviewRating | None] = mapped_column(
        SAEnum(
            FlashcardReviewRating,
            name="flashcard_review_rating",
            values_callable=enum_values,
        ),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    flashcard: Mapped[Flashcard] = relationship()
