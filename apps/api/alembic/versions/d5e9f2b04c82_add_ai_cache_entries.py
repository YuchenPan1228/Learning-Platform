"""add ai cache entries

Revision ID: d5e9f2b04c82
Revises: c4d8e1a93b71
Create Date: 2026-07-17 06:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "d5e9f2b04c82"
down_revision: Union[str, Sequence[str], None] = "c4d8e1a93b71"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_cache_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "result_kind",
            sa.Enum(
                "explanation",
                "hint",
                "summary",
                "generated_question",
                name="ai_cache_result_kind",
            ),
            nullable=False,
        ),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("prompt_template_version", sa.String(length=64), nullable=False),
        sa.Column("prompt_hash", sa.String(length=64), nullable=False),
        sa.Column("input_object_version", sa.String(length=64), nullable=False),
        sa.Column("response_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider",
            "model",
            "result_kind",
            "prompt_template_version",
            "prompt_hash",
            "input_object_version",
            name="uq_ai_cache_entries_lookup",
        ),
    )
    op.create_index(
        op.f("ix_ai_cache_entries_model"),
        "ai_cache_entries",
        ["model"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_cache_entries_provider"),
        "ai_cache_entries",
        ["provider"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_cache_entries_result_kind"),
        "ai_cache_entries",
        ["result_kind"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_cache_entries_result_kind"), table_name="ai_cache_entries")
    op.drop_index(op.f("ix_ai_cache_entries_provider"), table_name="ai_cache_entries")
    op.drop_index(op.f("ix_ai_cache_entries_model"), table_name="ai_cache_entries")
    op.drop_table("ai_cache_entries")
    op.execute("DROP TYPE IF EXISTS ai_cache_result_kind")
