"""expand fortune record fields

Revision ID: 8d3a9f4b2c11
Revises: de707e93b7ec
Create Date: 2026-05-21 18:20:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "8d3a9f4b2c11"
down_revision = "de707e93b7ec"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("fortune_records", schema=None) as batch_op:
        batch_op.add_column(sa.Column("love", sa.String(length=20), nullable=True, comment="爱情运势"))
        batch_op.add_column(sa.Column("career", sa.String(length=20), nullable=True, comment="事业运势"))
        batch_op.add_column(sa.Column("health", sa.String(length=20), nullable=True, comment="健康运势"))
        batch_op.add_column(sa.Column("wealth", sa.String(length=20), nullable=True, comment="财富运势"))
        batch_op.add_column(
            sa.Column(
                "gua_meaning_lines",
                postgresql.ARRAY(sa.String(length=40)),
                nullable=True,
                comment="Two-line gua meaning copy",
            )
        )
        batch_op.add_column(sa.Column("lucky_hour_name", sa.String(length=20), nullable=True, comment="Lucky hour label"))
        batch_op.add_column(sa.Column("lucky_hour_range", sa.String(length=20), nullable=True, comment="Lucky hour range"))

    op.execute(
        sa.text(
            """
            UPDATE fortune_records
            SET
                love = COALESCE(love, '平稳'),
                career = COALESCE(career, '平稳'),
                health = COALESCE(health, '稳定'),
                wealth = COALESCE(wealth, '平稳'),
                gua_meaning_lines = COALESCE(
                    gua_meaning_lines,
                    CASE
                        WHEN score >= 85 THEN ARRAY['乾元得势', '顺势而为，主动推进']
                        WHEN score >= 75 THEN ARRAY['木火通明', '节奏清朗，宜扩展布局']
                        WHEN score >= 65 THEN ARRAY['阴阳守中', '稳步前行，先稳后进']
                        WHEN score >= 55 THEN ARRAY['地山谦', '以退为进，夯实基础']
                        ELSE ARRAY['坎离未济', '先养精神，再谋后动']
                    END
                ),
                lucky_hour_name = COALESCE(
                    lucky_hour_name,
                    CASE
                        WHEN score >= 90 THEN '辰时'
                        WHEN score >= 82 THEN '巳时'
                        WHEN score >= 74 THEN '午时'
                        WHEN score >= 66 THEN '未时'
                        ELSE '酉时'
                    END
                ),
                lucky_hour_range = COALESCE(
                    lucky_hour_range,
                    CASE
                        WHEN score >= 90 THEN '07:00-09:00'
                        WHEN score >= 82 THEN '09:00-11:00'
                        WHEN score >= 74 THEN '11:00-13:00'
                        WHEN score >= 66 THEN '13:00-15:00'
                        ELSE '17:00-19:00'
                    END
                )
            """
        )
    )

    with op.batch_alter_table("fortune_records", schema=None) as batch_op:
        batch_op.alter_column("love", existing_type=sa.String(length=20), nullable=False)
        batch_op.alter_column("career", existing_type=sa.String(length=20), nullable=False)
        batch_op.alter_column("health", existing_type=sa.String(length=20), nullable=False)
        batch_op.alter_column("wealth", existing_type=sa.String(length=20), nullable=False)
        batch_op.alter_column(
            "gua_meaning_lines",
            existing_type=postgresql.ARRAY(sa.String(length=40)),
            nullable=False,
        )
        batch_op.alter_column("lucky_hour_name", existing_type=sa.String(length=20), nullable=False)
        batch_op.alter_column("lucky_hour_range", existing_type=sa.String(length=20), nullable=False)
        batch_op.drop_column("lucky_color")
        batch_op.drop_column("lucky_direction")


def downgrade():
    with op.batch_alter_table("fortune_records", schema=None) as batch_op:
        batch_op.add_column(sa.Column("lucky_direction", sa.String(length=20), nullable=True, comment="幸运方向"))
        batch_op.add_column(sa.Column("lucky_color", sa.String(length=20), nullable=True, comment="幸运颜色"))
        batch_op.drop_column("lucky_hour_range")
        batch_op.drop_column("lucky_hour_name")
        batch_op.drop_column("gua_meaning_lines")
        batch_op.drop_column("wealth")
        batch_op.drop_column("health")
        batch_op.drop_column("career")
        batch_op.drop_column("love")
