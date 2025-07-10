import jwt
import datetime
from flask import request, jsonify
from functools import wraps
from config import ACCESS_SECRET, REFRESH_SECRET

refresh_tokens = []

def generate_access_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)  # 10s for testing
    }
    return jwt.encode(payload, ACCESS_SECRET, algorithm='HS256')

def generate_refresh_token(username):
    payload = {
        'username': username
    }
    token = jwt.encode(payload, REFRESH_SECRET, algorithm='HS256')
    refresh_tokens.append(token)
    return token

def verify_refresh_token(token):
    try:
        if token not in refresh_tokens:
            return None
        payload = jwt.decode(token, REFRESH_SECRET, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def remove_refresh_token(token):
    if token in refresh_tokens:
        refresh_tokens.remove(token)

# ⛔ Protect routes with this decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({'error': 'Missing or invalid token'}), 401

        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, ACCESS_SECRET, algorithms=['HS256'])
            request.username = decoded['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Access token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated
