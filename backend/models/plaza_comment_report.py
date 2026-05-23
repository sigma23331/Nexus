from .base import db, BaseModel


class PlazaCommentReport(BaseModel):
    __tablename__ = "plaza_comment_reports"
    __table_args__ = (
        db.UniqueConstraint("reporter_user_id", "comment_id", name="uq_reporter_comment"),
        db.Index("idx_plaza_comment_report_comment_status", "comment_id", "status"),
    )

    comment_id = db.Column(db.String(64), db.ForeignKey("plaza_comments.id"), nullable=False, index=True)
    reporter_user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=False, index=True)
    reason_code = db.Column(db.String(32), nullable=False)
    reason_text = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(16), nullable=False, default="open", index=True)

    comment = db.relationship("PlazaComment", back_populates="reports")
    reporter = db.relationship("User", foreign_keys=[reporter_user_id], back_populates="comment_reports")

    def __repr__(self):
        return f"<PlazaCommentReport {self.comment_id} {self.reason_code}>"
