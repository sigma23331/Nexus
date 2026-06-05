"""add badge notifications

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-06-05 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "c2d3e4f5a6b7"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_badge_notifications",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("badge_code", sa.String(length=64), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("change_type", sa.String(length=16), nullable=False),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["badge_code"], ["badge_definitions.code"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_badge_notifications_user_id"), "user_badge_notifications", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_badge_notifications_badge_code"), "user_badge_notifications", ["badge_code"], unique=False)
    op.create_index(op.f("ix_user_badge_notifications_change_type"), "user_badge_notifications", ["change_type"], unique=False)
    op.create_index(op.f("ix_user_badge_notifications_read_at"), "user_badge_notifications", ["read_at"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_user_badge_notifications_read_at"), table_name="user_badge_notifications")
    op.drop_index(op.f("ix_user_badge_notifications_change_type"), table_name="user_badge_notifications")
    op.drop_index(op.f("ix_user_badge_notifications_badge_code"), table_name="user_badge_notifications")
    op.drop_index(op.f("ix_user_badge_notifications_user_id"), table_name="user_badge_notifications")
    op.drop_table("user_badge_notifications")
