from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint
from .base import db, BaseModel
import enum
from sqlalchemy.dialects.postgresql import ARRAY

class CardType(enum.Enum):
    FORTUNE = 'fortune'
    ANSWER = 'answer'

class PlazaCard(BaseModel):
    __tablename__ = 'plaza_cards'
    __table_args__ = (
        CheckConstraint(
            "(type = 'FORTUNE' AND fortune_id IS NOT NULL AND answer_id IS NULL) OR "
            "(type = 'ANSWER' AND answer_id IS NOT NULL AND fortune_id IS NULL)",
            name='check_valid_source'
        ),
    )

    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.Enum(CardType), nullable=False)
    snapshot_url = db.Column(db.String(500), nullable=False)
    content = db.Column(db.String(100), nullable=True)
    tags = db.Column(ARRAY(db.String(10)), nullable=True)
    likes_count = db.Column(db.Integer, default=0, nullable=False)

    fortune_id = db.Column(db.String(64), db.ForeignKey('fortune_records.id'), nullable=True)
    answer_id = db.Column(db.String(64), db.ForeignKey('answer_records.id'), nullable=True)

    user = db.relationship('User', back_populates='plaza_cards')
    fortune = db.relationship('FortuneRecord', back_populates='plaza_card', foreign_keys=[fortune_id])
    answer = db.relationship('AnswerRecord', back_populates='plaza_card', foreign_keys=[answer_id])
    likes = db.relationship('Like', back_populates='card', cascade='all, delete-orphan')

    @validates('tags')
    def validate_tags(self, key, tags):
        if tags and len(tags) > 3:
            raise ValueError('Cannot have more than 3 tags')
        if tags:
            for tag in tags:
                if len(tag) > 10:
                    raise ValueError('Tag cannot exceed 10 characters')
        return tags

    def __repr__(self):
        return f'<PlazaCard {self.id[:20]}... Type:{self.type.value} Likes:{self.likes_count}>'
