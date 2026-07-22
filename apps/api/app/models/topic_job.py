from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import TopicJobCreatedBy, TopicJobStatus, enum_values

if TYPE_CHECKING:
    from app.models.concept import Concept
    from app.models.extracted_object import ExtractedObject
    from app.models.job_execution_log import JobExecutionLog
    from app.models.topic import Topic


class TopicJob(Base, TimestampMixin):
    __tablename__ = "topic_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    concept_id: Mapped[int | None] = mapped_column(
        ForeignKey("concepts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    target_source_count: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    status: Mapped[TopicJobStatus] = mapped_column(
        SAEnum(
            TopicJobStatus,
            name="topic_job_status",
            values_callable=enum_values,
        ),
        default=TopicJobStatus.QUEUED,
        nullable=False,
        index=True,
    )
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    created_by: Mapped[TopicJobCreatedBy] = mapped_column(
        SAEnum(
            TopicJobCreatedBy,
            name="topic_job_created_by",
            values_callable=enum_values,
        ),
        default=TopicJobCreatedBy.ADMIN,
        nullable=False,
        index=True,
    )

    topic: Mapped[Topic] = relationship()
    concept: Mapped[Concept | None] = relationship()
    extracted_objects: Mapped[list[ExtractedObject]] = relationship(
        back_populates="topic_job",
    )
    execution_logs: Mapped[list[JobExecutionLog]] = relationship(
        back_populates="topic_job",
        cascade="all, delete-orphan",
    )
