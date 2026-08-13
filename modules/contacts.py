from flask import Blueprint, jsonify, request
from config import LOCAL_DB

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('/api/contacts/sync', methods=['POST'])
def sync_contacts():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    query = data.get('query', '').strip().replace('@', '').lower()

    contact_info = {
        "id": query,
        "username": f"@{query}",
        "avatar_url": f"https://api.dicebear.com/7.x/bottts/svg?seed={query}",
        "status_text": "Contacto sincronizado vía QR/Red"
    }

    if user_id not in LOCAL_DB["contacts"]:
        LOCAL_DB["contacts"][user_id] = []
    
    LOCAL_DB["contacts"][user_id].append(contact_info)
    return jsonify({"status": "success", "contact": contact_info}), 200
  
