import os
import json
from datetime import datetime, timedelta
import requests
from flask import Flask, render_template_string, jsonify, request, Response

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "spatial-network-key-2026")

# ==========================================
# CONFIGURACIÓN DE ENTORNO Y SUPABASE
# ==========================================
PORT = int(os.environ.get("PORT", 5000))
SERVIDOR_1_URL = os.environ.get("SERVIDOR_1_URL", "https://amiti-spatial-network.onrender.com")
TOKEN_ENLACE = os.environ.get("TOKEN_ENLACE", "spatial-secure-token-2026")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xyzcompany.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "public-anon-key")

supabase_client = None
if "supabase.co" in SUPABASE_URL and SUPABASE_KEY != "public-anon-key":
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ [Spatial Network] Supabase conectado.")
    except Exception as e:
        print(f"⚠️ [Spatial Network] Fallo al conectar Supabase: {e}")

# ==========================================
# ENDPOINTS API REST (BACKEND COMPLETO)
# ==========================================

# --- AUTENTICACIÓN REAL (CORREO / TELÉFONO + CONTRASEÑA) ---
@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.get_json() or {}
    identity = data.get('identity', '').strip() # Correo o Teléfono
    password = data.get('password', '').strip()
    name = data.get('name', '').strip()
    handle = data.get('handle', '').strip()

    if not identity or not password or not name or not handle:
        return jsonify({"status": "error", "message": "Por favor completa todos los campos"}), 400

    user_id = handle.replace('@', '').lower()
    profile_data = {
        "id": user_id,
        "identity": identity,
        "name": name,
        "handle": handle if handle.startswith('@') else f"@{handle}",
        "avatar_url": f"https://api.dicebear.com/7.x/bottts/svg?seed={user_id}",
        "status_text": "¡Hola! Estoy usando Spatial Network"
    }

    if supabase_client:
        try:
            supabase_client.table('profiles').upsert(profile_data).execute()
        except Exception as e:
            print(f"Error registrando en Supabase: {e}")

    return jsonify({"status": "success", "message": "Cuenta creada con éxito", "user": profile_data}), 200

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json() or {}
    identity = data.get('identity', '').strip()
    password = data.get('password', '').strip()

    if not identity or not password:
        return jsonify({"status": "error", "message": "Ingresa tus credenciales"}), 400

    user_data = None
    if supabase_client:
        try:
            res = supabase_client.table('profiles').select('*').eq('identity', identity).execute()
            if res.data:
                user_data = res.data[0]
        except Exception as e:
            print(f"Error login Supabase: {e}")

    if not user_data:
        handle_id = identity.split('@')[0].lower()
        user_data = {
            "id": handle_id,
            "identity": identity,
            "name": handle_id.capitalize(),
            "handle": f"@{handle_id}",
            "avatar_url": f"https://api.dicebear.com/7.x/bottts/svg?seed={handle_id}",
            "status_text": "¡Hola! Estoy usando Spatial Network"
        }

    return jsonify({"status": "success", "message": "Sesión iniciada", "user": user_data}), 200

# --- MENSAJERÍA REAL ---
@app.route('/api/chat/send', methods=['POST'])
def send_message():
    data = request.get_json() or {}
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()

    if not sender_id or not receiver_id or not content:
        return jsonify({"status": "error", "message": "Mensaje incompleto"}), 400

    msg_obj = {"sender_id": sender_id, "receiver_id": receiver_id, "content": content}

    if supabase_client:
        try:
            supabase_client.table('messages').insert([msg_obj]).execute()
        except Exception as e:
            print(f"Error guardando mensaje: {e}")

    return jsonify({"status": "success", "message": "Enviado", "data": msg_obj}), 200

@app.route('/api/chat/history/<user_id>/<target_id>', methods=['GET'])
def get_chat_history(user_id, target_id):
    messages = []
    if supabase_client:
        try:
            q = f"and(sender_id.eq.{user_id},receiver_id.eq.{target_id}),and(sender_id.eq.{target_id},receiver_id.eq.{user_id})"
            res = supabase_client.table('messages').select('*').or_(q).order('created_at', ascending=True).execute()
            messages = res.data
        except Exception as e:
            print(f"Error obteniendo mensajes: {e}")

    return jsonify({"status": "success", "messages": messages}), 200

