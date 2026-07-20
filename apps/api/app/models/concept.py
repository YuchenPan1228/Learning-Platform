from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ConceptEdgeRelationshipType, enum_values

if TYPE_CHECKING:
    from app.models.learning_path import LearningPathStep
    from app.models.topic import Topic


class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    formula: Mapped[str | None] = mapped_column(Text, nullable=True)
    intuition: Mapped[str | None] = mapped_column(Text, nullable=True)
    worked_example: Mapped[str | None] = mapped_column(Text, nullable=True)
    common_mistakes: Mapped[str | None] = mapped_column(Text, nullable=True)
    interview_tips: Mapped[str | None] = mapped_column(Text, nullable=True)
    prerequisites: Mapped[str | None] = mapped_column(Text, nullable=True)

    topic: Mapped[Topic] = relationship(back_populates="concepts")
    outgoing_edges: Mapped[list[ConceptEdge]] = relationship(
        back_populates="source_concept",
        foreign_keys="ConceptEdge.source_concept_id",
        cascade="all, delete-orphan",
    )
    incoming_edges: Mapped[list[ConceptEdge]] = relationship(
        back_populates="target_concept",
        foreign_keys="ConceptEdge.target_concept_id",
        cascade="all, delete-orphan",
    )
    learning_path_steps: Mapped[list[LearningPathStep]] = relationship(back_populates="concept")


class ConceptEdge(Base):
    __tablename__ = "concept_edges"
    __table_args__ = (
        UniqueConstraint(
            "source_concept_id",
            "target_concept_id",
            "relationship_type",
            name="uq_concept_edges_source_target_relationship",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_concept_id: Mapped[int] = mapped_column(
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_concept_id: Mapped[int] = mapped_column(
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relationship_type: Mapped[ConceptEdgeRelationshipType] = mapped_column(
        SAEnum(
            ConceptEdgeRelationshipType,
            name="concept_edge_relationship_type",
            values_callable=enum_values,
        ),
        nullable=False,
        index=True,
    )
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    source_concept: Mapped[Concept] = relationship(
        back_populates="outgoing_edges",
        foreign_keys=[source_concept_id],
    )
    target_concept: Mapped[Concept] = relationship(
        back_populates="incoming_edges",
        foreign_keys=[target_concept_id],
    )
