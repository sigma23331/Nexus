from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

diary_bp = Blueprint('diary', __name__)


@diary_bp.route('/entry', methods=['POST'])
@jwt_required()
def save_entry():
    return jsonify(code=501, message="未实现", data=None), 501


@diary_bp.route('/timeline', methods=['GET'])
@jwt_required()
def get_timeline():
    return jsonify(code=501, message="未实现", data=None), 501


@diary_bp.route('/entry/<id>', methods=['GET'])
@jwt_required()
def get_entry(id):
    return jsonify(code=501, message="未实现", data=None), 501


@diary_bp.route('/entry/<id>', methods=['PUT'])
@jwt_required()
def update_entry(id):
    return jsonify(code=501, message="未实现", data=None), 501


@diary_bp.route('/entry/<id>', methods=['DELETE'])
@jwt_required()
def delete_entry(id):
    return jsonify(code=501, message="未实现", data=None), 501