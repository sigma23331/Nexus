"""add plaza comments

Revision ID: e5b1d2f3a4c5
Revises: c4f5e6a7b8c9
Create Date: 2026-05-23 16:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "e5b1d2f3a4c5"
down_revision = "c4f5e6a7b8c9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plaza_cards", schema=None) as batch_op:
        batch_op.add_column(sa.Column("comments_count", sa.Integer(), nullable=False, server_default="0"))

    op.create_table(
        "plaza_comments",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("card_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("parent_id", sa.String(length=64), nullable=True),
        sa.Column("reply_to_user_id", sa.String(length=64), nullable=True),
        sa.Column("content", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("moderation_status", sa.String(length=16), nullable=False),
        sa.Column("moderation_source", sa.String(length=32), nullable=True),
        sa.Column("moderation_reason", sa.String(length=255), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["card_id"], ["plaza_cards.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["plaza_comments.id"]),
        sa.ForeignKeyConstraint(["reply_to_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("plaza_comments", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_plaza_comments_card_id"), ["card_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_plaza_comments_moderation_status"), ["moderation_status"], unique=False)
        batch_op.create_index(batch_op.f("ix_plaza_comments_parent_id"), ["parent_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_plaza_comments_reply_to_user_id"), ["reply_to_user_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_plaza_comments_status"), ["status"], unique=False)
        batch_op.create_index(batch_op.f("ix_plaza_comments_user_id"), ["user_id"], unique=False)
        batch_op.create_index(
            "idx_plaza_comment_card_parent_created",
            ["card_id", "parent_id", "created_at"],
            unique=False,
        )
        batch_op.create_index(
            "idx_plaza_comment_user_created",
            ["user_id", "created_at"],
            unique=False,
        )

    op.create_table(
        "plaza_comment_reports",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("comment_id", sa.String(length=64), nullable=False),
        sa.Column("reporter_user_id", sa.String(length=64), nullable=False),
        sa.Column("reason_code", sa.String(length=32), nullable=False),
        sa.Column("reason_text", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(["comment_id"], ["plaza_comments.id"]),
        sa.ForeignKeyConstraint(["reporter_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reporter_user_id", "comment_id", name="uq_reporter_comment"),
    )
    with op.batch_alter_table("plaza_comment_reports", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_plaza_comment_reports_comment_id"), ["comment_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_plaza_comment_reports_reporter_user_id"), ["reporter_user_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_plaza_comment_reports_status"), ["status"], unique=False)
        batch_op.create_index(
            "idx_plaza_comment_report_comment_status",
            ["comment_id", "status"],
            unique=False,
        )


def downgrade():
    with op.batch_alter_table("plaza_comment_reports", schema=None) as batch_op:
        batch_op.drop_index("idx_plaza_comment_report_comment_status")
        batch_op.drop_index(batch_op.f("ix_plaza_comment_reports_status"))
        batch_op.drop_index(batch_op.f("ix_plaza_comment_reports_reporter_user_id"))
        batch_op.drop_index(batch_op.f("ix_plaza_comment_reports_comment_id"))
    op.drop_table("plaza_comment_reports")

    with op.batch_alter_table("plaza_comments", schema=None) as batch_op:
        batch_op.drop_index("idx_plaza_comment_user_created")
        batch_op.drop_index("idx_plaza_comment_card_parent_created")
        batch_op.drop_index(batch_op.f("ix_plaza_comments_user_id"))
        batch_op.drop_index(batch_op.f("ix_plaza_comments_status"))
        batch_op.drop_index(batch_op.f("ix_plaza_comments_reply_to_user_id"))
        batch_op.drop_index(batch_op.f("ix_plaza_comments_parent_id"))
        batch_op.drop_index(batch_op.f("ix_plaza_comments_moderation_status"))
        batch_op.drop_index(batch_op.f("ix_plaza_comments_card_id"))
    op.drop_table("plaza_comments")

    with op.batch_alter_table("plaza_cards", schema=None) as batch_op:
        batch_op.drop_column("comments_count")
