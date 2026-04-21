# backend/main.py
import os
from datetime import datetime
from flask import Flask, jsonify, current_app
from sqlalchemy import text
from config import Config
from extensions import db, migrate, cors

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')

    # === 阶段1: 初始化扩展 ==
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # === 阶段2: 导入并注册模型 ===
    with app.app_context():
        import models

    # 注册蓝图
    register_blueprints(app)
    # 注册自定义命令
    register_commands(app)

    # 添加基础路由
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Nexus 后端服务运行中',
            'status': 'running',
            'endpoints': ['/api/test', '/health', '/api/test-db']
        })

    @app.route('/api/test')
    def test():
        return jsonify({
            'message': '来自服务器后端的慰藉：连接成功！',
            'status': 'success'
        })

    @app.route('/health')
    def health():
        """健康检查端点"""
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
    """注册所有蓝图"""
    from routes.test import test_bp
    from routes.auth import auth_bp
    app.register_blueprint(test_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/v1/auth')


def register_commands(app):
    """注册自定义命令"""
    @app.cli.command("init-db")
    def init_db():
        """初始化数据库（创建所有表）"""
        with app.app_context():
            try:
                # 由于模型已在create_app的with app.app_context()块中导入，
                # 此时db.metadata中已包含所有表定义。
                db.create_all()
                print("数据库初始化完成！")
                print("   表已创建: users, fortune_records, answer_records, diary_entries, plaza_cards, likes, favorites, sms_codes")
            except Exception as e:
                print(f"数据库初始化失败: {str(e)}")

    @app.cli.command("drop-db")
    def drop_db():
        """删除所有表（开发环境使用）"""
        confirm = input("确定要删除所有表吗？这将会清除所有数据！(输入 'yes' 确认): ")
        if confirm.lower() == 'yes':
            with app.app_context():
                db.drop_all()
                print("所有表已删除！")
        else:
            print("操作已取消")

    # === 将详细的 /api/test-db 路由定义也移到此处，避免重复定义 ===
    @app.route('/api/test-db')
    def test_db():
        """专门测试数据库连接和基本操作的端点"""
        try:
            result = db.session.execute(text('SELECT version()')).fetchone()
            db_version = result[0] if result else 'unknown'

            current_db = db.session.execute(text('SELECT current_database()')).fetchone()[0]
            current_schema = db.session.execute(text('SELECT current_schema()')).fetchone()[0]

            tables_result = db.session.execute(text("""
                SELECT schemaname, tablename 
                FROM pg_catalog.pg_tables 
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            """)).fetchall()

            table_exists = False
            try:
                db.session.execute(text("SELECT 1 FROM users LIMIT 0"))
                table_exists = True
            except:
                table_exists = False

            return jsonify({
                'status': 'success',
                'database': 'connected',
                'current_database': current_db,
                'current_schema': current_schema,
                'tables': [{'schema': row[0], 'table': row[1]} for row in tables_result],
                'tables_initialized': table_exists,
                'timestamp': datetime.utcnow().isoformat(),
                'message': '数据库连接测试成功'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'message': '数据库连接测试失败'
            }), 500


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)