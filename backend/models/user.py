from extensions import db
from .base import BaseModel
from sqlalchemy import Column, String
from sqlalchemy.orm import validates, relationship
import re
from werkzeug.security import generate_password_hash, check_password_hash  # 新增


class User(BaseModel):
    """用户表"""
    __tablename__ = 'users'

    # 核心字段
    phone = Column(String(11), unique=True, nullable=True, index=True, comment='手机号，唯一索引')
    nickname = Column(String(20), nullable=False, default='', comment='用户昵称，1-20字符')
    avatar = Column(String(255), default='', comment='头像URL')

    # 密码字段（文档2.1节，账密登录备用）
    password_hash = Column(String(256), nullable=True, comment='密码哈希（bcrypt）')

    # 微信字段（文档2.3节，预留）
    wechat_openid = Column(String(128), unique=True, nullable=True, index=True, comment='微信OpenID')
    wechat_unionid = Column(String(128), unique=True, nullable=True, comment='微信UnionID')

    # 关系（延迟加载，避免循环导入）
    fortunes = relationship('FortuneRecord', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    answers = relationship('AnswerRecord', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    diaries = relationship('DiaryEntry', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    plaza_cards = relationship('PlazaCard', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')

    # 关联关系
    favorites = relationship('Favorite', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    likes = relationship('Like', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    profile = relationship('UserProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')

    @validates('phone')
    def validate_phone(self, key, phone):
        """手机号格式验证"""
        if phone and not re.match(r'^1[3-9]\d{9}$', phone):
            raise ValueError('Invalid phone number format')
        return phone

    # ---------- 新增：密码加密与校验 ----------
    def set_password(self, password: str):
        """使用 werkzeug 生成密码哈希，并存入 password_hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """校验明文密码是否与哈希匹配"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # ----------------------------------------

    @classmethod
    def create_with_profile(cls, **user_fields):
        """Create user and default profile in one transaction."""
        from services.user_profile_service import UserProfileService

        try:
            user = cls(**user_fields)
            db.session.add(user)
            db.session.flush()

            UserProfileService.create_default_profile(db.session, user.id)
            db.session.commit()
            return user
        except Exception:
            db.session.rollback()
            raise

    def __repr__(self):
        return f'<User {self.nickname} ({self.id})>'