"""add user flashcard progress for spaced repetition

Revision ID: f7a8b9c0d1e2
Revises: e1a2b3c4d5f6
Create Date: 2026-07-21 16:55:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, Sequence[str], None] = "e1a2b3c4d5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_flashcard_progress",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("flashcard_id", sa.Integer(), nullable=False),
        sa.Column("interval_days", sa.Float(), nullable=False),
        sa.Column("ease_factor", sa.Float(), nullable=False),
        sa.Column("repetitions", sa.Integer(), nullable=False),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "last_rating",
            sa.Enum("again", "good", "easy", name="flashcard_review_rating"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["flashcard_id"], ["flashcards.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "flashcard_id"),
    )
    op.create_index(
        op.f("ix_user_flashcard_progress_next_review_at"),
        "user_flashcard_progress",
        ["next_review_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_user_flashcard_progress_next_review_at"),
        table_name="user_flashcard_progress",
    )
    op.drop_table("user_flashcard_progress")
    op.execute("DROP TYPE IF EXISTS flashcard_review_rating")
