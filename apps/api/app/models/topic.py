from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.concept import Concept
    from app.models.flashcard import Flashcard
    from app.models.question import Question
    from app.models.user_topic_mastery import UserTopicMastery


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_topic_id: Mapped[int | None] = mapped_column(
        ForeignKey("topics.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    parent_topic: Mapped[Topic | None] = relationship(
        "Topic",
        remote_side="Topic.id",
        back_populates="subtopics",
    )
    subtopics: Mapped[list[Topic]] = relationship("Topic", back_populates="parent_topic")
    concepts: Mapped[list[Concept]] = relationship(back_populates="topic")
    questions: Mapped[list[Question]] = relationship(
        back_populates="topic",
        foreign_keys="Question.topic_id",
    )
    subtopic_questions: Mapped[list[Question]] = relationship(
        back_populates="subtopic",
        foreign_keys="Question.subtopic_id",
    )
    flashcards: Mapped[list[Flashcard]] = relationship(back_populates="topic")
    user_masteries: Mapped[list[UserTopicMastery]] = relationship(back_populates="topic")
