from datetime import datetime

from .base import db, BaseModel


class PlazaComment(BaseModel):
    __tablename__ = "plaza_comments"
    __table_args__ = (
        db.Index("idx_plaza_comment_card_parent_created", "card_id", "parent_id", "created_at"),
        db.Index("idx_plaza_comment_user_created", "user_id", "created_at"),
    )

    card_id = db.Column(db.String(64), db.ForeignKey("plaza_cards.id"), nullable=False, index=True)
    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=False, index=True)
    parent_id = db.Column(db.String(64), db.ForeignKey("plaza_comments.id"), nullable=True, index=True)
    reply_to_user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=True, index=True)

    content = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="visible", index=True)
    moderation_status = db.Column(db.String(16), nullable=False, default="pass", index=True)
    moderation_source = db.Column(db.String(32), nullable=True)
    moderation_reason = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    card = db.relationship("PlazaCard", back_populates="comments")
    user = db.relationship("User", foreign_keys=[user_id], back_populates="comments")
    parent = db.relationship("PlazaComment", remote_side="PlazaComment.id", back_populates="replies")
    replies = db.relationship(
        "PlazaComment",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    reply_to_user = db.relationship("User", foreign_keys=[reply_to_user_id])
    reports = db.relationship("PlazaCommentReport", back_populates="comment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PlazaComment {self.id[:12]} status:{self.status}>"
