"""add user question progress overrides

Revision ID: b7e1f4c82a90
Revises: a8c4e2b91d0f
Create Date: 2026-07-12 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b7e1f4c82a90"
down_revision: Union[str, Sequence[str], None] = "a8c4e2b91d0f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_question_progress",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column(
            "manual_status",
            sa.Enum("solved", "not_attempted", name="manual_question_progress_status"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "question_id"),
    )
    op.create_index(
        op.f("ix_user_question_progress_question_id"),
        "user_question_progress",
        ["question_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_user_question_progress_question_id"),
        table_name="user_question_progress",
    )
    op.drop_table("user_question_progress")
    op.execute("DROP TYPE IF EXISTS manual_question_progress_status")
