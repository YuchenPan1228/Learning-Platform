from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import TagCategory

if TYPE_CHECKING:
    from app.models.question import Question


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[TagCategory] = mapped_column(
        SAEnum(TagCategory, name="tag_category"),
        nullable=False,
        index=True,
    )

    question_tags: Mapped[list[QuestionTag]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan",
    )


class QuestionTag(Base):
    __tablename__ = "question_tags"

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    question: Mapped[Question] = relationship(back_populates="question_tags")
    tag: Mapped[Tag] = relationship(back_populates="question_tags")
