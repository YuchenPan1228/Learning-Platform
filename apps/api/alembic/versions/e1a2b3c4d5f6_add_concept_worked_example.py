"""add concept worked_example

Revision ID: e1a2b3c4d5f6
Revises: d5e9f2b04c82
Create Date: 2026-07-19 22:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e1a2b3c4d5f6"
down_revision: Union[str, Sequence[str], None] = "d5e9f2b04c82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("concepts", sa.Column("worked_example", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("concepts", "worked_example")
