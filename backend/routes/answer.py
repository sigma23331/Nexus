from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

answer_bp = Blueprint('answer', __name__)


@answer_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask_answer():
    return jsonify(code=501, message="未实现", data=None), 501


@answer_bp.route('/history', methods=['GET'])
@jwt_required()
def answer_history():
    return jsonify(code=501, message="未实现", data=None), 501


@answer_bp.route('/favorite', methods=['POST'])
@jwt_required()
def toggle_favorite():
    return jsonify(code=501, message="未实现", data=None), 501