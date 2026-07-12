from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.constants import LOCAL_USER_ID
from app.models.enums import ManualQuestionProgressStatus, enum_values

if TYPE_CHECKING:
    from app.models.question import Question


class UserQuestionProgress(Base):
    __tablename__ = "user_question_progress"

    user_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=LOCAL_USER_ID,
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    manual_status: Mapped[ManualQuestionProgressStatus] = mapped_column(
        SAEnum(
            ManualQuestionProgressStatus,
            name="manual_question_progress_status",
            values_callable=enum_values,
        ),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    question: Mapped[Question] = relationship()
