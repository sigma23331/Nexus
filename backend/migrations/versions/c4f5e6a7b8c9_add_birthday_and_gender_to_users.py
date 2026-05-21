"""add birthday and gender to users

Revision ID: c4f5e6a7b8c9
Revises: 8d3a9f4b2c11
Create Date: 2026-05-21 20:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c4f5e6a7b8c9"
down_revision = "8d3a9f4b2c11"
branch_labels = None
depends_on = None


gender_enum = sa.Enum("male", "female", "secret", name="usergender")


def upgrade():
    bind = op.get_bind()
    gender_enum.create(bind, checkfirst=True)

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("birthday", sa.Date(), nullable=True, comment="生日，可为空"))
        batch_op.add_column(
            sa.Column(
                "gender",
                gender_enum,
                nullable=False,
                server_default="secret",
                comment="性别：male/female/secret",
            )
        )

    op.execute(sa.text("UPDATE users SET gender = 'secret' WHERE gender IS NULL"))


def downgrade():
    bind = op.get_bind()

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("gender")
        batch_op.drop_column("birthday")

    gender_enum.drop(bind, checkfirst=True)
