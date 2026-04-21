from .base import db, BaseModel
from datetime import datetime


class Favorite(BaseModel):
    """收藏关系表"""
    __tablename__ = 'favorites'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'answer_id', name='uq_user_answer'),
    )

    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False, index=True)
    answer_id = db.Column(db.String(64), db.ForeignKey('answer_records.id'), nullable=False, index=True)

    # 关系
    user = db.relationship('User', back_populates='favorites')
    answer = db.relationship('AnswerRecord', back_populates='favorites')

    def __repr__(self):
        return f'<Favorite User:{self.user_id} Answer:{self.answer_id}>'


class Like(BaseModel):
    """点赞关系表"""
    __tablename__ = 'likes'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'card_id', name='uq_user_card'),
    )

    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False, index=True)
    card_id = db.Column(db.String(64), db.ForeignKey('plaza_cards.id'), nullable=False, index=True)

    # 关系
    user = db.relationship('User', back_populates='likes')
    card = db.relationship('PlazaCard', back_populates='likes')

    def __repr__(self):
        return f'<Like User:{self.user_id} Card:{self.card_id}>'


class SmsCode(BaseModel):
    """短信验证码表"""
    __tablename__ = 'sms_codes'

    phone = db.Column(db.String(11), nullable=False, index=True, comment='手机号')
    code = db.Column(db.String(6), nullable=False, comment='6位验证码')
    action = db.Column(db.String(20), nullable=False, comment='验证码用途：login/bind')
    expires_at = db.Column(db.DateTime, nullable=False, comment='过期时间')
    used = db.Column(db.Boolean, default=False, nullable=False, comment='是否已使用')

    # 索引：按手机号和过期时间查询
    __table_args__ = (
        db.Index('idx_phone_action_expires', 'phone', 'action', 'expires_at'),
    )

    def __repr__(self):
        return f'<SmsCode {self.phone} {self.code[:2]}**>'