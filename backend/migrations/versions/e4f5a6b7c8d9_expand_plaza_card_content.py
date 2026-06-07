"""expand plaza card content

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-06-07 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "e4f5a6b7c8d9"
down_revision = "d3e4f5a6b7c8"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plaza_cards", schema=None) as batch_op:
        batch_op.alter_column(
            "content",
            existing_type=sa.String(length=100),
            type_=sa.String(length=1000),
            existing_nullable=True,
        )


def downgrade():
    op.execute(sa.text("UPDATE plaza_cards SET content = LEFT(content, 100) WHERE LENGTH(content) > 100"))
    with op.batch_alter_table("plaza_cards", schema=None) as batch_op:
        batch_op.alter_column(
            "content",
            existing_type=sa.String(length=1000),
            type_=sa.String(length=100),
            existing_nullable=True,
        )
