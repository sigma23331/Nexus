from .base import db, BaseModel
from sqlalchemy.orm import validates
from sqlalchemy import event
import enum

class MoodType(enum.Enum):
    HAPPY = 'happy'
    CALM = 'calm'
    SAD = 'sad'
    ANGRY = 'angry'
    TIRED = 'tired'

class DiaryEntry(BaseModel):
    __tablename__ = 'diary_entries'

    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False, index=True)
    mood_tag = db.Column(db.Enum(MoodType), nullable=False)
    content = db.Column(db.String(2000), nullable=False)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    created_date = db.Column(db.Date, nullable=False, index=True)

    user = db.relationship('User', back_populates='diaries')

    @validates('content')
    def validate_content(self, key, content):
        if not content or len(content.strip()) == 0:
            raise ValueError('Content cannot be empty')
        if len(content) > 2000:
            raise ValueError('Content cannot exceed 2000 characters')
        return content

    def __repr__(self):
        return f'<DiaryEntry {self.id[:20]}... Mood:{self.mood_tag.value}>'

@event.listens_for(DiaryEntry, 'before_insert')
def set_created_date(mapper, connection, target):
    if target.created_at and not target.created_date:
        target.created_date = target.created_at.date()