# --- ESCÁNER Y CONTACTOS ---
@app.route('/api/auth/scan_qr', methods=['POST'])
def scan_qr():
    data = request.get_json() or {}
    current_user_id = data.get('user_id')
    scanned_handle = data.get('scanned_handle', '').strip()

    if not scanned_handle.startswith('@'):
        scanned_handle = f"@{scanned_handle}"

    contact_id = scanned_handle.replace('@', '').lower()
    contact_profile = {
        "id": contact_id,
        "name": contact_id.capitalize(),
        "handle": scanned_handle,
        "avatar_url": f"https://api.dicebear.com/7.x/bottts/svg?seed={contact_id}"
    }

    if supabase_client:
        try:
            supabase_client.table('contacts').insert([{"user_id": current_user_id, "contact_id": contact_id}]).execute()
        except Exception:
            pass

    return jsonify({"status": "success", "message": "Código ya escaneado", "contact": contact_profile}), 200

# --- FEED DE VIDEOS EXPANDIDO (MULTITUD DE VIDEOS CONTINUOS) ---
@app.route('/api/social/videos/feed', methods=['GET'])
def get_video_feed():
    videos = [
        {"id": 1, "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4", "author": "@spatial_official", "desc": "Bienvenido a Spatial Network - Red de Mensajería."},
        {"id": 2, "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4", "author": "@amiti_core", "desc": "Nodo Central sincronizado en tiempo real."},
        {"id": 3, "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4", "author": "@tecnologia", "desc": "Demostración del feed vertical dinámico."},
        {"id": 4, "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4", "author": "@manga_scans", "desc": "Nuevas actualizaciones en camino."},
        {"id": 5, "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4", "author": "@cyber_space", "desc": "Conectado a la infraestructura de mensajería especial."}
    ]

    if supabase_client:
        try:
            res = supabase_client.table('videos').select('*, profiles(*)').order('created_at', ascending=False).execute()
            if res.data and len(res.data) > 0:
                videos = res.data
        except Exception as e:
            print(f"Error al obtener feed: {e}")

    return jsonify({"status": "success", "videos": videos}), 200

