import os
import json
from datetime import datetime, timedelta
import requests
from flask import Flask, render_template_string, jsonify, request, Response

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "mensajeria-especial-key-2026")

# ==========================================
# CONFIGURACIÓN Y VARIABLES DE ENTORNO
# ==========================================
PORT = int(os.environ.get("PORT", 5000))
SERVIDOR_1_URL = os.environ.get("SERVIDOR_1_URL", "https://amiti-spatial-network.onrender.com")
TOKEN_ENLACE = os.environ.get("TOKEN_ENLACE", "spatial-secure-token-2026")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xyzcompany.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "public-anon-key")

# ==========================================
# CLIENTE SUPABASE REAL
# ==========================================
supabase_client = None
if "supabase.co" in SUPABASE_URL and SUPABASE_KEY != "public-anon-key":
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ [Mensajería Especial] Supabase conectado correctamente.")
    except Exception as e:
        print(f"⚠️ [Mensajería Especial] Supabase operando en modo contingencia: {e}")

# ==========================================
# ENDPOINTS API REST (BACKEND COMPLETO)
# ==========================================

# --- PERFILES Y AUTENTICACIÓN ---
@app.route('/api/auth/sync_profile', methods=['POST'])
def sync_profile():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    handle = data.get('handle')
    name = data.get('name')
    avatar_url = data.get('avatar_url', 'https://cdn-icons-png.flaticon.com/512/149/149071.png')

    if not user_id or not handle or not name:
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400

    profile_data = {
        "id": user_id,
        "handle": handle if handle.startswith('@') else f"@{handle}",
        "name": name,
        "avatar_url": avatar_url
    }

    if supabase_client:
        try:
            supabase_client.table('profiles').upsert(profile_data).execute()
        except Exception as e:
            print(f"Error upsert profile: {e}")

    return jsonify({"status": "success", "profile": profile_data}), 200

# --- ESCÁNER Y CONTACTOS CON AVATAR REAL ---
@app.route('/api/auth/scan_qr', methods=['POST'])
def scan_qr():
    data = request.get_json() or {}
    current_user_id = data.get('user_id')
    scanned_handle = data.get('scanned_handle', '').strip()

    if not current_user_id or not scanned_handle:
        return jsonify({"status": "error", "message": "Escaneo inválido"}), 400

    if not scanned_handle.startswith('@'):
        scanned_handle = f"@{scanned_handle}"

    contact_profile = None
    if supabase_client:
        try:
            res = supabase_client.table('profiles').select('*').eq('handle', scanned_handle).execute()
            if res.data:
                contact_profile = res.data[0]
        except Exception as e:
            print(f"Error buscando contacto: {e}")

    # Si no se encuentra en DB, genera la estructura real sincronizada
    if not contact_profile:
        contact_id = scanned_handle.replace('@', '').lower()
        contact_profile = {
            "id": contact_id,
            "name": contact_id.capitalize(),
            "handle": scanned_handle,
            "avatar_url": f"https://api.dicebear.com/7.x/bottts/svg?seed={contact_id}"
        }

    # Vincular en tabla de contactos
    if supabase_client and current_user_id != contact_profile['id']:
        try:
            supabase_client.table('contacts').insert([
                {"user_id": current_user_id, "contact_id": contact_profile['id']}
            ]).execute()
        except Exception:
            pass

    return jsonify({
        "status": "success",
        "message": "Código ya escaneado",
        "contact": contact_profile
    }), 200

