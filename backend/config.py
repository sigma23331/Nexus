import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123456'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('FLASK_ENV') == 'development'

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 604800

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

    SMS_PROVIDER = os.environ.get('SMS_PROVIDER', 'mock')
    SMS_SIGN_NAME = os.environ.get('SMS_SIGN_NAME', '速通互联验证码')
    SMS_TEMPLATE_CODE = os.environ.get('SMS_TEMPLATE_CODE', '100001')
    SMS_CODE_LENGTH = int(os.environ.get('SMS_CODE_LENGTH', '6'))
    SMS_SEND_INTERVAL = int(os.environ.get('SMS_SEND_INTERVAL', '60'))
    SLIDER_CAPTCHA_REQUIRED = os.environ.get('SLIDER_CAPTCHA_REQUIRED', 'true').lower() == 'true'
    DYPNS_API_ENDPOINT = os.environ.get('DYPNS_API_ENDPOINT', 'dypnsapi.aliyuncs.com')
    ALIYUN_GREEN_ENABLED = os.environ.get('ALIYUN_GREEN_ENABLED', 'false').lower() == 'true'
    ALIYUN_GREEN_REGION = os.environ.get('ALIYUN_GREEN_REGION', 'cn-shanghai')
    ALIYUN_GREEN_ENDPOINT = os.environ.get('ALIYUN_GREEN_ENDPOINT', 'green.cn-shanghai.aliyuncs.com')
    ALIYUN_GREEN_TIMEOUT = int(os.environ.get('ALIYUN_GREEN_TIMEOUT', '3'))
    ALIYUN_GREEN_FAIL_OPEN = os.environ.get('ALIYUN_GREEN_FAIL_OPEN', 'false').lower() == 'true'

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

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.environ.get("DB_POOL_SIZE", "20")),
        "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "10")),
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }

    PASSWORD_HASH_METHOD = os.environ.get("PASSWORD_HASH_METHOD", "pbkdf2:sha256")


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
