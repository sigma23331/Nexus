# backend/routes/test.py
from flask import Blueprint, jsonify

test_bp = Blueprint('test', __name__)

@test_bp.route('/test')
def test():
    """测试接口 - 原app.py中的代码"""
    return jsonify({
        "message": "来自服务器后端的慰藉：连接成功！",
        "status": "success"
    })