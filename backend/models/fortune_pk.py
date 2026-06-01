import enum
from datetime import datetime

from sqlalchemy.orm import validates

from .base import BaseModel, db


class FortunePKResult(enum.Enum):
    CHALLENGER_WIN = "challenger_win"
    DEFENDER_WIN = "defender_win"
    DRAW = "draw"


class FortunePKStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    EXPIRED = "expired"


class FortunePKRecord(BaseModel):
    __tablename__ = "fortune_pk_records"

    token = db.Column(db.String(32), unique=True, nullable=False, index=True)
    challenger_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=False, index=True)
    challenger_score = db.Column(db.Integer, nullable=False)
    defender_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=True, index=True)
    defender_score = db.Column(db.Integer, nullable=True)
    result = db.Column(
        db.Enum(
            FortunePKResult,
            name="fortune_pk_result",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=True,
    )
    status = db.Column(
        db.Enum(
            FortunePKStatus,
            name="fortune_pk_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=FortunePKStatus.PENDING,
        server_default=FortunePKStatus.PENDING.value,
        index=True,
    )
    date = db.Column(db.Date, nullable=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    challenger = db.relationship(
        "User",
        foreign_keys=[challenger_id],
        back_populates="fortune_pk_challenges",
    )
    defender = db.relationship(
        "User",
        foreign_keys=[defender_id],
        back_populates="fortune_pk_defenses",
    )

    @validates("challenger_score", "defender_score")
    def validate_score(self, _key, score):
        if score is None:
            return score
        if not 0 <= score <= 100:
            raise ValueError("Score must be between 0 and 100")
        return score

    def complete(self, defender_id, defender_score):
        if defender_id == self.challenger_id:
            raise ValueError("Cannot PK with yourself")

        self.defender_id = defender_id
        self.defender_score = defender_score
        if self.challenger_score > defender_score:
            self.result = FortunePKResult.CHALLENGER_WIN
        elif self.challenger_score < defender_score:
            self.result = FortunePKResult.DEFENDER_WIN
        else:
            self.result = FortunePKResult.DRAW
        self.status = FortunePKStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def __repr__(self):
        return f"<FortunePKRecord {self.token} Status:{self.status.value}>"
