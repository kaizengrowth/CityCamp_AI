"""Add image_paths to meetings table

Revision ID: 002
Revises: 001
Create Date: 2025-08-06

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    # Add image_paths column to meetings table
    op.add_column(
        "meetings",
        sa.Column("image_paths", postgresql.JSON(astext_type=sa.Text()), nullable=True),
    )


def downgrade():
    # Remove image_paths column from meetings table
    op.drop_column("meetings", "image_paths")
