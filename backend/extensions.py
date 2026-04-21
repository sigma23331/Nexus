# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# 创建扩展实例
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()