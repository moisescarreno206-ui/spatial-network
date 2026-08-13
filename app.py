import os
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "spatial-network-key-2026")

# ==========================================
# CONFIGURACIÓN Y SUPABASE
# ==========================================
PORT = int(os.environ.get("PORT", 5000))
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xyzcompany.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "public-anon-key")

supabase_client = None
if "supabase.co" in SUPABASE_URL and SUPABASE_KEY != "public-anon-key":
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ [Spatial Network] Supabase conectado.")
    except Exception as e:
        print(f"⚠️ Fallo al conectar Supabase: {e}")

# ==========================================
# ENDPOINTS BACKEND
# ==========================================

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.get_json() or {}
    identity = data.get('identity', '').strip()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip() or "Moises"
    handle = data.get('handle', '').strip() or "@Jack"

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
            print(f"Error Supabase: {e}")

    return jsonify({"status": "success", "user": profile_data}), 200

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json() or {}
    identity = data.get('identity', '').strip()
    password = data.get('password', '').strip()

    handle_id = identity.split('@')[0].lower() if identity else "jack"
    user_data = {
        "id": handle_id,
        "identity": identity,
        "name": "Moises",
        "handle": f"@{handle_id}" if handle_id else "@Jack",
        "avatar_url": f"https://api.dicebear.com/7.x/bottts/svg?seed={handle_id}",
        "status_text": "¡Hola! Estoy usando Spatial Network"
    }

    if supabase_client:
        try:
            res = supabase_client.table('profiles').select('*').eq('identity', identity).execute()
            if res.data:
                user_data = res.data[0]
        except Exception as e:
            print(f"Error login: {e}")

    return jsonify({"status": "success", "user": user_data}), 200

@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    data = request.get_json() or {}
    user_id = data.get('id')
    name = data.get('name', '').strip()
    avatar_url = data.get('avatar_url', '').strip()
    status_text = data.get('status_text', '').strip()

    updated = {
        "id": user_id,
        "name": name or "Moises",
        "avatar_url": avatar_url or f"https://api.dicebear.com/7.x/bottts/svg?seed={user_id}",
        "status_text": status_text or "¡Hola! Estoy usando Spatial Network"
    }

    if supabase_client:
        try:
            supabase_client.table('profiles').update(updated).eq('id', user_id).execute()
        except Exception as e:
            print(f"Error actualizando perfil: {e}")

    return jsonify({"status": "success", "user": updated}), 200

@app.route('/api/social/videos/feed', methods=['GET'])
def get_video_feed():
    videos = [
        {"id": 1, "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4", "author": "@spatial_official", "desc": "Bienvenido a Spatial Network"},
        {"id": 2, "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4", "author": "@amiti_core", "desc": "Sincronización en vivo"},
        {"id": 3, "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4", "author": "@soporte_tecnico", "desc": "Canal de soporte de videos"}
    ]
    return jsonify({"status": "success", "videos": videos}), 200

