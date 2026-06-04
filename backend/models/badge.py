from datetime import date

from .base import BaseModel, db


class BadgeDefinition(BaseModel):
    __tablename__ = "badge_definitions"

    code = db.Column(db.String(64), nullable=False, unique=True, index=True)
    name = db.Column(db.String(32), nullable=False)
    category = db.Column(db.String(32), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False, default="")
    icon_url = db.Column(db.String(500), nullable=False, default="")
    gray_icon_url = db.Column(db.String(500), nullable=False, default="")
    sort_order = db.Column(db.Integer, nullable=False, default=0, index=True)
    enabled = db.Column(db.Boolean, nullable=False, default=True, index=True)

    levels = db.relationship(
        "BadgeLevel",
        back_populates="badge",
        cascade="all, delete-orphan",
        order_by="BadgeLevel.level.asc()",
    )
    user_badges = db.relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BadgeDefinition {self.code} {self.name}>"


class BadgeLevel(BaseModel):
    __tablename__ = "badge_levels"
    __table_args__ = (
        db.UniqueConstraint("badge_code", "level", name="uq_badge_level"),
    )

    badge_code = db.Column(db.String(64), db.ForeignKey("badge_definitions.code"), nullable=False, index=True)
    level = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(32), nullable=False)
    condition_type = db.Column(db.String(32), nullable=False)
    metric_key = db.Column(db.String(64), nullable=False, index=True)
    threshold = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")

    badge = db.relationship("BadgeDefinition", back_populates="levels")

    def __repr__(self):
        return f"<BadgeLevel {self.badge_code} Lv.{self.level}>"


class UserBadge(BaseModel):
    __tablename__ = "user_badges"
    __table_args__ = (
        db.UniqueConstraint("user_id", "badge_code", name="uq_user_badge"),
    )

    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=False, index=True)
    badge_code = db.Column(db.String(64), db.ForeignKey("badge_definitions.code"), nullable=False, index=True)
    level = db.Column(db.Integer, nullable=False, default=0)
    current_progress = db.Column(db.Integer, nullable=False, default=0)
    target = db.Column(db.Integer, nullable=False, default=1)
    unlocked_at = db.Column(db.DateTime, nullable=True)
    last_evaluated_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="badges")
    badge = db.relationship("BadgeDefinition", back_populates="user_badges")

    def __repr__(self):
        return f"<UserBadge user:{self.user_id} badge:{self.badge_code} level:{self.level}>"


class UserLoginDay(BaseModel):
    __tablename__ = "user_login_days"
    __table_args__ = (
        db.UniqueConstraint("user_id", "login_date", name="uq_user_login_day"),
    )

    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=False, index=True)
    login_date = db.Column(db.Date, nullable=False, default=date.today, index=True)

    user = db.relationship("User", back_populates="login_days")

    def __repr__(self):
        return f"<UserLoginDay user:{self.user_id} date:{self.login_date}>"