# --- MENSAJERÍA REAL Y ACCIONES WHATSAPP (BLOQUEAR, VACÍAR, REPORTAR) ---
@app.route('/api/chat/send', methods=['POST'])
def send_message():
    data = request.get_json() or {}
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()
    is_group = data.get('is_group', False)

    if not sender_id or not receiver_id or not content:
        return jsonify({"status": "error", "message": "Campos incompletos"}), 400

    # Comprobar bloqueo
    if supabase_client and not is_group:
        try:
            blocked = supabase_client.table('blocked_users').select('*').eq('user_id', receiver_id).eq('blocked_id', sender_id).execute()
            if blocked.data:
                return jsonify({"status": "error", "message": "No puedes enviar mensajes a este usuario"}), 403
        except Exception:
            pass

    msg_obj = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "content": content,
        "is_group": is_group
    }

    if supabase_client:
        try:
            supabase_client.table('messages').insert([msg_obj]).execute()
        except Exception as e:
            print(f"Error guardando mensaje: {e}")

    return jsonify({"status": "success", "message": "Mensaje enviado", "data": msg_obj}), 200

@app.route('/api/chat/history/<user_id>/<target_id>', methods=['GET'])
def get_chat_history(user_id, target_id):
    messages = []
    if supabase_client:
        try:
            q = f"and(sender_id.eq.{user_id},receiver_id.eq.{target_id}),and(sender_id.eq.{target_id},receiver_id.eq.{user_id})"
            res = supabase_client.table('messages').select('*').or_(q).order('created_at', ascending=True).execute()
            messages = res.data
        except Exception as e:
            print(f"Error consultando historial: {e}")

    return jsonify({"status": "success", "messages": messages}), 200

@app.route('/api/chat/block', methods=['POST'])
def block_user():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    blocked_id = data.get('blocked_id')
    if supabase_client and user_id and blocked_id:
        try:
            supabase_client.table('blocked_users').insert([{"user_id": user_id, "blocked_id": blocked_id}]).execute()
        except Exception:
            pass
    return jsonify({"status": "success", "message": "Usuario bloqueado"}), 200

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    target_id = data.get('target_id')
    if supabase_client and user_id and target_id:
        try:
            supabase_client.table('messages').delete().or_(f"and(sender_id.eq.{user_id},receiver_id.eq.{target_id}),and(sender_id.eq.{target_id},receiver_id.eq.{user_id})").execute()
        except Exception:
            pass
    return jsonify({"status": "success", "message": "Chat vaciado"}), 200

# --- CANAL AMITI (CENTRO DE MANDO / REPOS) ---
@app.route('/api/amiti/soporte', methods=['POST'])
def amiti_soporte():
    data = request.get_json() or {}
    user_id = data.get('user_id', 'anonimo')
    descripcion = data.get('descripcion', '')

    payload = {
        "origen": "Mensajeria_Especial",
        "user_id": user_id,
        "extension": "soporte_tecnico",
        "detalles": descripcion
    }
    
    try:
        res = requests.post(f"{SERVIDOR_1_URL.rstrip('/')}/api/v1/soporte_entrante", json=payload, headers={"Authorization": f"Bearer {TOKEN_ENLACE}"}, timeout=8)
        return jsonify({"status": "success", "respuesta_s1": res.json() if res.status_code == 200 else "Reporte en cola"}), 200
    except Exception as e:
        return jsonify({"status": "warning", "message": f"Amiti S1 no disponible: {e}"}), 200

# --- HISTORIAS (ESTADOS ESTILO FACEBOOK 24H) ---
@app.route('/api/social/stories/active', methods=['GET'])
def get_active_stories():
    historias = []
    if supabase_client:
        try:
            hace_24h = (datetime.utcnow() - timedelta(hours=24)).isoformat()
            res = supabase_client.table('stories').select('*, profiles(*)').gte('created_at', hace_24h).order('created_at', ascending=False).execute()
            historias = res.data
        except Exception as e:
            print(f"Error obteniendo historias: {e}")

    return jsonify({"status": "success", "stories": historias}), 200

@app.route('/api/social/stories/create', methods=['POST'])
def create_story():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    media_url = data.get('media_url')
    caption = data.get('caption', '')

    if supabase_client and user_id and media_url:
        try:
            supabase_client.table('stories').insert([{
                "user_id": user_id,
                "media_url": media_url,
                "caption": caption
            }]).execute()
        except Exception as e:
            print(f"Error al crear historia: {e}")

    return jsonify({"status": "success", "message": "Estado publicado con duración de 24 horas"}), 200

