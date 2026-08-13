from flask import Blueprint, jsonify, request
from config import LOCAL_DB
from datetime import datetime

chats_bp = Blueprint('chats', __name__)

@chats_bp.route('/api/chats/ops', methods=['POST'])
def chat_operations():
    data = request.get_json() or {}
    action = data.get('action') # vaciar, bloquear, reportar, crear_grupo, silenciar
    user_id = data.get('user_id')
    target_id = data.get('target_id')

    if action == 'vaciar':
        chat_key = f"{min(user_id, target_id)}_{max(user_id, target_id)}"
        LOCAL_DB["messages"][chat_key] = []
        return jsonify({"status": "success", "message": "Chat vaciado correctamente"})

    elif action == 'bloquear':
        if user_id not in LOCAL_DB["blocked"]:
            LOCAL_DB["blocked"][user_id] = []
        if target_id not in LOCAL_DB["blocked"][user_id]:
            LOCAL_DB["blocked"][user_id].append(target_id)
        return jsonify({"status": "success", "message": "Contacto bloqueado"})

    elif action == 'reportar':
        LOCAL_DB["reports"].append({"reporter": user_id, "reported": target_id, "date": datetime.utcnow().isoformat()})
        return jsonify({"status": "success", "message": "Contacto reportado al sistema"})

    elif action == 'crear_grupo':
        group_id = f"group_{len(LOCAL_DB['groups']) + 1}"
        new_group = {"id": group_id, "name": f"Grupo con {target_id}", "members": [user_id, target_id]}
        LOCAL_DB["groups"].append(new_group)
        return jsonify({"status": "success", "group": new_group})

    elif action == 'silenciar':
        return jsonify({"status": "success", "message": "Notificaciones de contacto silenciadas"})

    return jsonify({"status": "error", "message": "Acción no reconocida"}), 400
  
