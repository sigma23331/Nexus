from .base import db,BaseModel
from sqlalchemy.orm import validates

class AnswerRecord(BaseModel):
    """答案之书记录"""
    __tablename__ = 'answer_records'
    # 基础字段
    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False, index=True)

    # 内容字段（对应文档4.1节）
    question = db.Column(db.String(200), nullable=False, comment='提问内容，1-200字符')
    answer_text = db.Column(db.String(100), nullable=False, comment='答案内容，1-100字符')

    # 关系
    user = db.relationship('User', back_populates='answers')
    plaza_card = db.relationship('PlazaCard', back_populates='answer', uselist=False, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', back_populates='answer', cascade='all, delete-orphan')

    # 计算属性：是否被当前用户收藏
    def __repr__(self):
        return f'<AnswerRecord {self.id[:20]}... User:{self.user_id}>'