# ==========================================
# FRONTEND INTERFAZ SPATIAL NETWORK
# ==========================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Spatial Network</title>
    <meta name="theme-color" content="#0a0a12">
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

        .view { display: none; flex: 1; flex-direction: column; height: calc(100vh - 65px); overflow-y: auto; position: relative; }
        .view.active { display: flex; }

        .header-spatial { height: 60px; background: var(--bg-card); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; font-weight: bold; font-size: 20px; color: var(--accent-purple); }
        .header-icons { display: flex; gap: 16px; align-items: center; font-size: 18px; color: var(--text-main); cursor: pointer; }

        .auth-container { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 24px; background: radial-gradient(circle at center, #1b0e2b 0%, var(--bg-dark) 100%); }
        .auth-box { width: 100%; max-width: 380px; background: var(--bg-card); border: 1px solid var(--border); padding: 28px; border-radius: 24px; display: flex; flex-direction: column; gap: 14px; }
        .auth-tabs { display: flex; border-bottom: 1px solid var(--border); margin-bottom: 8px; }
        .auth-tab-btn { flex: 1; padding: 10px; text-align: center; color: var(--text-muted); cursor: pointer; font-weight: bold; font-size: 14px; }
        .auth-tab-btn.active { color: var(--accent-purple); border-bottom: 2px solid var(--accent-purple); }

        .input-field { background: var(--bg-input); border: 1px solid var(--border); padding: 14px; border-radius: 14px; color: white; outline: none; font-size: 14px; width: 100%; }
        .input-field:focus { border-color: var(--accent-purple); box-shadow: 0 0 10px var(--accent-purple-glow); }
        .btn-purple { background: var(--accent-purple); color: white; border: none; padding: 14px; border-radius: 14px; font-weight: bold; font-size: 15px; cursor: pointer; text-align: center; }

        .nav-bar { display: flex; background: var(--bg-card); border-top: 1px solid var(--border); height: 65px; position: fixed; bottom: 0; left: 0; right: 0; z-index: 50; }
        .nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; color: var(--text-muted); font-size: 11px; cursor: pointer; }
        .nav-item.active { color: var(--accent-purple); font-weight: bold; }

        .profile-section { display: flex; flex-direction: column; align-items: center; padding: 24px 16px; text-align: center; }
        .status-bubble { background: var(--bg-card); border: 1px solid var(--border); padding: 10px 18px; border-radius: 20px; font-size: 14px; color: var(--text-main); margin-bottom: 16px; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; }
        .status-bubble:hover { border-color: var(--accent-purple); }
        .profile-avatar-container { position: relative; margin-bottom: 12px; cursor: pointer; }
        .profile-avatar { width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 3px solid var(--accent-purple); box-shadow: 0 0 25px var(--accent-purple-glow); background: #1b182e; }

        .menu-cards-list { display: flex; flex-direction: column; gap: 12px; padding: 0 16px 24px 16px; }
        .menu-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 18px; padding: 16px; display: flex; align-items: center; gap: 16px; cursor: pointer; }
        .menu-card:active { background: var(--bg-card-hover); border-color: var(--accent-purple); }

        .tiktok-feed { flex: 1; overflow-y: scroll; scroll-snap-type: y mandatory; background: #000; height: 100%; }
        .tiktok-card { height: 100%; width: 100%; scroll-snap-align: start; scroll-snap-stop: always; position: relative; display: flex; justify-content: center; align-items: center; background: #000; }
        .tiktok-card video { width: 100%; height: 100%; object-fit: cover; }

        .fab-support { position: absolute; bottom: 80px; right: 20px; width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #a855f7, #7c3aed); display: flex; justify-content: center; align-items: center; color: white; font-size: 24px; box-shadow: 0 6px 20px var(--accent-purple-glow); cursor: pointer; z-index: 10; }

        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 100; flex-direction: column; justify-content: center; align-items: center; padding: 20px; }
        .modal.active { display: flex; }
        .modal-content { background: var(--bg-card); border-radius: 20px; padding: 20px; border: 1px solid var(--border); width: 100%; max-width: 400px; display: flex; flex-direction: column; gap: 14px; }
    </style>
</head>
<body>

    <!-- AUTH -->
    <div id="view-auth" class="view active" style="height: 100vh;">
        <div class="auth-container">
            <div class="auth-box">
                <h2 style="color:var(--accent-purple); text-align:center;">Spatial Network</h2>
                <div class="auth-tabs">
                    <div id="tab-btn-login" class="auth-tab-btn active" onclick="switchAuthTab('login')">Iniciar Sesión</div>
                    <div id="tab-btn-register" class="auth-tab-btn" onclick="switchAuthTab('register')">Registrarse</div>
                </div>

                <div id="form-login" style="display:flex; flex-direction:column; gap:12px;">
                    <input type="text" id="login-identity" class="input-field" placeholder="Correo o Teléfono">
                    <input type="password" id="login-password" class="input-field" placeholder="Contraseña">
                    <button class="btn-purple" onclick="ejecutarLogin()">Entrar</button>
                </div>

                <div id="form-register" style="display:none; flex-direction:column; gap:12px;">
                    <input type="text" id="reg-name" class="input-field" placeholder="Nombre (ej. Moises)">
                    <input type="text" id="reg-handle" class="input-field" placeholder="@usuario (ej. @Jack)">
                    <input type="text" id="reg-identity" class="input-field" placeholder="Correo o Teléfono">
                    <input type="password" id="reg-password" class="input-field" placeholder="Contraseña">
                    <button class="btn-purple" onclick="ejecutarRegistro()">Crear Cuenta</button>
                </div>
            </div>
        </div>
    </div>

    <!-- CHATS -->
    <div id="view-chats" class="view">
        <div class="header-spatial">
            <span>Spatial Network</span>
            <div class="header-icons">
                <span onclick="abrirModal('modal-qr')">📷</span>
                <span onclick="abrirChatSoporte()">🤖</span>
                <span onclick="abrirModal('modal-edit-profile')">✏️</span>
            </div>
        </div>

        <div style="padding:12px 16px;">
            <div style="background:var(--bg-input); border:1px solid var(--border); border-radius:20px; padding:10px 16px; display:flex; align-items:center; gap:8px;">
                <span>🔍</span>
                <input type="text" placeholder="Buscar chats..." style="background:transparent; border:none; outline:none; color:white; width:100%;">
            </div>
        </div>

        <div style="padding: 10px 16px;">
            <!-- Opción directa para Soporte Técnico -->
            <div class="menu-card" onclick="abrirChatSoporte()">
                <div style="font-size:30px;">🤖</div>
                <div>
                    <strong style="color:white; display:block;">Amiti Soporte Técnico</strong>
                    <span style="color:var(--text-muted); font-size:12px;">Chat privado de ayuda y asistencia</span>
                </div>
            </div>
        </div>

        <div id="chats-container" style="flex:1; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:30px; color:var(--text-muted); font-size:14px;">
            No tienes más chats iniciados.<br>Agrega contactos o escribe al soporte técnico arriba.
        </div>

        <!-- Globo flotante de soporte -->
        <div class="fab-support" onclick="abrirChatSoporte()" title="Soporte Técnico">💬</div>
    </div>

    <!-- NOVEDADES / TIKTOK FEED -->
    <div id="view-novedades" class="view">
        <div class="header-spatial">
            <span>Novedades & Videos</span>
        </div>
        <div id="tiktok-feed" class="tiktok-feed"></div>
    </div>

    <!-- CONTACTOS -->
    <div id="view-contactos" class="view">
        <div class="header-spatial">
            <span>Contactos</span>
            <div class="header-icons">
                <span onclick="abrirModal('modal-qr')">📷</span>
            </div>
        </div>
        <div style="padding:16px;">
            <div class="menu-card" onclick="abrirChatSoporte()">
                <div style="font-size:30px;">🤖</div>
                <div>
                    <strong style="color:white; display:block;">Amiti Soporte Técnico</strong>
                    <span style="color:var(--text-muted); font-size:12px;">Canal Oficial de Asistencia</span>
                </div>
            </div>
        </div>
    </div>

    <!-- MENÚ / PERFIL -->
    <div id="view-menu" class="view">
        <div class="header-spatial">
            <span>Spatial Network</span>
            <div class="header-icons">
                <span onclick="abrirModal('modal-qr')">📷</span>
                <span onclick="abrirChatSoporte()">🤖</span>
                <span onclick="abrirModal('modal-edit-profile')">✏️</span>
            </div>
        </div>

        <div class="profile-section">
            <div class="status-bubble" onclick="abrirModal('modal-edit-profile')">
                <span>💭</span> <span id="user-status-text">¡Hola! Estoy usando Spatial Network</span>
            </div>
            <div class="profile-avatar-container" onclick="abrirModal('modal-edit-profile')">
                <img id="user-avatar-img" src="https://api.dicebear.com/7.x/bottts/svg?seed=Jack" class="profile-avatar" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Jack'">
            </div>
            <div id="user-display-name" style="font-size:22px; font-weight:bold; color:white;">Moises</div>
            <div id="user-display-handle" style="font-size:14px; color:var(--text-muted); margin-top:2px;">@Jack</div>
            <div style="font-size:13px; color:var(--accent-purple); margin-top:4px;">Contacto: Privado 🔒</div>
        </div>

        <div class="menu-cards-list">
            <div class="menu-card" onclick="cambiarTab('novedades')">
                <div style="font-size:26px;">🎬</div>
                <div>
                    <strong style="color:white; display:block;">Reproductor de Video</strong>
                    <span style="color:var(--text-muted); font-size:12px;">Ver videos continuos estilo TikTok</span>
                </div>
            </div>

            <div class="menu-card" onclick="abrirModal('modal-edit-profile')">
                <div style="font-size:26px;">✏️</div>
                <div>
                    <strong style="color:white; display:block;">Editar Perfil</strong>
                    <span style="color:var(--text-muted); font-size:12px;">Cambiar foto, nombre y mensaje de estado</span>
                </div>
            </div>

            <div class="menu-card" onclick="abrirChatSoporte()">
                <div style="font-size:26px;">🤖</div>
                <div>
                    <strong style="color:white; display:block;">Amiti Soporte Técnico</strong>
                    <span style="color:var(--text-muted); font-size:12px;">Abrir chat privado con soporte</span>
                </div>
            </div>

            <div class="menu-card" onclick="abrirModal('modal-qr')">
                <div style="font-size:26px;">📱</div>
                <div>
                    <strong style="color:white; display:block;">Mi Código QR / Escáner</strong>
                    <span style="color:var(--text-muted); font-size:12px;">Escanea o muestra tu código</span>
                </div>
            </div>

            <button class="btn-purple" style="background:#2d1b36; margin-top:12px;" onclick="cerrarSesion()">Cerrar Sesión</button>
        </div>
    </div>

    <!-- SALA DE CHAT / PRIVADO CON SOPORTE -->
    <div id="view-room" class="view">
        <div class="header-spatial">
            <div style="display:flex; align-items:center; gap:10px;">
                <button onclick="cambiarTab('chats')" style="background:none; border:none; color:white; font-size:20px; cursor:pointer;">←</button>
                <span id="room-title">Amiti Soporte Técnico</span>
            </div>
        </div>
        <div id="chat-messages" style="flex:1; padding:16px; overflow-y:auto; display:flex; flex-direction:column; gap:10px;">
            <div style="background:var(--bg-card); padding:12px; border-radius:12px; max-width:80%; border:1px solid var(--border);">
                🤖 <strong>Amiti Soporte:</strong> ¡Hola! ¿En qué te puedo ayudar hoy con Spatial Network?
            </div>
        </div>
        <div style="padding:12px; background:var(--bg-card); border-top:1px solid var(--border); display:flex; gap:8px;">
            <input type="text" id="message-input" class="input-field" placeholder="Escribe un mensaje..." onkeypress="if(event.key==='Enter') enviarMensajeSoporte()">
            <button class="btn-purple" style="padding:0 20px;" onclick="enviarMensajeSoporte()">➤</button>
        </div>
    </div>

    <!-- NAV BAR -->
    <div id="main-nav" class="nav-bar">
        <div class="nav-item active" id="nav-chats" onclick="cambiarTab('chats')">
            <span style="font-size:18px;">💬</span><span>Chats</span>
        </div>
        <div class="nav-item" id="nav-novedades" onclick="cambiarTab('novedades')">
            <span style="font-size:18px;">⭕</span><span>Novedades</span>
        </div>
        <div class="nav-item" id="nav-contactos" onclick="cambiarTab('contactos')">
            <span style="font-size:18px;">👥</span><span>Contactos</span>
        </div>
        <div class="nav-item" id="nav-menu" onclick="cambiarTab('menu')">
            <span style="font-size:18px;">⚙️</span><span>Menú</span>
        </div>
    </div>

    <!-- MODAL EDITAR PERFIL -->
    <div id="modal-edit-profile" class="modal">
        <div class="modal-content">
            <h3 style="text-align:center; color:var(--accent-purple);">Editar Perfil</h3>
            <label style="font-size:12px; color:var(--text-muted);">Nombre de usuario:</label>
            <input type="text" id="edit-name" class="input-field" placeholder="Tu Nombre">
            
            <label style="font-size:12px; color:var(--text-muted);">URL de Foto / Avatar:</label>
            <input type="text" id="edit-avatar" class="input-field" placeholder="https://link-de-tu-imagen.jpg">
            
            <label style="font-size:12px; color:var(--text-muted);">Mensaje de estado:</label>
            <input type="text" id="edit-status" class="input-field" placeholder="Tu estado actual">
            
            <button class="btn-purple" onclick="guardarCambiosPerfil()">Guardar Cambios</button>
            <button class="btn-purple" style="background:#231f38;" onclick="cerrarModal('modal-edit-profile')">Cancelar</button>
        </div>
    </div>

    <!-- MODAL QR -->
    <div id="modal-qr" class="modal">
        <div class="modal-content">
            <h3 style="text-align:center; color:var(--accent-purple);">Código QR</h3>
            <div style="display:flex; justify-content:center; padding:10px;"><canvas id="qr-canvas"></canvas></div>
            <button class="btn-purple" style="background:#231f38;" onclick="cerrarModal('modal-qr')">Cerrar</button>
        </div>
    </div>

    <script>
        let usuario = JSON.parse(localStorage.getItem('spatial_user')) || {
            id: 'jack',
            name: 'Moises',
            handle: '@Jack',
            avatar_url: 'https://api.dicebear.com/7.x/bottts/svg?seed=Jack',
            status_text: '¡Hola! Estoy usando Spatial Network'
        };

        window.onload = () => {
            renderizarUsuario();
            cargarFeedVideos();
            cambiarTab('chats');
        };

        function renderizarUsuario() {
            if(!usuario.name || usuario.name === 'undefined') usuario.name = 'Moises';
            if(!usuario.handle || usuario.handle === 'undefined') usuario.handle = '@Jack';
            if(!usuario.avatar_url || usuario.avatar_url === 'undefined') usuario.avatar_url = 'https://api.dicebear.com/7.x/bottts/svg?seed=Jack';
            if(!usuario.status_text) usuario.status_text = '¡Hola! Estoy usando Spatial Network';

            document.getElementById('user-display-name').innerText = usuario.name;
            document.getElementById('user-display-handle').innerText = usuario.handle;
            document.getElementById('user-avatar-img').src = usuario.avatar_url;
            document.getElementById('user-status-text').innerText = usuario.status_text;

            document.getElementById('edit-name').value = usuario.name;
            document.getElementById('edit-avatar').value = usuario.avatar_url;
            document.getElementById('edit-status').value = usuario.status_text;

            generarQR();
        }

        async function guardarCambiosPerfil() {
            usuario.name = document.getElementById('edit-name').value.trim() || 'Moises';
            usuario.avatar_url = document.getElementById('edit-avatar').value.trim() || 'https://api.dicebear.com/7.x/bottts/svg?seed=Jack';
            usuario.status_text = document.getElementById('edit-status').value.trim() || '¡Hola! Estoy usando Spatial Network';

            localStorage.setItem('spatial_user', JSON.stringify(usuario));
            renderizarUsuario();
            cerrarModal('modal-edit-profile');

            await fetch('/api/profile/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(usuario)
            });
        }

        function abrirChatSoporte() {
            document.getElementById('room-title').innerText = "Amiti Soporte Técnico";
            cambiarTab('room');
        }

        function enviarMensajeSoporte() {
            const input = document.getElementById('message-input');
            const txt = input.value.trim();
            if(!txt) return;

            const box = document.getElementById('chat-messages');
            box.innerHTML += `<div style="background:var(--accent-purple); color:white; padding:12px; border-radius:12px; align-self:flex-end; max-width:80%; margin-left:auto;">${txt}</div>`;
            input.value = '';

            setTimeout(() => {
                box.innerHTML += `<div style="background:var(--bg-card); padding:12px; border-radius:12px; max-width:80%; border:1px solid var(--border);">🤖 <strong>Amiti Soporte:</strong> Mensaje recibido. Soporte en proceso.</div>`;
                box.scrollTop = box.scrollHeight;
            }, 800);
        }

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
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ identity, password })
            });
            const data = await res.json();
            if(data.user) {
                usuario = data.user;
                localStorage.setItem('spatial_user', JSON.stringify(usuario));
                document.getElementById('view-auth').classList.remove('active');
                renderizarUsuario();
                cambiarTab('chats');
            }
        }

        async function ejecutarRegistro() {
            const name = document.getElementById('reg-name').value.trim();
            const handle = document.getElementById('reg-handle').value.trim();
            const identity = document.getElementById('reg-identity').value.trim();
            const password = document.getElementById('reg-password').value.trim();

            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name, handle, identity, password })
            });
            const data = await res.json();
            if(data.user) {
                usuario = data.user;
                localStorage.setItem('spatial_user', JSON.stringify(usuario));
                document.getElementById('view-auth').classList.remove('active');
                renderizarUsuario();
                cambiarTab('chats');
            }
        }

        function cerrarSesion() {
            localStorage.removeItem('spatial_user');
            location.reload();
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
                        card.innerHTML = `<video src="${v.video_url}" controls loop playsinline></video>`;
                        feed.appendChild(card);
                    });
                }
            });
        }

        function generarQR() {
            new QRious({
                element: document.getElementById('qr-canvas'),
                value: usuario.handle || '@Jack',
                size: 180, background: '#12101f', foreground: '#a855f7'
            });
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
    print(f"🚀 Servidor Spatial Network activo en puerto {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=False)
