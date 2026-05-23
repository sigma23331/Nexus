"""add content moderation logs

Revision ID: f6c2e3d4b5a6
Revises: e5b1d2f3a4c5
Create Date: 2026-05-23 19:10:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "f6c2e3d4b5a6"
down_revision = "e5b1d2f3a4c5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "content_moderation_logs",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("scene", sa.String(length=64), nullable=False),
        sa.Column("target_type", sa.String(length=32), nullable=False),
        sa.Column("target_id", sa.String(length=64), nullable=True),
        sa.Column("user_id", sa.String(length=64), nullable=True),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("processed_text", sa.Text(), nullable=True),
        sa.Column("action", sa.String(length=16), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("labels", sa.JSON(), nullable=True),
        sa.Column("reason_code", sa.String(length=64), nullable=True),
        sa.Column("provider_name", sa.String(length=32), nullable=True),
        sa.Column("provider_result", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("content_moderation_logs", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_content_moderation_logs_action"), ["action"], unique=False)
        batch_op.create_index(batch_op.f("ix_content_moderation_logs_scene"), ["scene"], unique=False)
        batch_op.create_index(batch_op.f("ix_content_moderation_logs_target_id"), ["target_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_content_moderation_logs_target_type"), ["target_type"], unique=False)
        batch_op.create_index(batch_op.f("ix_content_moderation_logs_user_id"), ["user_id"], unique=False)
        batch_op.create_index(
            "idx_content_moderation_target_created",
            ["target_type", "target_id", "created_at"],
            unique=False,
        )


def downgrade():
    with op.batch_alter_table("content_moderation_logs", schema=None) as batch_op:
        batch_op.drop_index("idx_content_moderation_target_created")
        batch_op.drop_index(batch_op.f("ix_content_moderation_logs_user_id"))
        batch_op.drop_index(batch_op.f("ix_content_moderation_logs_target_type"))
        batch_op.drop_index(batch_op.f("ix_content_moderation_logs_target_id"))
        batch_op.drop_index(batch_op.f("ix_content_moderation_logs_scene"))
        batch_op.drop_index(batch_op.f("ix_content_moderation_logs_action"))
    op.drop_table("content_moderation_logs")