# --- GRUPOS Y COMUNIDADES ---
@app.route('/api/social/groups/create', methods=['POST'])
def create_group():
    data = request.get_json() or {}
    group_id = data.get('group_id')
    name = data.get('name')
    created_by = data.get('user_id')
    community_id = data.get('community_id', None)

    if supabase_client and group_id and name and created_by:
        try:
            supabase_client.table('groups').insert([{
                "id": group_id, "name": name, "created_by": created_by, "community_id": community_id
            }]).execute()
            supabase_client.table('group_members').insert([{
                "group_id": group_id, "user_id": created_by, "role": "admin"
            }]).execute()
        except Exception as e:
            print(f"Error creando grupo: {e}")

    return jsonify({"status": "success", "message": f"Grupo '{name}' creado exitosamente"}), 200

# --- FEED DE VIDEOS (REPÚBLICA TIKTOK) ---
@app.route('/api/social/videos/feed', methods=['GET'])
def get_video_feed():
    videos = [
        {"id": 1, "video_url": "https://www.w3schools.com/html/mov_bbb.mp4", "author": "@amiti_core", "desc": "Nodo central de Mensajería Especial activo."},
        {"id": 2, "video_url": "https://www.w3schools.com/html/movie.mp4", "author": "@red_espacial", "desc": "Transmisión en directo del feed de contenidos."}
    ]
    if supabase_client:
        try:
            res = supabase_client.table('videos').select('*, profiles(*)').order('created_at', ascending=False).execute()
            if res.data:
                videos = res.data
        except Exception as e:
            print(f"Error obteniendo videos: {e}")

    return jsonify({"status": "success", "videos": videos}), 200

# ==========================================
# MANIFEST & SERVICE WORKER (PWA)
# ==========================================
@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Mensajería Especial",
        "short_name": "Mensajería",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#050508",
        "theme_color": "#10b981"
    })

@app.route('/sw.js')
def service_worker():
    return Response("self.addEventListener('fetch', function(e){});", mimetype='application/javascript')

