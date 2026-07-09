from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import ContentStatus, Difficulty

if TYPE_CHECKING:
    from app.models.attempt import Attempt
    from app.models.tag import QuestionTag
    from app.models.topic import Topic


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    short_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[Difficulty] = mapped_column(
        SAEnum(Difficulty, name="difficulty"),
        nullable=False,
        index=True,
    )
    estimated_time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    source_license: Mapped[str | None] = mapped_column(String(120), nullable=True)
    extraction_method: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    generated_from_id: Mapped[int | None] = mapped_column(
        ForeignKey("questions.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_attribution: Mapped[str | None] = mapped_column(Text, nullable=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subtopic_id: Mapped[int | None] = mapped_column(
        ForeignKey("topics.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    company_hint: Mapped[str | None] = mapped_column(String(200), nullable=True)
    frequency_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_solution_pattern: Mapped[str | None] = mapped_column(Text, nullable=True)
    common_mistakes: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    prerequisites: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    related_question_ids: Mapped[list[int] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[ContentStatus] = mapped_column(
        SAEnum(ContentStatus, name="content_status"),
        default=ContentStatus.DRAFT,
        nullable=False,
        index=True,
    )

    topic: Mapped[Topic] = relationship(
        back_populates="questions",
        foreign_keys=[topic_id],
    )
    subtopic: Mapped[Topic | None] = relationship(
        back_populates="subtopic_questions",
        foreign_keys=[subtopic_id],
    )
    generated_from: Mapped[Question | None] = relationship(
        remote_side="Question.id",
        foreign_keys=[generated_from_id],
    )
    question_tags: Mapped[list[QuestionTag]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )
    attempts: Mapped[list[Attempt]] = relationship(back_populates="question")
