from datetime import datetime

from .base import db


class MoodAnalysisJob(db.Model):
    __tablename__ = 'mood_analysis_jobs'

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    trigger_event = db.Column(db.String(32), nullable=False)
    window_days = db.Column(db.Integer, nullable=False, default=7)
    payload_json = db.Column(db.JSON, nullable=True)

    attempt_count = db.Column(db.Integer, nullable=False, default=0)
    max_attempts = db.Column(db.Integer, nullable=False, default=3)
    next_run_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    request_id = db.Column(db.String(64), nullable=False, unique=True)
    result_text = db.Column(db.String(64), nullable=True)
    error_message = db.Column(db.String(255), nullable=True)

    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = db.relationship('User')
