from .base import db, BaseModel
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import validates
from datetime import date


class FortuneRecord(BaseModel):
    """运势记录表"""
    __tablename__ = 'fortune_records'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='uq_user_date'),
    )

    # 基础字段
    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True, comment='运势所属日期')

    # 运势内容（对应文档3.1节）
    score = db.Column(db.Integer, nullable=False, comment='运势分数0-100')
    title = db.Column(db.String(20), nullable=False, comment='运势标题，1-20字符')
    content = db.Column(db.String(200), nullable=False, comment='运势内容，1-200字符')

    # 宜忌事项（使用PostgreSQL数组类型）
    yi = db.Column(ARRAY(db.String(20)), nullable=False, comment='宜事项数组，最多5个')
    ji = db.Column(ARRAY(db.String(20)), nullable=False, comment='忌事项数组，最多5个')

    # 可选字段（文档8.1节提及）
    lucky_color = db.Column(db.String(20), nullable=True, comment='幸运颜色')
    lucky_direction = db.Column(db.String(20), nullable=True, comment='幸运方向')

    # 关系
    user = db.relationship('User', back_populates='fortunes')
    plaza_card = db.relationship('PlazaCard', back_populates='fortune', uselist=False, cascade='all, delete-orphan')

    @validates('score')
    def validate_score(self, key, score):
        if not 0 <= score <= 100:
            raise ValueError('Score must be between 0 and 100')
        return score

    @validates('yi', 'ji')
    def validate_arrays(self, key, value):
        if value and len(value) > 5:
            raise ValueError(f'{key} array cannot have more than 5 items')
        return value

    def __repr__(self):
        return f'<FortuneRecord {self.date} User:{self.user_id} Score:{self.score}>'