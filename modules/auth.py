import re
from flask import Blueprint, jsonify, request
from config import LOCAL_DB

auth_bp = Blueprint('auth', __name__)

def validate_identity(identity):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    phone_regex = r'^\+?[0-9]{7,15}$'
    clean = identity.replace(" ", "").replace("-", "")
    if re.match(email_regex, identity):
        return True, "email"
    elif re.match(phone_regex, clean):
        return True, "phone"
    return False, "invalid"

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    identity = data.get('identity', '').strip()
    password = data.get('password', '').strip()

    valid, id_type = validate_identity(identity)
    if not username or not valid or not password:
        return jsonify({"status": "error", "message": "Datos de registro inválidos"}), 400

    user_id = username.replace('@', '').lower()
    user_profile = {
        "id": user_id,
        "username": f"@{user_id}",
        "identity": identity,
        "identity_type": id_type,
        "avatar_url": f"https://api.dicebear.com/7.x/bottts/svg?seed={user_id}",
        "status_text": "¡Disponible en Spatial Network!",
        "privacy": "public",
        "theme_color": "#8b5cf6",
        "chat_bg": "#090810",
        "bubble_shape": "rounded"
    }

    LOCAL_DB["users"][user_id] = user_profile
    return jsonify({"status": "success", "user": user_profile}), 200

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    identity = data.get('identity', '').strip()
    password = data.get('password', '').strip()

    for u_id, u_data in LOCAL_DB["users"].items():
        if u_data.get("identity") == identity:
            return jsonify({"status": "success", "user": u_data}), 200

    # Auto-login de respaldo
    user_id = identity.split('@')[0].replace('+', '').lower()
    user_profile = {
        "id": user_id,
        "username": f"@{user_id}",
        "identity": identity,
        "avatar_url": f"https://api.dicebear.com/7.x/bottts/svg?seed={user_id}",
        "status_text": "¡Disponible en Spatial Network!",
        "privacy": "public",
        "theme_color": "#8b5cf6",
        "chat_bg": "#090810",
        "bubble_shape": "rounded"
    }
    LOCAL_DB["users"][user_id] = user_profile
    return jsonify({"status": "success", "user": user_profile}), 200
  
