from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import ContentStatus, ResourceSourceType, enum_values

if TYPE_CHECKING:
    from app.models.extracted_object import ExtractedObject


class Resource(Base, TimestampMixin):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[ResourceSourceType] = mapped_column(
        SAEnum(
            ResourceSourceType,
            name="resource_source_type",
            values_callable=enum_values,
        ),
        nullable=False,
        index=True,
    )
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    author: Mapped[str | None] = mapped_column(String(200), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(200), nullable=True)
    license: Mapped[str | None] = mapped_column(String(120), nullable=True)
    attribution: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain_reputation_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    content_length_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    formula_density_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    code_example_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    educational_structure_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    human_review_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_text_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ContentStatus] = mapped_column(
        SAEnum(
            ContentStatus,
            name="content_status",
            create_type=False,
            values_callable=enum_values,
        ),
        default=ContentStatus.DRAFT,
        nullable=False,
        index=True,
    )

    extracted_objects: Mapped[list[ExtractedObject]] = relationship(
        back_populates="resource",
    )
