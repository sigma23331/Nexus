from functools import wraps

from flask import g, jsonify, request


def login_required(func):
    """
    Temporary auth middleware.

    TODO: Replace X-User-ID parsing with JWT verification when auth module is ready.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({
                'code': 401,
                'message': '请先登录',
                'data': None,
            }), 401

        g.user_id = user_id
        return func(*args, **kwargs)

    return wrapper
