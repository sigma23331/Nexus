from datetime import datetime
import uuid
from extensions import db

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)