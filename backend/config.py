import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123456'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('FLASK_ENV') == 'development'

    # JWT 配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 604800  # 7天（示例，按需调整）

    # LLM 配置
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'real')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL')
    LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME')
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    LLM_TIMEOUT = int(os.environ.get('LLM_TIMEOUT', '12'))
    LLM_MAX_RETRIES = int(os.environ.get('LLM_MAX_RETRIES', '1'))
    PROMPT_LAB_DEV_ENABLED = os.environ.get('PROMPT_LAB_DEV_ENABLED', 'false').lower() == 'true'
    LLM_PROMPTS_DIR = os.environ.get('LLM_PROMPTS_DIR')
    LLM_PROMPT_ANSWER_VERSION = os.environ.get('LLM_PROMPT_ANSWER_VERSION', 'v4')
    LLM_PROMPT_FORTUNE_VERSION = os.environ.get('LLM_PROMPT_FORTUNE_VERSION', 'v4')
    LLM_PROMPT_PROFILE_VERSION = os.environ.get('LLM_PROMPT_PROFILE_VERSION', 'v1')

    # 数据库配置
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    else:
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        DB_PORT = os.environ.get('DB_PORT', '5432')
        DB_NAME = os.environ.get('DB_NAME', 'nexus_db')
        DB_USER = os.environ.get('DB_USER', 'nexus_user')
        DB_PASSWORD = os.environ.get('DB_PASSWORD')
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    DEBUG = False
    _db_url = os.environ.get('DATABASE_URL')
    if not _db_url:
        raise ValueError("ProductionConfig: DATABASE_URL must be set in environment")
    SQLALCHEMY_DATABASE_URI = _db_url


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
