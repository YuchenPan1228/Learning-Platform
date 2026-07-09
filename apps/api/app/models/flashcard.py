from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import Difficulty

if TYPE_CHECKING:
    from app.models.topic import Topic


class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[Difficulty | None] = mapped_column(
        SAEnum(Difficulty, name="difficulty", create_type=False),
        nullable=True,
    )

    topic: Mapped[Topic] = relationship(back_populates="flashcards")