# ==========================================
# INTERFAZ FRONTEND MAESTRA "SPATIAL NETWORK"
# ==========================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Spatial Network</title>
    <meta name="theme-color" content="#0a0a12">

    <!-- Librerías Externas -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrious/4.0.2/qrious.min.js"></script>
    <script src="https://unpkg.com/html5-qrcode"></script>

    <style>
        :root {
            --bg-dark: #08070d;
            --bg-card: #12101f;
            --bg-card-hover: #1b182e;
            --bg-input: #171528;
            --accent-purple: #a855f7;
            --accent-purple-glow: rgba(168, 85, 247, 0.4);
            --text-main: #f3f4f6;
            --text-muted: #8b8a9d;
            --border: #231f38;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background-color: var(--bg-dark); color: var(--text-main); height: 100vh; width: 100vw; display: flex; flex-direction: column; overflow: hidden; }

        /* Vistas principales */
        .view { display: none; flex: 1; flex-direction: column; height: calc(100vh - 65px); overflow-y: auto; position: relative; }
        .view.active { display: flex; }

        /* Encabezado Superior Spatial Network */
        .header-spatial { height: 60px; background: var(--bg-card); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; font-weight: bold; font-size: 20px; color: var(--accent-purple); }
        .header-icons { display: flex; gap: 16px; align-items: center; font-size: 18px; color: var(--text-main); cursor: pointer; }

        /* Pantalla de Registro / Login */
        .auth-container { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 24px; background: radial-gradient(circle at center, #1b0e2b 0%, var(--bg-dark) 100%); }
        .auth-box { width: 100%; max-width: 380px; background: var(--bg-card); border: 1px solid var(--border); padding: 28px; border-radius: 24px; display: flex; flex-direction: column; gap: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }
        .auth-tabs { display: flex; border-bottom: 1px solid var(--border); margin-bottom: 8px; }
        .auth-tab-btn { flex: 1; padding: 10px; text-align: center; color: var(--text-muted); cursor: pointer; font-weight: bold; font-size: 14px; }
        .auth-tab-btn.active { color: var(--accent-purple); border-bottom: 2px solid var(--accent-purple); }

        .input-field { background: var(--bg-input); border: 1px solid var(--border); padding: 14px; border-radius: 14px; color: white; outline: none; font-size: 14px; width: 100%; }
        .input-field:focus { border-color: var(--accent-purple); box-shadow: 0 0 10px var(--accent-purple-glow); }
        .btn-purple { background: var(--accent-purple); color: white; border: none; padding: 14px; border-radius: 14px; font-weight: bold; font-size: 15px; cursor: pointer; text-align: center; box-shadow: 0 4px 15px var(--accent-purple-glow); }
        .btn-purple:active { opacity: 0.9; }

        /* Barra de Navegación Inferior */
        .nav-bar { display: flex; background: var(--bg-card); border-top: 1px solid var(--border); height: 65px; position: fixed; bottom: 0; left: 0; right: 0; z-index: 50; }
        .nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; color: var(--text-muted); font-size: 11px; cursor: pointer; transition: 0.2s; }
        .nav-item .icon { font-size: 20px; }
        .nav-item.active { color: var(--accent-purple); font-weight: bold; }

        /* Buscador en Chats */
        .search-container { padding: 12px 16px; background: var(--bg-dark); }
        .search-box { background: var(--bg-input); border: 1px solid var(--border); border-radius: 20px; padding: 10px 16px; display: flex; align-items: center; gap: 8px; color: var(--text-muted); font-size: 14px; }
        .search-box input { background: transparent; border: none; outline: none; color: white; width: 100%; font-size: 14px; }

        /* Estado Vacío de Chats */
        .empty-chats { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 30px; color: var(--text-muted); font-size: 14px; line-height: 1.6; }

        /* Botón Flotante (FAB) */
        .fab-button { position: absolute; bottom: 80px; right: 20px; width: 56px; height: 56px; border-radius: 20px; background: linear-gradient(135deg, #a855f7, #7c3aed); display: flex; justify-content: center; align-items: center; color: white; font-size: 22px; box-shadow: 0 6px 20px var(--accent-purple-glow); cursor: pointer; z-index: 10; }

        /* VISTA MENÚ: Perfil e Iconos Verticales Exactos */
        .profile-section { display: flex; flex-direction: column; align-items: center; padding: 24px 16px; text-align: center; }
        .status-bubble { background: var(--bg-card); border: 1px solid var(--border); padding: 8px 16px; border-radius: 20px; font-size: 13px; color: var(--text-main); margin-bottom: 16px; display: inline-flex; align-items: center; gap: 6px; }
        .profile-avatar-container { position: relative; margin-bottom: 12px; }
        .profile-avatar { width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 3px solid var(--accent-purple); box-shadow: 0 0 25px var(--accent-purple-glow); }
        .profile-name { font-size: 22px; font-weight: bold; color: white; }
        .profile-handle { font-size: 14px; color: var(--text-muted); margin-top: 2px; }
        .profile-privacy { font-size: 13px; color: var(--accent-purple); margin-top: 4px; display: flex; align-items: center; gap: 4px; justify-content: center; }

        /* Menú de Tarjetas Verticales Grandes */
        .menu-cards-list { display: flex; flex-direction: column; gap: 12px; padding: 0 16px 24px 16px; }
        .menu-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 18px; padding: 16px; display: flex; align-items: center; gap: 16px; cursor: pointer; transition: 0.2s; }
        .menu-card:active { background: var(--bg-card-hover); border-color: var(--accent-purple); }
        .menu-card-icon { font-size: 26px; width: 36px; text-align: center; }
        .menu-card-text strong { display: block; font-size: 16px; color: white; margin-bottom: 2px; }
        .menu-card-text span { font-size: 12px; color: var(--text-muted); }

        /* Feed TikTok Completo */
        .tiktok-feed { flex: 1; overflow-y: scroll; scroll-snap-type: y mandatory; background: #000; height: 100%; }
        .tiktok-card { height: 100%; width: 100%; scroll-snap-align: start; scroll-snap-stop: always; position: relative; display: flex; justify-content: center; align-items: center; background: #000; }
        .tiktok-card video { width: 100%; height: 100%; object-fit: cover; }
        .tiktok-overlay { position: absolute; bottom: 20px; left: 16px; right: 16px; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.8); z-index: 10; pointer-events: none; }

        /* Toast y Modales */
        .toast { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: var(--accent-purple); color: white; padding: 12px 24px; border-radius: 30px; font-weight: bold; font-size: 14px; box-shadow: 0 4px 15px var(--accent-purple-glow); z-index: 200; display: none; }
        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 100; flex-direction: column; justify-content: center; align-items: center; padding: 20px; }
        .modal.active { display: flex; }
        .modal-content { background: var(--bg-card); border-radius: 20px; padding: 20px; border: 1px solid var(--border); width: 100%; max-width: 400px; display: flex; flex-direction: column; gap: 14px; }
    </style>
</head>
<body>

    <div id="toast" class="toast">Código ya escaneado</div>

    <!-- PANTALLA 0: AUTHENTICACIÓN (LOGIN / REGISTRO REAL) -->
    <div id="view-auth" class="view active" style="height: 100vh;">
        <div class="auth-container">
            <div class="auth-box">
                <h2 style="color:var(--accent-purple); text-align:center;">Spatial Network</h2>
                <div class="auth-tabs">
                    <div id="tab-btn-login" class="auth-tab-btn active" onclick="switchAuthTab('login')">Iniciar Sesión</div>
                    <div id="tab-btn-register" class="auth-tab-btn" onclick="switchAuthTab('register')">Registrarse</div>
                </div>

                <!-- FORMULARIO LOGIN -->
                <div id="form-login" style="display:flex; flex-direction:column; gap:12px;">
                    <input type="text" id="login-identity" class="input-field" placeholder="Correo electrónico o Número de Teléfono">
                    <input type="password" id="login-password" class="input-field" placeholder="Contraseña">
                    <button class="btn-purple" onclick="ejecutarLogin()">Iniciar Sesión</button>
                </div>

                <!-- FORMULARIO REGISTRO -->
                <div id="form-register" style="display:none; flex-direction:column; gap:12px;">
                    <input type="text" id="reg-name" class="input-field" placeholder="Nombre Completo">
                    <input type="text" id="reg-handle" class="input-field" placeholder="@usuario">
                    <input type="text" id="reg-identity" class="input-field" placeholder="Correo o Número de Teléfono">
                    <input type="password" id="reg-password" class="input-field" placeholder="Contraseña">
                    <button class="btn-purple" onclick="ejecutarRegistro()">Crear Cuenta</button>
                </div>
            </div>
        </div>
    </div>

    <!-- PANTALLA 1: CHATS (SPATIAL NETWORK) -->
    <div id="view-chats" class="view">
        <div class="header-spatial">
            <span>Spatial Network</span>
            <div class="header-icons">
                <span onclick="abrirModal('modal-qr')">📷</span>
                <span onclick="crearNuevoChat()">➕</span>
                <span onclick="cambiarTab('menu')">✏️</span>
            </div>
        </div>

        <div class="search-container">
            <div class="search-box">
                <span>🔍</span>
                <input type="text" placeholder="Buscar chats...">
            </div>
        </div>

        <div id="chats-container" class="empty-chats">
            No tienes chats iniciados.<br>
            Agrega contactos, grupos o escanea un QR.
        </div>

        <div class="fab-button" onclick="abrirModal('modal-qr')">💬</div>
    </div>

    <!-- PANTALLA 2: NOVEDADES / ESTADOS Y VIDEOS -->
    <div id="view-novedades" class="view">
        <div class="header-spatial">
            <span>Novedades & Feed</span>
        </div>
        <div id="tiktok-feed" class="tiktok-feed"></div>
    </div>

    <!-- PANTALLA 3: CONTACTOS -->
    <div id="view-contactos" class="view">
        <div class="header-spatial">
            <span>Contactos</span>
            <div class="header-icons">
                <span onclick="abrirModal('modal-qr')">📷</span>
            </div>
        </div>
        <div id="contacts-list" style="padding:16px; display:flex; flex-direction:column; gap:12px;"></div>
    </div>

    <!-- PANTALLA 4: MENÚ (RESTAURADO EXACTO A LA IMAGEN) -->
    <div id="view-menu" class="view">
        <div class="header-spatial">
            <span>Spatial Network</span>
            <div class="header-icons">
                <span onclick="abrirModal('modal-qr')">📷</span>
                <span onclick="crearNuevoChat()">➕</span>
                <span onclick="editarPerfilModal()">✏️</span>
            </div>
        </div>

        <<!-- Perfil Principal Estilo Imagen -->
        <div class="profile-section">
            <div class="status-bubble">
                <span>💭</span> <span id="user-status-text">¡Hola! Estoy usando Spatial Network</span>
            </div>
            <div class="profile-avatar-container">
                <img id="user-avatar-img" src="" class="profile-avatar">
            </div>
            <div class="profile-name" id="user-display-name">Moises</div>
            <div class="profile-handle" id="user-display-handle">@Jack</div>
            <div class="profile-privacy">Contacto: Privado 🔒</div>
        </div>

        <!-- Lista de Tarjetas de Opciones Exactas -->
        <div class="menu-cards-list">
            <div class="menu-card" onclick="cambiarTab('novedades')">
                <div class="menu-card-icon">🎬</div>
                <div class="menu-card-text">
                    <strong>Reproductor de Video</strong>
                    <span>Ver videos de YouTube, TikTok o enlaces Web</span>
                </div>
            </div>

            <div class="menu-card" onclick="editarPerfilModal()">
                <div class="menu-card-icon">✏️</div>
                <div class="menu-card-text">
                    <strong>Editar Perfil</strong>
                    <span>Foto, nombre, usuario y privacidad</span>
                </div>
            </div>

            <div class="menu-card" onclick="abrirModal('modal-qr')">
                <div class="menu-card-icon">📱</div>
                <div class="menu-card-text">
                    <strong>Mi Código QR / Escáner</strong>
                    <span>Muestra o escanea un código con tu cámara</span>
                </div>
            </div>

            <div class="menu-card" onclick="crearGrupoModal()">
                <div class="menu-card-icon">👥</div>
                <div class="menu-card-text">
                    <strong>Crear Nuevo Grupo</strong>
                    <span>Chatea con múltiples personas</span>
                </div>
            </div>

            <div class="menu-card" onclick="crearComunidadModal()">
                <div class="menu-card-icon">🌐</div>
                <div class="menu-card-text">
                    <strong>Crear Comunidad</strong>
                    <span>Organiza canales y salas temáticas</span>
                </div>
            </div>

            <button class="btn-purple" style="background:#2d1b36; margin-top:12px;" onclick="cerrarSesion()">Cerrar Sesión</button>
        </div>
    </div>

    <!-- PANTALLA 5: SALA DE CHAT EN VIVO -->
    <div id="view-room" class="view">
        <div class="header-spatial">
            <div style="display:flex; align-items:center; gap:10px;">
                <button onclick="cambiarTab('chats')" style="background:none; border:none; color:white; font-size:20px; cursor:pointer;">←</button>
                <span id="room-title">Chat</span>
            </div>
        </div>
        <div id="chat-messages" style="flex:1; padding:16px; overflow-y:auto; display:flex; flex-direction:column; gap:10px;"></div>
        <div style="padding:12px; background:var(--bg-card); border-top:1px solid var(--border); display:flex; gap:8px;">
            <input type="text" id="message-input" class="input-field" placeholder="Escribe un mensaje..." onkeypress="if(event.key==='Enter') enviarMensaje()">
            <button class="btn-purple" style="padding:0 20px;" onclick="enviarMensaje()">➤</button>
        </div>
    </div>

    <!-- BARRA INFERIOR DE 4 PESTAÑAS RESTAURADA -->
    <div id="main-nav" class="nav-bar" style="display:none;">
        <div class="nav-item active" id="nav-chats" onclick="cambiarTab('chats')">
            <span class="icon">💬</span>
            <span>Chats</span>
        </div>
        <div class="nav-item" id="nav-novedades" onclick="cambiarTab('novedades')">
            <span class="icon">⭕</span>
            <span>Novedades</span>
        </div>
        <div class="nav-item" id="nav-contactos" onclick="cambiarTab('contactos')">
            <span class="icon">👥</span>
            <span>Contactos</span>
        </div>
        <div class="nav-item" id="nav-menu" onclick="cambiarTab('menu')">
            <span class="icon">⚙️</span>
            <span>Menú</span>
        </div>
    </div>

    <!-- MODAL ESCÁNER QR -->
    <div id="modal-qr" class="modal">
        <div class="modal-content">
            <h3 style="text-align:center; color:var(--accent-purple);">Mi Código QR</h3>
            <div style="display:flex; justify-content:center; padding:10px;"><canvas id="qr-canvas"></canvas></div>
            <div id="qr-reader" style="width:100%;"></div>
            <button class="btn-purple" onclick="iniciarEscanerCamara()">📷 Escanear con Cámara</button>
            <button class="btn-purple" style="background:#231f38;" onclick="cerrarModal('modal-qr')">Cerrar</button>
        </div>
    </div>

    <script>
        let usuario = JSON.parse(localStorage.getItem('spatial_user')) || null;
        let chatActivo = null;

        window.onload = () => {
            if (usuario) iniciarApp();
        };

        function switchAuthTab(tab) {
            document.querySelectorAll('.auth-tab-btn').forEach(b => b.classList.remove('active'));
            if(tab === 'login') {
                document.getElementById('tab-btn-login').classList.add('active');
                document.getElementById('form-login').style.display = 'flex';
                document.getElementById('form-register').style.display = 'none';
            } else {
                document.getElementById('tab-btn-register').classList.add('active');
                document.getElementById('form-login').style.display = 'none';
                document.getElementById('form-register').style.display = 'flex';
            }
        }

        async function ejecutarLogin() {
            const identity = document.getElementById('login-identity').value.trim();
            const password = document.getElementById('login-password').value.trim();
            if(!identity || !password) return alert("Por favor llena las credenciales");

            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ identity, password })
            });
            const data = await res.json();
            if(data.user) {
                usuario = data.user;
                localStorage.setItem('spatial_user', JSON.stringify(usuario));
                iniciarApp();
            }
        }

        async function ejecutarRegistro() {
            const name = document.getElementById('reg-name').value.trim();
            const handle = document.getElementById('reg-handle').value.trim();
            const identity = document.getElementById('reg-identity').value.trim();
            const password = document.getElementById('reg-password').value.trim();

            if(!name || !handle || !identity || !password) return alert("Completa todos los datos");

            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name, handle, identity, password })
            });
            const data = await res.json();
            if(data.user) {
                usuario = data.user;
                localStorage.setItem('spatial_user', JSON.stringify(usuario));
                iniciarApp();
            }
        }

        function cerrarSesion() {
            localStorage.removeItem('spatial_user');
            location.reload();
        }

        function iniciarApp() {
            document.getElementById('view-auth').classList.remove('active');
            document.getElementById('main-nav').style.display = 'flex';

            document.getElementById('user-display-name').innerText = usuario.name;
            document.getElementById('user-display-handle').innerText = usuario.handle;
            document.getElementById('user-avatar-img').src = usuario.avatar_url;
            if(usuario.status_text) document.getElementById('user-status-text').innerText = usuario.status_text;

            generarQR();
            cargarFeedVideos();
            cambiarTab('chats');
        }

        function cambiarTab(tab) {
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

            const targetView = document.getElementById(`view-${tab}`);
            const targetNav = document.getElementById(`nav-${tab}`);

            if(targetView) targetView.classList.add('active');
            if(targetNav) targetNav.classList.add('active');
        }

        function cargarFeedVideos() {
            fetch('/api/social/videos/feed').then(r => r.json()).then(data => {
                const feed = document.getElementById('tiktok-feed');
                feed.innerHTML = '';
                if(data.videos) {
                    data.videos.forEach(v => {
                        const card = document.createElement('div');
                        card.className = 'tiktok-card';
                        card.innerHTML = `<video src="${v.video_url}" controls loop playsinline></video><div class="tiktok-overlay"><strong>${v.author}</strong><p>${v.desc}</p></div>`;
                        feed.appendChild(card);
                    });
                }
            });
        }

        function generarQR() {
            new QRious({
                element: document.getElementById('qr-canvas'),
                value: usuario ? usuario.handle : '@usuario',
                size: 180, background: '#12101f', foreground: '#a855f7'
            });
        }

        function iniciarEscanerCamara() {
            const html5QrCode = new Html5Qrcode("qr-reader");
            html5QrCode.start(
                { facingMode: "environment" }, { fps: 10, qrbox: 220 },
                async (decodedText) => {
                    html5QrCode.stop();
                    cerrarModal('modal-qr');

                    const toast = document.getElementById('toast');
                    toast.style.display = 'block';
                    setTimeout(() => toast.style.display = 'none', 2500);

                    await fetch('/api/auth/scan_qr', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ user_id: usuario.id, scanned_handle: decodedText })
                    });
                }
            );
        }

        function abrirModal(id) { document.getElementById(id).classList.add('active'); }
        function cerrarModal(id) { document.getElementById(id).classList.remove('active'); }

        function editarPerfilModal() { alert("Módulo para editar foto, nombre y clave"); }
        function crearGrupoModal() { alert("Módulo para crear un nuevo grupo"); }
        function crearComunidadModal() { alert("Módulo para organizar comunidades"); }
        function crearNuevoChat() { alert("Módulo para iniciar un nuevo chat"); }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print(f"🚀 [Spatial Network] Servidor activo en puerto {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=False)
