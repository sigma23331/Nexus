from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

fortune_bp = Blueprint('fortune', __name__)


@fortune_bp.route('/today', methods=['GET'])
@jwt_required()
def today_fortune():
    return jsonify(code=501, message="未实现", data=None), 501


@fortune_bp.route('/trend', methods=['GET'])
@jwt_required()
def fortune_trend():
    return jsonify(code=501, message="未实现", data=None), 501


@fortune_bp.route('/stats/global', methods=['GET'])
def global_stats():
    return jsonify(code=501, message="未实现", data=None), 501