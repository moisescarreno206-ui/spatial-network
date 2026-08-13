from flask import Blueprint, jsonify, request
from config import LOCAL_DB
from datetime import datetime, timedelta

statuses_bp = Blueprint('statuses', __name__)

@statuses_bp.route('/api/statuses/publish', methods=['POST'])
def publish_status():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    username = data.get('username')
    content_type = data.get('type') # 'text' -> Historia, 'image'/'video' -> Estado
    content = data.get('content')
    expiry_hours = int(data.get('expiry_hours', 24))

    item = {
        "id": len(LOCAL_DB["statuses"]) + 1,
        "user_id": user_id,
        "username": username,
        "category": "Historia" if content_type == "text" else "Estado",
        "type": content_type,
        "content": content,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=expiry_hours)).isoformat()
    }
    LOCAL_DB["statuses"].append(item)
    return jsonify({"status": "success", "item": item}), 200

@statuses_bp.route('/api/statuses/list', methods=['GET'])
def list_statuses():
    now = datetime.utcnow()
    active_items = []
    for s in LOCAL_DB["statuses"]:
        expires = datetime.fromisoformat(s["expires_at"])
        if now < expires:
            active_items.append(s)
    return jsonify({"status": "success", "items": active_items}), 200

