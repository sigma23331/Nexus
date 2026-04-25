from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

plaza_bp = Blueprint('plaza', __name__)


@plaza_bp.route('/cards', methods=['GET'])
def get_cards():
    return jsonify(code=501, message="未实现", data=None), 501


@plaza_bp.route('/card', methods=['POST'])
@jwt_required()
def post_card():
    return jsonify(code=501, message="未实现", data=None), 501


@plaza_bp.route('/like', methods=['POST'])
@jwt_required()
def toggle_like():
    return jsonify(code=501, message="未实现", data=None), 501