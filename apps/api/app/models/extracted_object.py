from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import ContentStatus, ExtractedObjectType, enum_values

if TYPE_CHECKING:
    from app.models.resource import Resource
    from app.models.topic_job import TopicJob


class ExtractedObject(Base, TimestampMixin):
    __tablename__ = "extracted_objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_id: Mapped[int | None] = mapped_column(
        ForeignKey("resources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    topic_job_id: Mapped[int | None] = mapped_column(
        ForeignKey("topic_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    object_type: Mapped[ExtractedObjectType] = mapped_column(
        SAEnum(
            ExtractedObjectType,
            name="extracted_object_type",
            values_callable=enum_values,
        ),
        nullable=False,
        index=True,
    )
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Nullable integer without FK: DuplicateCluster is deferred until Phase 6 (QP-049).
    duplicate_cluster_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
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
    extraction_method: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(120), nullable=True)

    resource: Mapped[Resource | None] = relationship(back_populates="extracted_objects")
    topic_job: Mapped[TopicJob | None] = relationship(back_populates="extracted_objects")
