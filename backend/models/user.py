import enum
import re

from flask import current_app
from sqlalchemy import Column, Date, Enum, String, Text
from sqlalchemy.orm import relationship, validates
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from .base import BaseModel


class Gender(enum.Enum):
    MALE = 'male'
    FEMALE = 'female'
    SECRET = 'secret'


class User(BaseModel):
    __tablename__ = 'users'

    phone = Column(String(11), unique=True, nullable=True, index=True)
    nickname = Column(String(20), unique=True, nullable=False)
    avatar = Column(Text, default='')
    birthday = Column(Date, nullable=True)
    gender = Column(
        Enum(
            Gender,
            name='usergender',
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=Gender.SECRET,
        server_default=Gender.SECRET.value
    )
    password_hash = Column(String(256), nullable=True)
    wechat_openid = Column(String(128), unique=True, nullable=True, index=True)
    wechat_unionid = Column(String(128), unique=True, nullable=True)

    fortunes = relationship('FortuneRecord', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    answers = relationship('AnswerRecord', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    diaries = relationship('DiaryEntry', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    plaza_cards = relationship('PlazaCard', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    comments = relationship(
        'PlazaComment',
        foreign_keys='PlazaComment.user_id',
        back_populates='user',
        lazy='dynamic',
        cascade='all, delete-orphan',
    )
    comment_reports = relationship(
        'PlazaCommentReport',
        foreign_keys='PlazaCommentReport.reporter_user_id',
        back_populates='reporter',
        lazy='dynamic',
        cascade='all, delete-orphan',
    )
    favorites = relationship('Favorite', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    likes = relationship('Like', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    profile = relationship('UserProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')

    @validates('phone')
    def validate_phone(self, key, phone):
        if phone is not None and not re.match(r'^1[3-9]\d{9}$', phone):
            raise ValueError('Invalid phone number format')
        return phone

    @validates('nickname')
    def validate_nickname(self, key, nickname):
        if not nickname or len(nickname.strip()) < 1:
            raise ValueError('Nickname cannot be empty')
        return nickname.strip()

    @validates('gender')
    def validate_gender(self, key, gender):
        if gender is None:
            return Gender.SECRET
        if isinstance(gender, Gender):
            return gender
        if isinstance(gender, str):
            try:
                return Gender(gender)
            except ValueError as exc:
                raise ValueError('Invalid gender value') from exc
        raise ValueError('Invalid gender value')

    def set_password(self, password: str):
        method = current_app.config.get('PASSWORD_HASH_METHOD', 'pbkdf2:sha256')
        self.password_hash = generate_password_hash(password, method=method)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_with_profile(cls, **user_fields):
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
