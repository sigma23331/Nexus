"""add fortune pk records

Revision ID: a7b8c9d0e1f2
Revises: a1b2c3d4e5f6
Create Date: 2026-05-31 14:30:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "a7b8c9d0e1f2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


pk_result_enum = postgresql.ENUM(
    "challenger_win",
    "defender_win",
    "draw",
    name="fortune_pk_result",
    create_type=False,
)
pk_status_enum = postgresql.ENUM(
    "pending",
    "completed",
    "expired",
    name="fortune_pk_status",
    create_type=False,
)


def upgrade():
    bind = op.get_bind()
    pk_result_enum.create(bind, checkfirst=True)
    pk_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "fortune_pk_records",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("token", sa.String(length=32), nullable=False),
        sa.Column("challenger_id", sa.String(length=64), nullable=False),
        sa.Column("challenger_score", sa.Integer(), nullable=False),
        sa.Column("defender_id", sa.String(length=64), nullable=True),
        sa.Column("defender_score", sa.Integer(), nullable=True),
        sa.Column("result", pk_result_enum, nullable=True),
        sa.Column("status", pk_status_enum, nullable=False, server_default="pending"),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["challenger_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["defender_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("fortune_pk_records", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_fortune_pk_records_token"), ["token"], unique=True)
        batch_op.create_index(batch_op.f("ix_fortune_pk_records_challenger_id"), ["challenger_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_fortune_pk_records_defender_id"), ["defender_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_fortune_pk_records_status"), ["status"], unique=False)
        batch_op.create_index(batch_op.f("ix_fortune_pk_records_date"), ["date"], unique=False)


def downgrade():
    with op.batch_alter_table("fortune_pk_records", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_fortune_pk_records_date"))
        batch_op.drop_index(batch_op.f("ix_fortune_pk_records_status"))
        batch_op.drop_index(batch_op.f("ix_fortune_pk_records_defender_id"))
        batch_op.drop_index(batch_op.f("ix_fortune_pk_records_challenger_id"))
        batch_op.drop_index(batch_op.f("ix_fortune_pk_records_token"))
    op.drop_table("fortune_pk_records")

    bind = op.get_bind()
    pk_status_enum.drop(bind, checkfirst=True)
    pk_result_enum.drop(bind, checkfirst=True)
