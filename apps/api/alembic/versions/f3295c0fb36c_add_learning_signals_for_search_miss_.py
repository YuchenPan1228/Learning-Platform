"""add learning signals for search miss tracking

Revision ID: f3295c0fb36c
Revises: dbe3c105925e
Create Date: 2026-07-10 17:36:16.040590

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f3295c0fb36c"
down_revision: Union[str, Sequence[str], None] = "dbe3c105925e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "learning_signals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column(
            "signal_type",
            sa.Enum(
                "search_miss",
                "confusing_question_flag",
                "high_completion_rate",
                "weak_topic",
                name="learning_signal_type",
            ),
            nullable=False,
        ),
        sa.Column("topic_id", sa.Integer(), nullable=True),
        sa.Column("question_id", sa.Integer(), nullable=True),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_learning_signals_question_id"),
        "learning_signals",
        ["question_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_learning_signals_signal_type"),
        "learning_signals",
        ["signal_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_learning_signals_topic_id"),
        "learning_signals",
        ["topic_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_learning_signals_user_id"),
        "learning_signals",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_learning_signals_user_id"), table_name="learning_signals")
    op.drop_index(op.f("ix_learning_signals_topic_id"), table_name="learning_signals")
    op.drop_index(op.f("ix_learning_signals_signal_type"), table_name="learning_signals")
    op.drop_index(op.f("ix_learning_signals_question_id"), table_name="learning_signals")
    op.drop_table("learning_signals")
    op.execute("DROP TYPE IF EXISTS learning_signal_type")
