"""Add key_decisions to meetings

Revision ID: 004
Revises: 003
Create Date: 2025-08-08 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("meetings", sa.Column("key_decisions", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("meetings", "key_decisions")
