"""add user equipped badges

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-06-06 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "d3e4f5a6b7c8"
down_revision = "c2d3e4f5a6b7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_equipped_badges",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("badge_code", sa.String(length=64), nullable=False),
        sa.Column("slot_order", sa.Integer(), nullable=False),
        sa.CheckConstraint("slot_order >= 1 AND slot_order <= 3", name="ck_user_equipped_badge_slot_order"),
        sa.ForeignKeyConstraint(["badge_code"], ["badge_definitions.code"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "badge_code", name="uq_user_equipped_badge"),
        sa.UniqueConstraint("user_id", "slot_order", name="uq_user_equipped_badge_slot"),
    )
    op.create_index(op.f("ix_user_equipped_badges_user_id"), "user_equipped_badges", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_equipped_badges_badge_code"), "user_equipped_badges", ["badge_code"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_user_equipped_badges_badge_code"), table_name="user_equipped_badges")
    op.drop_index(op.f("ix_user_equipped_badges_user_id"), table_name="user_equipped_badges")
    op.drop_table("user_equipped_badges")
