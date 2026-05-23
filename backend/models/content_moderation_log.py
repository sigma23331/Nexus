from .base import db, BaseModel


class ContentModerationLog(BaseModel):
    __tablename__ = "content_moderation_logs"
    __table_args__ = (
        db.Index(
            "idx_content_moderation_target_created",
            "target_type",
            "target_id",
            "created_at",
        ),
    )

    scene = db.Column(db.String(64), nullable=False, index=True)
    target_type = db.Column(db.String(32), nullable=False, index=True)
    target_id = db.Column(db.String(64), nullable=True, index=True)
    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=True, index=True)

    original_text = db.Column(db.Text(), nullable=False)
    processed_text = db.Column(db.Text(), nullable=True)
    action = db.Column(db.String(16), nullable=False, index=True)
    severity = db.Column(db.String(16), nullable=False, default="low")
    labels = db.Column(db.JSON, nullable=True)
    reason_code = db.Column(db.String(64), nullable=True)
    provider_name = db.Column(db.String(32), nullable=True)
    provider_result = db.Column(db.JSON, nullable=True)

    user = db.relationship("User")

    def __repr__(self):
        return f"<ContentModerationLog {self.scene} {self.action}>"
