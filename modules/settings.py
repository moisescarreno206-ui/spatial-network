from flask import Blueprint, jsonify, request
from config import LOCAL_DB

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/api/settings/virals', methods=['GET'])
def get_virals():
    creator = request.args.get('creator', '').strip().lower()
    virals_database = [
        {"creator": "amiti_official", "type": "video", "title": "Actualización Spatial V2", "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
        {"creator": "tech_master", "type": "image", "title": "Setup de desarrollo 2026", "url": "https://picsum.photos/400/300"},
        {"creator": "amiti_official", "type": "image", "title": "Próximos servidores globales", "url": "https://picsum.photos/401/300"}
    ]
    
    if creator:
        results = [v for v in virals_database if creator in v["creator"]]
    else:
        results = virals_database

    return jsonify({"status": "success", "items": results}), 200
  
