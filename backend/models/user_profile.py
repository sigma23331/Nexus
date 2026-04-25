from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from .base import db
import enum

class AnswerStyle(enum.Enum):
    PHILOSOPHICAL = 'philosophical'
    HUMOR = 'humor'

class PreferredFeature(enum.Enum):
    MOOD_DIARY = 'mood_diary'
    FORTUNE = 'fortune'
    ANSWER = 'answer'

class ActiveHourBucket(enum.Enum):
    MORNING = 'morning'
    AFTERNOON = 'afternoon'
    NIGHT = 'night'

class UserProfile(db.Model):
    """用户个性化画像表"""
    __tablename__ = 'user_profiles'

    # user_id 作为主键（1对1关联 users.id）
    user_id = db.Column(
        db.String(64),
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
        comment='用户ID，主键'
    )

    answer_style = db.Column(
        db.Enum(AnswerStyle),
        nullable=True,
        comment='用户偏好的答案风格：philosophical/humor'
    )

    topic_interests = db.Column(
        ARRAY(db.String(20)),
        nullable=True,
        comment='兴趣标签数组，如 ["love","career","health"]'
    )

    self_context_tag = db.Column(
        db.String(64),
        nullable=True,
        comment='用户自述场景，如“考研期”'
    )

    mood_tendency = db.Column(
        db.String(50),
        nullable=True,
        comment='情绪倾向，AI分析生成，例如"optimistic"/"anxious"等'
    )

    preferred_feature = db.Column(
        db.Enum(PreferredFeature),
        nullable=True,
        comment='最常用功能：mood_diary/fortune/answer'
    )

    active_hour_bucket = db.Column(
        db.Enum(ActiveHourBucket),
        nullable=True,
        comment='活跃时段：morning/afternoon/night'
    )

    personalization_enabled = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        comment='是否开启个性化推荐，默认true'
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment='创建时间'
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment='更新时间'
    )

    # 关系：反向引用 User.user_profile
    user = db.relationship('User', back_populates='profile', uselist=False)

    def __repr__(self):
        return f'<UserProfile user_id={self.user_id} enabled={self.personalization_enabled}>'