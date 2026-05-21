from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import validates

from .base import BaseModel, db


class FortuneRecord(BaseModel):
    """运势记录表"""

    __tablename__ = "fortune_records"
    __table_args__ = (
        db.UniqueConstraint("user_id", "date", name="uq_user_date"),
    )

    user_id = db.Column(db.String(64), db.ForeignKey("users.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True, comment="运势所属日期")

    score = db.Column(db.Integer, nullable=False, comment="运势分数0-100")
    title = db.Column(db.String(20), nullable=False, comment="运势标题")
    content = db.Column(db.String(200), nullable=False, comment="序列化运势内容")
    love = db.Column(db.String(20), nullable=False, comment="爱情运")
    career = db.Column(db.String(20), nullable=False, comment="事业运")
    health = db.Column(db.String(20), nullable=False, comment="健康运")
    wealth = db.Column(db.String(20), nullable=False, comment="财富运")

    yi = db.Column(ARRAY(db.String(20)), nullable=False, comment="宜事项, 2个")
    ji = db.Column(ARRAY(db.String(20)), nullable=False, comment="忌事项, 2个")
    gua_meaning_lines = db.Column(
        ARRAY(db.String(40)),
        nullable=False,
        comment="卦意",
    )
    lucky_hour_name = db.Column(db.String(20), nullable=False, comment="开运时辰名称")
    lucky_hour_range = db.Column(db.String(20), nullable=False, comment="开运时辰时间")

    user = db.relationship("User", back_populates="fortunes")
    plaza_card = db.relationship(
        "PlazaCard",
        back_populates="fortune",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @validates("score")
    def validate_score(self, _key, score):
        if not 0 <= score <= 100:
            raise ValueError("Score must be between 0 and 100")
        return score

    @validates("yi", "ji")
    def validate_arrays(self, key, value):
        if value and len(value) > 5:
            raise ValueError(f"{key} array cannot have more than 5 items")
        return value

    @validates("gua_meaning_lines")
    def validate_gua_lines(self, key, value):
        if not value or len(value) != 2:
            raise ValueError(f"{key} must contain exactly 2 items")
        return [str(item or "").strip()[:40] for item in value]

    def __repr__(self):
        return f"<FortuneRecord {self.date} User:{self.user_id} Score:{self.score}>"
