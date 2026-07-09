from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.concept import Concept


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_user_level: Mapped[str | None] = mapped_column(String(120), nullable=True)
    estimated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    steps: Mapped[list[LearningPathStep]] = relationship(
        back_populates="learning_path",
        cascade="all, delete-orphan",
        order_by="LearningPathStep.order_index",
    )


class LearningPathStep(Base):
    __tablename__ = "learning_path_steps"
    __table_args__ = (
        UniqueConstraint(
            "learning_path_id",
            "order_index",
            name="uq_learning_path_steps_path_order",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    learning_path_id: Mapped[int] = mapped_column(
        ForeignKey("learning_paths.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    concept_id: Mapped[int] = mapped_column(
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    required_mastery_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    learning_path: Mapped[LearningPath] = relationship(back_populates="steps")
    concept: Mapped[Concept] = relationship(back_populates="learning_path_steps")
