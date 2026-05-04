# main.py
import os
from datetime import datetime
from flask import Flask, jsonify, current_app
from sqlalchemy import text
from config import config
from extensions import db, migrate, cors, jwt


def create_app():
    app = Flask(__name__)

    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
    )

    # 根据环境加载配置
    env = os.getenv('FLASK_ENV', 'development')
    app.config['APP_ENV'] = env
    app.config.from_object(config.get(env, config['default']))

    # === 初始化扩展 ===
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/v1/*": {"origins": "*"}})
    jwt.init_app(app)

    # === 导入模型（必须放在这里，确保表被 SQLAlchemy 识别） ===
    with app.app_context():
        import models

    # 注册蓝图
    register_blueprints(app)

    # 注册全局错误处理
    register_error_handlers(app)

    # 基础路由（健康检查等）
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Nexus 后端服务运行中',
            'status': 'running',
            'endpoints': ['/health', '/v1/auth/...']
        })

    @app.route('/health')
    def health():
        try:
            db.session.execute(text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            current_app.logger.error(f'数据库连接失败: {str(e)}')
            db_status = 'disconnected'
        return jsonify({
            'status': 'healthy' if db_status == 'connected' else 'unhealthy',
            'database': db_status,
            'timestamp': datetime.utcnow().isoformat()
        })

    return app


def register_blueprints(app):
    from routes.auth_route import auth_bp
    from routes.user_route import user_bp
    from routes.fortune_route import fortune_bp
    from routes.answer_route import answer_bp
    from routes.plaza_route import plaza_bp
    from routes.diary_route import diary_bp
    from routes.prompt_lab_route import prompt_lab_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(fortune_bp, url_prefix='/fortune')
    app.register_blueprint(answer_bp, url_prefix='/answer')
    app.register_blueprint(plaza_bp, url_prefix='/plaza')
    app.register_blueprint(diary_bp, url_prefix='/diary')

    env = app.config.get('APP_ENV', 'development')
    if env in {'development', 'local'} and bool(app.config.get('PROMPT_LAB_DEV_ENABLED', False)):
        app.register_blueprint(prompt_lab_bp, url_prefix='/v1/dev/prompt-lab')


def register_error_handlers(app):
    """统一 JSON 错误响应"""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(code=400, message=str(e.description) if e.description else "参数错误", data=None), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify(code=401, message="Token 无效或已过期", data=None), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(code=403, message="无权限执行此操作", data=None), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(code=404, message="请求的资源不存在", data=None), 404

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify(code=429, message="请求过于频繁，请稍后再试", data=None), 429

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(code=500, message="服务器内部错误", data=None), 500


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
