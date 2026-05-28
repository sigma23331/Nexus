"""add user geo location fields

Revision ID: a1b2c3d4e5f6
Revises: f6c2e3d4b5a6
Create Date: 2026-05-28 16:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "f6c2e3d4b5a6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("latitude", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("longitude", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("location_accuracy", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("location_updated_at", sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("location_updated_at")
        batch_op.drop_column("location_accuracy")
        batch_op.drop_column("longitude")
        batch_op.drop_column("latitude")