# ==========================================
# INTERFAZ FRONTEND MAESTRA (SINGLE PAGE)
# ==========================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Mensajería Especial</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#050508">

    <!-- Librerías Externas JS -->
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrious/4.0.2/qrious.min.js"></script>
    <script src="https://unpkg.com/html5-qrcode"></script>

    <style>
        :root {
            --bg-dark: #050508;
            --bg-card: #0f111a;
            --bg-input: #181b26;
            --accent: #10b981;
            --accent-hover: #059669;
            --amiti-purple: #7c3aed;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border: #1f2433;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background-color: var(--bg-dark); color: var(--text-main); height: 100vh; width: 100vw; display: flex; flex-direction: column; overflow: hidden; }

        .view { display: none; flex: 1; flex-direction: column; height: calc(100vh - 60px); overflow: hidden; position: relative; }
        .view.active { display: flex; }

        /* Login Screen */
        .auth-container { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 24px; background: radial-gradient(circle at center, #062e22 0%, var(--bg-dark) 100%); }
        .auth-box { width: 100%; max-width: 380px; background: var(--bg-card); border: 1px solid var(--border); padding: 28px; border-radius: 20px; display: flex; flex-direction: column; gap: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }

        .input-field { background: var(--bg-input); border: 1px solid var(--border); padding: 14px; border-radius: 12px; color: white; outline: none; font-size: 15px; width: 100%; }
        .input-field:focus { border-color: var(--accent); }
        .btn-primary { background: var(--accent); color: white; border: none; padding: 14px; border-radius: 12px; font-weight: bold; font-size: 15px; cursor: pointer; text-align: center; }
        .btn-primary:active { background: var(--accent-hover); }

        /* Bottom Nav Bar */
        .nav-bar { display: flex; background: var(--bg-card); border-top: 1px solid var(--border); height: 60px; position: fixed; bottom: 0; left: 0; right: 0; z-index: 50; }
        .nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; color: var(--text-muted); font-size: 10px; cursor: pointer; }
        .nav-item.active { color: var(--accent); font-weight: bold; }

        .header-bar { padding: 14px 16px; background: var(--bg-card); border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-weight: bold; font-size: 16px; }

        /* Layout de Estados Estilo Facebook */
        .facebook-stories-wrapper { display: flex; gap: 12px; padding: 14px; overflow-x: auto; background: var(--bg-card); border-bottom: 1px solid var(--border); }
        .fb-story-card { width: 90px; height: 130px; border-radius: 14px; background: var(--bg-input); border: 1px solid var(--border); display: flex; flex-direction: column; justify-content: space-between; padding: 8px; position: relative; flex-shrink: 0; cursor: pointer; background-size: cover; background-position: center; }
        .fb-story-avatar { width: 32px; height: 32px; border-radius: 50%; border: 2px solid var(--accent); object-fit: cover; }
        .fb-story-name { font-size: 11px; font-weight: bold; color: white; text-shadow: 0 1px 3px rgba(0,0,0,0.8); }

        /* Canales y Comunidades Abajo de Estados */
        .channels-section { padding: 12px 16px; background: var(--bg-dark); border-bottom: 1px solid var(--border); }
        .channel-chip { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 20px; font-size: 12px; margin-right: 8px; cursor: pointer; }

        /* Elementos de Chat */
        .chat-list { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 10px; }
        .chat-item { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 12px; display: flex; align-items: center; gap: 12px; cursor: pointer; }
        .chat-item img { width: 48px; height: 48px; border-radius: 50%; object-fit: cover; }
        .chat-info { flex: 1; }
        .chat-info strong { display: block; font-size: 15px; }
        .chat-info span { font-size: 12px; color: var(--text-muted); }

        /* Sala de Chat */
        .chat-messages { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; background: #08090f; }
        .message-bubble { max-width: 82%; padding: 12px 16px; border-radius: 18px; font-size: 14px; line-height: 1.4; word-break: break-word; }
        .message-bubble.sent { background: var(--accent); color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
        .message-bubble.received { background: var(--bg-input); color: var(--text-main); align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid var(--border); }

        /* Feed TikTok Video */
        .tiktok-feed { flex: 1; overflow-y: scroll; scroll-snap-type: y mandatory; background: #000; height: 100%; }
        .tiktok-card { height: 100%; width: 100%; scroll-snap-align: start; scroll-snap-stop: always; position: relative; display: flex; justify-content: center; align-items: center; background: #000; }
        .tiktok-card video, .tiktok-card iframe { width: 100%; height: 100%; object-fit: cover; border: none; }
        .tiktok-overlay { position: absolute; bottom: 20px; left: 16px; right: 16px; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.8); z-index: 10; pointer-events: none; }

        /* Toast / Notificación */
        .toast { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: var(--accent); color: white; padding: 12px 24px; border-radius: 30px; font-weight: bold; font-size: 14px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); z-index: 200; display: none; }

        /* Modales */
        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 100; flex-direction: column; justify-content: center; align-items: center; padding: 20px; }
        .modal.active { display: flex; }
        .modal-content { background: var(--bg-card); border-radius: 20px; padding: 20px; border: 1px solid var(--border); width: 100%; max-width: 400px; display: flex; flex-direction: column; gap: 14px; }
    </style>
</head>
<body>

    <div id="toast" class="toast">Código ya escaneado</div>

    <!-- VISTA 0: REGISTRO / LOGIN -->
    <div id="view-auth" class="view active" style="height: 100vh;">
        <div class="auth-container">
            <div class="auth-box">
                <h2 style="color:var(--accent); text-align:center;">Mensajería Especial</h2>
                <p style="color:var(--text-muted); font-size:13px; text-align:center;">Red Social & Mensajería Espacial</p>
                <input type="text" id="auth-name" class="input-field" placeholder="Tu Nombre">
                <input type="text" id="auth-handle" class="input-field" placeholder="@usuario">
                <input type="text" id="auth-avatar" class="input-field" placeholder="URL Foto de Perfil (Opcional)">
                <button class="btn-primary" onclick="iniciarSesion()">Ingresar al Sistema</button>
            </div>
        </div>
    </div>

    <!-- VISTA 1: CHATS, ESTADOS FACEBOOK Y CANALES -->
    <div id="view-chats" class="view">
        <div class="header-bar">
            <span>Mensajería</span>
            <button class="btn-primary" style="padding: 6px 12px; font-size:12px;" onclick="abrirModal('modal-qr')">📷 Mi QR / Escanear</button>
        </div>

        <!-- Estados Estilo Facebook (Arriba a la Izquierda) -->
        <div class="facebook-stories-wrapper" id="stories-wrapper">
            <div class="fb-story-card" style="background-color: var(--bg-input);" onclick="publicarEstado()">
                <div style="font-size:24px; text-align:center; margin-top:20px; color:var(--accent);">+</div>
                <div class="fb-story-name">Crear Estado</div>
            </div>
        </div>

        <!-- Lista de Canales y Comunidades Abajo -->
        <div class="channels-section">
            <div style="font-size:12px; color:var(--text-muted); margin-bottom:6px;">Canales y Comunidades Nativas</div>
            <div style="overflow-x:auto; white-space:nowrap;">
                <div class="channel-chip" onclick="abrirChatCon('comunidad_oficial', '🌐 Comunidad Oficial', 'https://cdn-icons-png.flaticon.com/512/3820/3820107.png')">🌐 Comunidad Oficial</div>
                <div class="channel-chip" onclick="abrirChatCon('amiti_soporte', '🤖 Amiti Soporte S1', 'https://cdn-icons-png.flaticon.com/512/4712/4712035.png')">🤖 Amiti Soporte</div>
            </div>
        </div>

        <!-- Lista de Chats con Fotos Reales -->
        <div id="chats-list" class="chat-list"></div>
    </div>

    <!-- VISTA 2: SALA DE CHAT EN TIEMPO REAL -->
    <div id="view-room" class="view">
        <div class="header-bar">
            <div style="display:flex; align-items:center; gap:10px;">
                <button onclick="cerrarChat()" style="background:none; border:none; color:white; font-size:20px; cursor:pointer;">←</button>
                <img id="room-avatar" src="" style="width:36px; height:36px; border-radius:50%; object-fit:cover;">
                <span id="room-title">@Chat</span>
            </div>
            <button onclick="abrirModal('modal-options')" style="background:none; border:none; color:white; font-size:20px;">⋮</button>
        </div>
        <div id="chat-messages" class="chat-messages"></div>
        <div style="padding: 12px; background: var(--bg-card); border-top: 1px solid var(--border); display: flex; gap: 8px;">
            <input type="text" id="message-input" class="input-field" style="flex:1;" placeholder="Escribe un mensaje..." onkeypress="if(event.key==='Enter') enviarMensaje()">
            <button class="btn-primary" style="padding:0 18px;" onclick="enviarMensaje()">➤</button>
        </div>
    </div>

    <!-- VISTA 3: GRUPOS Y COMUNIDADES -->
    <div id="view-groups" class="view">
        <div class="header-bar">
            <span>Grupos & Comunidades</span>
            <button class="btn-primary" style="padding: 6px 12px; font-size:12px;" onclick="crearGrupo()">+ Nuevo Grupo</button>
        </div>
        <div class="chat-list" id="groups-list">
            <div class="chat-item" onclick="abrirChatCon('grupo_general', '👥 Grupo de Desarrolladores', 'https://cdn-icons-png.flaticon.com/512/615/615075.png')">
                <img src="https://cdn-icons-png.flaticon.com/512/615/615075.png">
                <div class="chat-info">
                    <strong>👥 Grupo de Desarrolladores</strong>
                    <span>Comunidad General de la Mensajería</span>
                </div>
            </div>
        </div>
    </div>

    <!-- VISTA 4: REPRODUCTOR TIKTOK DE VIDEOS -->
    <div id="view-videos" class="view">
        <div id="tiktok-feed" class="tiktok-feed"></div>
    </div>

    <!-- VISTA 5: MENU AJUSTES PRESERVADO -->
    <div id="view-menu" class="view">
        <div class="header-bar">Ajustes del Sistema</div>
        <div style="padding: 16px; display: flex; flex-direction: column; gap: 14px;">
            <div style="background:var(--bg-card); padding:16px; border-radius:14px; border:1px solid var(--border); display:flex; align-items:center; gap:12px;">
                <img id="menu-avatar-img" src="" style="width:50px; height:50px; border-radius:50%;">
                <div>
                    <div style="font-weight:bold;" id="menu-user-name">Usuario</div>
                    <div style="color:var(--text-muted); font-size:13px;" id="menu-user-handle">@handle</div>
                </div>
            </div>
            <button class="btn-primary" style="background:#374151;" onclick="cerrarSesion()">Cerrar Sesión</button>
        </div>
    </div>

    <!-- NAVEGACIÓN INFERIOR DE 5 PESTAÑAS -->
    <div id="main-nav" class="nav-bar" style="display:none;">
        <div class="nav-item active" id="nav-chats" onclick="cambiarTab('chats')">💬 Chats</div>
        <div class="nav-item" id="nav-groups" onclick="cambiarTab('groups')">👥 Grupos</div>
        <div class="nav-item" id="nav-videos" onclick="cambiarTab('videos')">▶️ Videos</div>
        <div class="nav-item" id="nav-menu" onclick="cambiarTab('menu')">⚙️ Ajustes</div>
    </div>

    <!-- MODAL OPCIONES WHATSAPP -->
    <div id="modal-options" class="modal">
        <div class="modal-content">
            <h3>Opciones de Chat</h3>
            <button class="btn-primary" style="background:#dc2626;" onclick="bloquearContacto()">Bloquear Contacto</button>
            <button class="btn-primary" style="background:#d97706;" onclick="reportarContacto()">Reportar / Falla a Amiti</button>
            <button class="btn-primary" style="background:#4b5563;" onclick="vaciarChatActual()">Vaciar Chat</button>
            <button class="btn-primary" style="background:#1f2937;" onclick="cerrarModal('modal-options')">Cancelar</button>
        </div>
    </div>

    <!-- MODAL QR Y ESCÁNER -->
    <div id="modal-qr" class="modal">
        <div class="modal-content">
            <h3 style="text-align:center;">Tu Código QR</h3>
            <div style="display:flex; justify-content:center; padding:10px;"><canvas id="qr-canvas"></canvas></div>
            <div id="qr-reader" style="width:100%;"></div>
            <button class="btn-primary" onclick="iniciarEscaner()">📷 Escanear Cámara</button>
            <button class="btn-primary" style="background:#374151;" onclick="cerrarModal('modal-qr')">Cerrar</button>
        </div>
    </div>

    <script>
        let usuario = JSON.parse(localStorage.getItem('mensajeria_especial_user')) || null;
        let chatActivo = null;
        let contactos = JSON.parse(localStorage.getItem('mensajeria_especial_contacts')) || [
            { id: 'amiti_soporte', name: 'Amiti IA (Centro de Mando)', handle: '@amiti_s1', avatar_url: 'https://cdn-icons-png.flaticon.com/512/4712/4712035.png' }
        ];

        window.onload = () => {
            if (usuario) iniciarApp();
        };

        function iniciarSesion() {
            const name = document.getElementById('auth-name').value.trim();
            const handle = document.getElementById('auth-handle').value.trim();
            let avatar = document.getElementById('auth-avatar').value.trim();

            if(!name || !handle) return alert('Por favor completa los campos requeridos');
            if(!avatar) avatar = `https://api.dicebear.com/7.x/bottts/svg?seed=${handle}`;

            usuario = { id: handle.replace('@','').toLowerCase(), name, handle: handle.startsWith('@')?handle:'@'+handle, avatar_url: avatar };
            localStorage.setItem('mensajeria_especial_user', JSON.stringify(usuario));

            fetch('/api/auth/sync_profile', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(usuario)
            });

            iniciarApp();
        }

        function cerrarSesion() {
            localStorage.removeItem('mensajeria_especial_user');
            location.reload();
        }

        function iniciarApp() {
            document.getElementById('view-auth').classList.remove('active');
            document.getElementById('main-nav').style.display = 'flex';
            document.getElementById('menu-user-name').innerText = usuario.name;
            document.getElementById('menu-user-handle').innerText = usuario.handle;
            document.getElementById('menu-avatar-img').src = usuario.avatar_url;

            generarQR();
            cargarListaChats();
            cargarEstadosFacebook();
            cargarVideosFeed();
            cambiarTab('chats');
            setInterval(sincronizarMensajes, 3000);
        }

        function cambiarTab(tab) {
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            
            const viewTarget = document.getElementById(`view-${tab}`);
            const navTarget = document.getElementById(`nav-${tab}`);
            if(viewTarget) viewTarget.classList.add('active');
            if(navTarget) navTarget.classList.add('active');
        }

        function cargarListaChats() {
            const list = document.getElementById('chats-list');
            list.innerHTML = '';
            contactos.forEach(c => {
                const item = document.createElement('div');
                item.className = 'chat-item';
                item.onclick = () => abrirChatCon(c.id, c.name, c.avatar_url);
                item.innerHTML = `
                    <img src="${c.avatar_url}">
                    <div class="chat-info">
                        <strong>${c.name}</strong>
                        <span>${c.handle}</span>
                    </div>
                `;
                list.appendChild(item);
            });
        }

        function abrirChatCon(id, nombre, avatar) {
            chatActivo = { id, nombre, avatar };
            document.getElementById('room-title').innerText = nombre;
            document.getElementById('room-avatar').src = avatar;
            document.getElementById('chat-messages').innerHTML = '';
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.getElementById('view-room').classList.add('active');
            sincronizarMensajes();
        }

        function cerrarChat() {
            chatActivo = null;
            cambiarTab('chats');
        }

        async function enviarMensaje() {
            const input = document.getElementById('message-input');
            const texto = input.value.trim();
            if(!texto || !chatActivo) return;

            renderBubble(texto, 'sent');
            input.value = '';

            if (chatActivo.id === 'amiti_soporte') {
                fetch('/api/amiti/soporte', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ user_id: usuario.id, descripcion: texto })
                });
            } else {
                fetch('/api/chat/send', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ sender_id: usuario.id, receiver_id: chatActivo.id, content: texto })
                });
            }
        }

        async function sincronizarMensajes() {
            if(!chatActivo) return;
            const res = await fetch(`/api/chat/history/${usuario.id}/${chatActivo.id}`);
            const data = await res.json();
            if(data.messages) {
                const box = document.getElementById('chat-messages');
                box.innerHTML = '';
                data.messages.forEach(m => {
                    renderBubble(m.content, m.sender_id === usuario.id ? 'sent' : 'received');
                });
            }
        }

        function renderBubble(txt, classType) {
            const box = document.getElementById('chat-messages');
            const div = document.createElement('div');
            div.className = `message-bubble ${classType}`;
            div.innerText = txt;
            box.appendChild(div);
            box.scrollTop = box.scrollHeight;
        }

        function cargarEstadosFacebook() {
            fetch('/api/social/stories/active').then(r => r.json()).then(data => {
                const wrapper = document.getElementById('stories-wrapper');
                if(data.stories) {
                    data.stories.forEach(s => {
                        const card = document.createElement('div');
                        card.className = 'fb-story-card';
                        card.style.backgroundImage = `url(${s.media_url})`;
                        card.innerHTML = `<img src="${s.profiles?.avatar_url || usuario.avatar_url}" class="fb-story-avatar"><div class="fb-story-name">${s.profiles?.name || 'Usuario'}</div>`;
                        card.onclick = () => alert(`Estado de ${s.profiles?.name}: ${s.caption}`);
                        wrapper.appendChild(card);
                    });
                }
            });
        }

        function publicarEstado() {
            const url = prompt("Ingresa la URL de la imagen o foto para tu Estado (24h):");
            const caption = prompt("Escribe un texto / descripción:");
            if(url) {
                fetch('/api/social/stories/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ user_id: usuario.id, media_url: url, caption })
                }).then(() => cargarEstadosFacebook());
            }
        }

        function cargarVideosFeed() {
            fetch('/api/social/videos/feed').then(r => r.json()).then(data => {
                const feed = document.getElementById('tiktok-feed');
                feed.innerHTML = '';
                data.videos.forEach(v => {
                    const card = document.createElement('div');
                    card.className = 'tiktok-card';
                    card.innerHTML = `<video src="${v.video_url}" controls loop playsinline></video><div class="tiktok-overlay"><strong>${v.author || '@usuario'}</strong><p>${v.desc || ''}</p></div>`;
                    feed.appendChild(card);
                });
            });
        }

        function generarQR() {
            new QRious({
                element: document.getElementById('qr-canvas'),
                value: usuario ? usuario.handle : '@usuario',
                size: 180, background: '#0f111a', foreground: '#10b981'
            });
        }

        function iniciarEscaner() {
            const html5QrCode = new Html5Qrcode("qr-reader");
            html5QrCode.start(
                { facingMode: "environment" }, { fps: 10, qrbox: 220 },
                async (decodedText) => {
                    html5QrCode.stop();
                    cerrarModal('modal-qr');

                    // Alerta "Código ya escaneado"
                    const toast = document.getElementById('toast');
                    toast.style.display = 'block';
                    setTimeout(() => toast.style.display = 'none', 2500);

                    // Sincronizar contacto real en backend
                    const res = await fetch('/api/auth/scan_qr', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ user_id: usuario.id, scanned_handle: decodedText })
                    });
                    const data = await res.json();
                    if(data.contact) {
                        contactos.unshift(data.contact);
                        localStorage.setItem('mensajeria_especial_contacts', JSON.stringify(contactos));
                        cargarListaChats();
                    }
                }
            );
        }

        function bloquearContacto() {
            if(!chatActivo) return;
            fetch('/api/chat/block', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: usuario.id, blocked_id: chatActivo.id })
            }).then(() => { alert("Contacto Bloqueado"); cerrarModal('modal-options'); cerrarChat(); });
        }

        function reportarContacto() {
            if(!chatActivo) return;
            const razon = prompt("Escribe el motivo del reporte o falla:");
            if(razon) {
                fetch('/api/amiti/soporte', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ user_id: usuario.id, descripcion: `Reporte contra ${chatActivo.id}: ${razon}` })
                }).then(() => { alert("Reporte enviado a Amiti"); cerrarModal('modal-options'); });
            }
        }

        function vaciarChatActual() {
            if(!chatActivo) return;
            fetch('/api/chat/clear', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: usuario.id, target_id: chatActivo.id })
            }).then(() => { document.getElementById('chat-messages').innerHTML = ''; cerrarModal('modal-options'); });
        }

        function crearGrupo() {
            const name = prompt("Nombre del grupo:");
            if(name) {
                const id = 'grupo_' + Date.now();
                fetch('/api/social/groups/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ group_id: id, name, user_id: usuario.id })
                }).then(() => alert(`Grupo '${name}' creado`));
            }
        }

        function abrirModal(id) { document.getElementById(id).classList.add('active'); }
        function cerrarModal(id) { document.getElementById(id).classList.remove('active'); }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print(f"🚀 [Mensajería Especial] Servidor Maestro iniciado en puerto {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=False)
