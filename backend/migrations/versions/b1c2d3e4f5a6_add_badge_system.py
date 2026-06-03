"""add badge system

Revision ID: b1c2d3e4f5a6
Revises: a7b8c9d0e1f2
Create Date: 2026-06-02 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "b1c2d3e4f5a6"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


BADGES = [
    ("badge-first-fortune", "first_fortune", "初来乍到", "fortune", "首次查看当日运势", 1),
    ("badge-diary-writer", "diary_writer", "心灵笔触", "diary", "记录情绪日记天数", 2),
    ("badge-answer-traveler", "answer_traveler", "解惑旅人", "answer", "使用答案之书累计次数", 3),
    ("badge-lucky-streak", "lucky_streak", "好运连莲", "fortune", "连续多天获得高分运势", 4),
    ("badge-login-streak", "login_streak", "恒心之岛", "login", "连续登录天数", 5),
    ("badge-share-station", "share_station", "心卡驿站", "plaza", "成功分享运势或答案卡片", 6),
    ("badge-favorite-collector", "favorite_collector", "收藏小栈", "favorite", "收藏内容累计数量", 7),
    ("badge-social-master", "social_master", "社交达人", "plaza", "在分享广场发表评论或点赞", 8),
    ("badge-fortune-companion", "fortune_companion", "签运随身", "fortune", "累计查看运势天数", 9),
]

LEVELS = [
    ("first_fortune", 1, "初访之舟", "first_time", "fortune_exists", 1, "首次查看当日运势"),
    ("diary_writer", 1, "萌生笔意", "count", "diary_days", 3, "记录情绪日记满 3 天"),
    ("diary_writer", 2, "信笺常客", "count", "diary_days", 7, "记录情绪日记满 7 天"),
    ("diary_writer", 3, "心语成章", "count", "diary_days", 15, "记录情绪日记满 15 天"),
    ("diary_writer", 4, "心迹长存", "count", "diary_days", 30, "记录情绪日记满 30 天"),
    ("answer_traveler", 1, "迷途寻问", "count", "answer_count", 10, "使用答案之书累计 10 次"),
    ("answer_traveler", 2, "解惑学徒", "count", "answer_count", 50, "使用答案之书累计 50 次"),
    ("answer_traveler", 3, "明灯行者", "count", "answer_count", 200, "使用答案之书累计 200 次"),
    ("answer_traveler", 4, "智慧先知", "count", "answer_count", 1000, "使用答案之书累计 1000 次"),
    ("lucky_streak", 1, "祥瑞之始", "streak", "lucky_fortune_streak", 3, "连续 3 天运势评级为上上签或更高"),
    ("lucky_streak", 2, "鸿运当头", "streak", "lucky_fortune_streak", 7, "连续 7 天运势评级为上上签或更高"),
    ("login_streak", 1, "七日驻留", "streak", "login_streak", 7, "连续登录 7 天"),
    ("login_streak", 2, "潮汐守望", "streak", "login_streak", 30, "连续登录 30 天"),
    ("login_streak", 3, "季风航标", "streak", "login_streak", 100, "连续登录 100 天"),
    ("login_streak", 4, "永恒灯塔", "streak", "login_streak", 365, "连续登录 365 天"),
    ("share_station", 1, "见习驿员", "count", "plaza_card_count", 1, "成功分享运势/答案卡片 1 次"),
    ("share_station", 2, "正式驿员", "count", "plaza_card_count", 10, "累计分享 10 次"),
    ("share_station", 3, "卡片信使", "count", "plaza_card_count", 50, "累计分享 50 次"),
    ("share_station", 4, "驿站之主", "count", "plaza_card_count", 200, "累计分享 200 次"),
    ("favorite_collector", 1, "拾贝新手", "count", "favorite_count", 3, "收藏内容累计 3 条"),
    ("favorite_collector", 2, "珍藏小栈", "count", "favorite_count", 15, "收藏内容累计 15 条"),
    ("favorite_collector", 3, "鉴赏大师", "count", "favorite_count", 50, "收藏内容累计 50 条"),
    ("favorite_collector", 4, "时空收藏家", "count", "favorite_count", 200, "收藏内容累计 200 条"),
    ("social_master", 1, "初次登门", "count", "plaza_interaction_count", 3, "在分享广场发表评论或点赞 3 次"),
    ("social_master", 2, "串门熟手", "count", "plaza_interaction_count", 50, "互动累计 50 次"),
    ("social_master", 3, "群岛访客", "count", "plaza_interaction_count", 200, "互动累计 200 次"),
    ("social_master", 4, "知交满岛", "count", "plaza_interaction_count", 800, "互动累计 800 次"),
    ("fortune_companion", 1, "一签启运", "count", "fortune_days", 7, "累计查看运势 7 天"),
    ("fortune_companion", 2, "签途常客", "count", "fortune_days", 30, "累计查看运势 30 天"),
    ("fortune_companion", 3, "签缘行者", "count", "fortune_days", 100, "累计查看运势 100 天"),
    ("fortune_companion", 4, "灵签居士", "count", "fortune_days", 300, "累计查看运势 300 天"),
]


def upgrade():
    op.create_table(
        "badge_definitions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("icon_url", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("gray_icon_url", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_badge_definitions_code"), "badge_definitions", ["code"], unique=False)
    op.create_index(op.f("ix_badge_definitions_category"), "badge_definitions", ["category"], unique=False)
    op.create_index(op.f("ix_badge_definitions_sort_order"), "badge_definitions", ["sort_order"], unique=False)
    op.create_index(op.f("ix_badge_definitions_enabled"), "badge_definitions", ["enabled"], unique=False)

    op.create_table(
        "badge_levels",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("badge_code", sa.String(length=64), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=32), nullable=False),
        sa.Column("condition_type", sa.String(length=32), nullable=False),
        sa.Column("metric_key", sa.String(length=64), nullable=False),
        sa.Column("threshold", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False, server_default=""),
        sa.ForeignKeyConstraint(["badge_code"], ["badge_definitions.code"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("badge_code", "level", name="uq_badge_level"),
    )
    op.create_index(op.f("ix_badge_levels_badge_code"), "badge_levels", ["badge_code"], unique=False)
    op.create_index(op.f("ix_badge_levels_metric_key"), "badge_levels", ["metric_key"], unique=False)

    op.create_table(
        "user_badges",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("badge_code", sa.String(length=64), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("target", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unlocked_at", sa.DateTime(), nullable=True),
        sa.Column("last_evaluated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["badge_code"], ["badge_definitions.code"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "badge_code", name="uq_user_badge"),
    )
    op.create_index(op.f("ix_user_badges_user_id"), "user_badges", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_badges_badge_code"), "user_badges", ["badge_code"], unique=False)

    op.create_table(
        "user_login_days",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("login_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "login_date", name="uq_user_login_day"),
    )
    op.create_index(op.f("ix_user_login_days_user_id"), "user_login_days", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_login_days_login_date"), "user_login_days", ["login_date"], unique=False)

    badge_table = sa.table(
        "badge_definitions",
        sa.column("id", sa.String),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("category", sa.String),
        sa.column("description", sa.String),
        sa.column("icon_url", sa.String),
        sa.column("gray_icon_url", sa.String),
        sa.column("sort_order", sa.Integer),
        sa.column("enabled", sa.Boolean),
    )
    level_table = sa.table(
        "badge_levels",
        sa.column("id", sa.String),
        sa.column("badge_code", sa.String),
        sa.column("level", sa.Integer),
        sa.column("title", sa.String),
        sa.column("condition_type", sa.String),
        sa.column("metric_key", sa.String),
        sa.column("threshold", sa.Integer),
        sa.column("description", sa.String),
    )

    op.bulk_insert(
        badge_table,
        [
            {
                "id": row[0],
                "code": row[1],
                "name": row[2],
                "category": row[3],
                "description": row[4],
                "icon_url": f"/images/badges/{row[1]}.png",
                "gray_icon_url": f"/images/badges/{row[1]}_gray.png",
                "sort_order": row[5],
                "enabled": True,
            }
            for row in BADGES
        ],
    )
    op.bulk_insert(
        level_table,
        [
            {
                "id": f"badge-level-{row[0]}-{row[1]}",
                "badge_code": row[0],
                "level": row[1],
                "title": row[2],
                "condition_type": row[3],
                "metric_key": row[4],
                "threshold": row[5],
                "description": row[6],
            }
            for row in LEVELS
        ],
    )


def downgrade():
    op.drop_index(op.f("ix_user_login_days_login_date"), table_name="user_login_days")
    op.drop_index(op.f("ix_user_login_days_user_id"), table_name="user_login_days")
    op.drop_table("user_login_days")
    op.drop_index(op.f("ix_user_badges_badge_code"), table_name="user_badges")
    op.drop_index(op.f("ix_user_badges_user_id"), table_name="user_badges")
    op.drop_table("user_badges")
    op.drop_index(op.f("ix_badge_levels_metric_key"), table_name="badge_levels")
    op.drop_index(op.f("ix_badge_levels_badge_code"), table_name="badge_levels")
    op.drop_table("badge_levels")
    op.drop_index(op.f("ix_badge_definitions_enabled"), table_name="badge_definitions")
    op.drop_index(op.f("ix_badge_definitions_sort_order"), table_name="badge_definitions")
    op.drop_index(op.f("ix_badge_definitions_category"), table_name="badge_definitions")
    op.drop_index(op.f("ix_badge_definitions_code"), table_name="badge_definitions")
    op.drop_table("badge_definitions")
