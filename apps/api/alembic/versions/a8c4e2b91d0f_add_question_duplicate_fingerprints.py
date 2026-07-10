"""add question duplicate fingerprints

Revision ID: a8c4e2b91d0f
Revises: f3295c0fb36c
Create Date: 2026-07-10 17:55:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dedup.fingerprints import apply_question_fingerprints
from app.models.question import Question

# revision identifiers, used by Alembic.
revision: str = "a8c4e2b91d0f"
down_revision: Union[str, Sequence[str], None] = "f3295c0fb36c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("raw_text_hash", sa.String(length=64), nullable=True))
    op.add_column(
        "questions",
        sa.Column("normalized_text_hash", sa.String(length=64), nullable=True),
    )
    op.add_column("questions", sa.Column("normalized_text", sa.Text(), nullable=True))
    op.create_index(
        op.f("ix_questions_raw_text_hash"),
        "questions",
        ["raw_text_hash"],
        unique=False,
    )
    op.create_index(
        op.f("ix_questions_normalized_text_hash"),
        "questions",
        ["normalized_text_hash"],
        unique=False,
    )

    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        questions = session.scalars(select(Question)).all()
        for question in questions:
            apply_question_fingerprints(question)
        session.commit()
    finally:
        session.close()


def downgrade() -> None:
    op.drop_index(op.f("ix_questions_normalized_text_hash"), table_name="questions")
    op.drop_index(op.f("ix_questions_raw_text_hash"), table_name="questions")
    op.drop_column("questions", "normalized_text")
    op.drop_column("questions", "normalized_text_hash")
    op.drop_column("questions", "raw_text_hash")
