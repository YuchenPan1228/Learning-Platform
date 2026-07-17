"""add ai usage logs

Revision ID: c4d8e1a93b71
Revises: b7e1f4c82a90
Create Date: 2026-07-14 09:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c4d8e1a93b71"
down_revision: Union[str, Sequence[str], None] = "b7e1f4c82a90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_usage_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("estimated_cost_usd", sa.Numeric(precision=12, scale=6), nullable=False),
        sa.Column("cache_hit", sa.Boolean(), nullable=False),
        sa.Column("prompt_hash", sa.String(length=64), nullable=True),
        sa.Column("input_object_version", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ai_usage_logs_created_at"),
        "ai_usage_logs",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_usage_logs_model"),
        "ai_usage_logs",
        ["model"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_usage_logs_provider"),
        "ai_usage_logs",
        ["provider"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_usage_logs_provider"), table_name="ai_usage_logs")
    op.drop_index(op.f("ix_ai_usage_logs_model"), table_name="ai_usage_logs")
    op.drop_index(op.f("ix_ai_usage_logs_created_at"), table_name="ai_usage_logs")
    op.drop_table("ai_usage_logs")
