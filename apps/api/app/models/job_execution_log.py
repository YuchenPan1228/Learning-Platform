from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import JobExecutionStage, JobExecutionStatus, enum_values

if TYPE_CHECKING:
    from app.models.ai_usage_log import AIUsageLog
    from app.models.topic_job import TopicJob


class JobExecutionLog(Base):
    __tablename__ = "job_execution_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_job_id: Mapped[int] = mapped_column(
        ForeignKey("topic_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage: Mapped[JobExecutionStage] = mapped_column(
        SAEnum(
            JobExecutionStage,
            name="job_execution_stage",
            values_callable=enum_values,
        ),
        nullable=False,
        index=True,
    )
    status: Mapped[JobExecutionStatus] = mapped_column(
        SAEnum(
            JobExecutionStatus,
            name="job_execution_status",
            values_callable=enum_values,
        ),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    runtime_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    ai_usage_log_id: Mapped[int | None] = mapped_column(
        ForeignKey("ai_usage_logs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    topic_job: Mapped[TopicJob] = relationship(back_populates="execution_logs")
    ai_usage_log: Mapped[AIUsageLog | None] = relationship()
