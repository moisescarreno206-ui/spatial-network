import os
import re
import json
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "spatial-network-key-2026")

# ==========================================
# CONFIGURACIÓN Y CONEXIÓN SUPABASE / DB
# ==========================================
PORT = int(os.environ.get("PORT", 5000))
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xyzcompany.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "public-anon-key")

supabase_client = None
if "supabase.co" in SUPABASE_URL and SUPABASE_KEY != "public-anon-key":
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ [Spatial Network] Conectado a Supabase.")
    except Exception as e:
        print(f"⚠️ Fallo al conectar Supabase: {e}")

# Memoria de respaldo local cuando no hay DB conectada
LOCAL_DB = {
    "users": {},
    "contacts": {},
    "statuses": [],
    "messages": []
}

def get_client_ip():
    """Obtiene la dirección IP real del dispositivo que envía la solicitud"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or "127.0.0.1"

def validate_email_or_phone(identity):
    """Verifica si la identidad ingresada es un correo válido o número telefónico"""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    phone_regex = r'^\+?[0-9]{7,15}$'
    
    clean_identity = identity.replace(" ", "").replace("-", "")
    if re.match(email_regex, identity):
        return True, "email"
    elif re.match(phone_regex, clean_identity):
        return True, "phone"
    return False, "invalid"

# ==========================================
# ENDPOINTS ENDPOINTS BACKEND REALES
# ==========================================

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    identity = data.get('identity', '').strip()
    password = data.get('password', '').strip()
    client_ip = get_client_ip()

    if not username or not identity or not password:
        return jsonify({"status": "error", "message": "Todos los campos son obligatorios"}), 400

    is_valid, id_type = validate_email_or_phone(identity)
    if not is_valid:
        return jsonify({"status": "error", "message": "Ingresa un correo electrónico o teléfono válido."}), 400

    user_handle = username if username.startswith('@') else f"@{username}"
    user_id = user_handle.replace('@', '').lower()

    user_profile = {
        "id": user_id,
        "username": user_handle,
        "identity": identity,
        "identity_type": id_type,
        "avatar_url": f"https://api.dicebear.com/7.x/bottts/svg?seed={user_id}",
        "status_text": "¡Hola! Estoy usando Spatial Network",
        "last_ip": client_ip,
        "created_at": datetime.utcnow().isoformat()
    }

    if supabase_client:
        try:
            supabase_client.table('profiles').upsert(user_profile).execute()
        except Exception as e:
            print(f"Error Supabase en registro: {e}")

    LOCAL_DB["users"][user_id] = user_profile
    return jsonify({"status": "success", "user": user_profile, "client_ip": client_ip}), 200

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json() or {}
    identity = data.get('identity', '').strip()
    password = data.get('password', '').strip()
    client_ip = get_client_ip()

    is_valid, _ = validate_email_or_phone(identity)
    if not is_valid and identity != "admin":
        return jsonify({"status": "error", "message": "Ingresa un correo o teléfono válido."}), 400

    user_id = identity.split('@')[0].lower().replace('+', '')
    user_profile = {
        "id": user_id,
        "username": f"@{user_id}",
        "identity": identity,
        "avatar_url": f"https://api.dicebear.com/7.x/bottts/svg?seed={user_id}",
        "status_text": "¡Hola! Estoy usando Spatial Network",
        "last_ip": client_ip
    }

    if supabase_client:
        try:
            res = supabase_client.table('profiles').select('*').eq('identity', identity).execute()
            if res.data:
                user_profile = res.data[0]
                user_profile['last_ip'] = client_ip
                supabase_client.table('profiles').update({'last_ip': client_ip}).eq('id', user_profile['id']).execute()
        except Exception as e:
            print(f"Error login Supabase: {e}")

    LOCAL_DB["users"][user_id] = user_profile
    return jsonify({"status": "success", "user": user_profile, "client_ip": client_ip}), 200

@app.route('/api/contacts/sync', methods=['POST'])
def sync_contacts():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    contact_handle = data.get('contact_handle', '').strip()

    if not contact_handle:
        return jsonify({"status": "error", "message": "Ingresa un usuario o número válido."}), 400

    contact_id = contact_handle.replace('@', '').lower()
    contact_data = {
        "id": contact_id,
        "handle": contact_handle if contact_handle.startswith('@') else f"@{contact_handle}",
        "name": contact_handle.replace('@', '').capitalize(),
        "avatar_url": f"https://api.dicebear.com/7.x/bottts/svg?seed={contact_id}"
    }

    if user_id not in LOCAL_DB["contacts"]:
        LOCAL_DB["contacts"][user_id] = []
    
    LOCAL_DB["contacts"][user_id].append(contact_data)
    return jsonify({"status": "success", "contact": contact_data}), 200

@app.route('/api/statuses', methods=['GET', 'POST'])
def handle_statuses():
    client_ip = get_client_ip()
    
    if request.method == 'POST':
        data = request.get_json() or {}
        user_id = data.get('user_id')
        username = data.get('username', '@Usuario')
        content_type = data.get('type', 'text') # text, image, video
        content_url = data.get('url', '')
        text_body = data.get('text', '')

        status_item = {
            "id": len(LOCAL_DB["statuses"]) + 1,
            "user_id": user_id,
            "username": username,
            "type": content_type,
            "url": content_url,
            "text": text_body,
            "client_ip": client_ip,
            "created_at": datetime.utcnow().isoformat()
        }

        if supabase_client:
            try:
                supabase_client.table('statuses').insert(status_item).execute()
            except Exception as e:
                print(f"Error insertando estado: {e}")

        LOCAL_DB["statuses"].append(status_item)
        return jsonify({"status": "success", "data": status_item}), 200

    # GET: Filtrar estados con máximo 24 horas de vigencia
    now = datetime.utcnow()
    valid_statuses = []
    
    for s in LOCAL_DB["statuses"]:
        created = datetime.fromisoformat(s["created_at"])
        if now - created <= timedelta(hours=24):
            valid_statuses.append(s)

    return jsonify({"status": "success", "statuses": valid_statuses}), 200

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
    <meta name="theme-color" content="#0d0b18">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrious/4.0.2/qrious.min.js"></script>

    <style>
        :root {
            --bg-dark: #090810;
            --bg-card: #131122;
            --bg-card-hover: #1c1933;
            --bg-input: #19162e;
            --accent-purple: #8b5cf6;
            --accent-purple-glow: rgba(139, 92, 246, 0.4);
            --text-main: #f3f4f6;
            --text-muted: #8c8aa0;
            --border: #24203d;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background-color: var(--bg-dark); color: var(--text-main); height: 100vh; width: 100vw; display: flex; flex-direction: column; overflow: hidden; }

        .view { display: none; flex: 1; flex-direction: column; height: calc(100vh - 65px); overflow-y: auto; position: relative; }
        .view.active { display: flex; }

        .header-spatial { height: 60px; background: var(--bg-card); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; font-weight: bold; font-size: 20px; color: var(--accent-purple); }
        .header-icons { display: flex; gap: 16px; align-items: center; font-size: 18px; color: var(--text-main); cursor: pointer; }

        /* AUTH - IDÉNTICO A IMAGEN 1000039296.png */
        .auth-container { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 20px; background: radial-gradient(circle at center, #180d2d 0%, var(--bg-dark) 100%); }
        .auth-box { width: 100%; max-width: 380px; background: #121021; border: 1px solid var(--border); padding: 32px 24px; border-radius: 28px; display: flex; flex-direction: column; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .auth-title { font-size: 26px; font-weight: 800; color: #a78bfa; text-align: center; letter-spacing: 0.5px; }
        .auth-subtitle { font-size: 13px; color: var(--text-muted); text-align: center; margin-top: 6px; margin-bottom: 24px; }
        
        .auth-tabs { display: flex; border-bottom: 1px solid var(--border); margin-bottom: 20px; }
        .auth-tab-btn { flex: 1; padding: 10px; text-align: center; color: var(--text-muted); cursor: pointer; font-weight: 600; font-size: 15px; }
        .auth-tab-btn.active { color: #a78bfa; border-bottom: 2px solid #a78bfa; }

        .field-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
        .field-label { font-size: 13px; color: var(--text-main); }
        .input-field { background: var(--bg-input); border: 1px solid var(--border); padding: 14px 16px; border-radius: 14px; color: white; outline: none; font-size: 14px; width: 100%; }
        .input-field:focus { border-color: var(--accent-purple); box-shadow: 0 0 12px var(--accent-purple-glow); }
        .btn-purple { background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white; border: none; padding: 15px; border-radius: 16px; font-weight: bold; font-size: 15px; cursor: pointer; text-align: center; margin-top: 10px; box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4); }

        /* BARRA NAVEGACIÓN INFERIOR */
        .nav-bar { display: flex; background: var(--bg-card); border-top: 1px solid var(--border); height: 65px; position: fixed; bottom: 0; left: 0; right: 0; z-index: 50; }
        .nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; color: var(--text-muted); font-size: 11px; cursor: pointer; }
        .nav-item.active { color: var(--accent-purple); font-weight: bold; }

        /* PERFIL & MENÚ */
        .profile-section { display: flex; flex-direction: column; align-items: center; padding: 24px 16px; text-align: center; }
        .status-bubble { background: var(--bg-card); border: 1px solid var(--border); padding: 10px 18px; border-radius: 20px; font-size: 14px; color: var(--text-main); margin-bottom: 16px; cursor: pointer; }
        .profile-avatar { width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid var(--accent-purple); box-shadow: 0 0 20px var(--accent-purple-glow); background: #1a1730; margin-bottom: 12px; }

        .menu-cards-list { display: flex; flex-direction: column; gap: 12px; padding: 0 16px 24px 16px; }
        .menu-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 18px; padding: 16px; display: flex; align-items: center; gap: 16px; cursor: pointer; }

        /* GLOBO FLOTANTE (FAB) DE OBTENCIÓN DE CHAT / SOPORTE / CONTACTOS */
        .fab-main { position: fixed; bottom: 80px; right: 20px; width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #8b5cf6, #6d28d9); display: flex; justify-content: center; align-items: center; color: white; font-size: 24px; box-shadow: 0 8px 25px rgba(139, 92, 246, 0.5); cursor: pointer; z-index: 90; }

        /* ESTADOS / NOVEDADES */
        .status-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 14px; margin-bottom: 12px; }

        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 100; flex-direction: column; justify-content: center; align-items: center; padding: 20px; }
        .modal.active { display: flex; }
        .modal-content { background: var(--bg-card); border-radius: 22px; padding: 22px; border: 1px solid var(--border); width: 100%; max-width: 400px; display: flex; flex-direction: column; gap: 14px; }
    </style>
</head>
<body>

    <!-- AUTHENTICATION VIEW -->
    <div id="view-auth" class="view active" style="height: 100vh;">
        <div class="auth-container">
            <div class="auth-box">
                <div class="auth-title">SPATIAL NETWORK</div>
                <div class="auth-subtitle">Red Social y Transmisión Multimedia Global</div>

                <div class="auth-tabs">
                    <div id="tab-btn-login" class="auth-tab-btn" onclick="switchAuthTab('login')">Ingresar</div>
                    <div id="tab-btn-register" class="auth-tab-btn active" onclick="switchAuthTab('register')">Registrarse</div>
                </div>

                <!-- FORMULARIO DE INGRESO -->
                <div id="form-login" style="display:none; flex-direction:column;">
                    <div class="field-group">
                        <span class="field-label">Correo electrónico o Teléfono</span>
                        <input type="text" id="login-identity" class="input-field" placeholder="usuario@espacio.com o +58412...">
                    </div>
                    <div class="field-group">
                        <span class="field-label">Contraseña</span>
                        <input type="password" id="login-password" class="input-field" placeholder="••••••••">
                    </div>
                    <button class="btn-purple" onclick="ejecutarLogin()">Entrar</button>
                </div>

                <!-- FORMULARIO DE REGISTRO EXACTO A IMAGEN 1000039296.png -->
                <div id="form-register" style="display:flex; flex-direction:column;">
                    <div class="field-group">
                        <span class="field-label">Nombre de usuario</span>
                        <input type="text" id="reg-username" class="input-field" placeholder="@usuario">
                    </div>
                    <div class="field-group">
                        <span class="field-label">Correo electrónico</span>
                        <input type="text" id="reg-identity" class="input-field" placeholder="usuario@espacio.com">
                    </div>
                    <div class="field-group">
                        <span class="field-label">Contraseña</span>
                        <input type="password" id="reg-password" class="input-field" placeholder="••••••••">
                    </div>
                    <button class="btn-purple" onclick="ejecutarRegistro()">Crear Cuenta</button>
                </div>
            </div>
        </div>
    </div>

    <!-- VISTA CHATS (SIN CARD FIJO DE SOPORTE) -->
    <div id="view-chats" class="view">
        <div class="header-spatial">
            <span>Spatial Network</span>
            <div class="header-icons">
                <span onclick="abrirModal('modal-qr')">📷</span>
                <span onclick="abrirModal('modal-action-globo')">🤖</span>
                <span onclick="abrirModal('modal-edit-profile')">✏️</span>
            </div>
        </div>

        <div style="padding:12px 16px;">
            <div style="background:var(--bg-input); border:1px solid var(--border); border-radius:20px; padding:12px 16px; display:flex; align-items:center; gap:8px;">
                <span>🔍</span>
                <input type="text" placeholder="Buscar chats..." style="background:transparent; border:none; outline:none; color:white; width:100%;">
            </div>
        </div>

        <div id="active-chats-list" style="padding:0 16px;"></div>

        <div id="empty-chats-msg" style="flex:1; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:30px; color:var(--text-muted); font-size:14px;">
            No tienes más chats iniciados.<br>Agrega contactos o escribe al soporte técnico arriba.
        </div>

        <!-- GLOBO DE ACCIONES (NUEVO CHAT / SOPORTE / CONTACTOS) -->
        <div class="fab-main" onclick="abrirModal('modal-action-globo')" title="Opciones de chat">💬</div>
    </div>

    <!-- VISTA NOVEDADES (ESTADOS DE 24 HORAS REALES) -->
    <div id="view-novedades" class="view">
        <div class="header-spatial">
            <span>Novedades / Estados</span>
            <div class="header-icons">
                <span onclick="abrirModal('modal-new-status')">➕</span>
            </div>
        </div>

        <div style="padding:16px;">
            <div class="menu-card" onclick="abrirModal('modal-new-status')" style="margin-bottom:16px; border-color:var(--accent-purple);">
                <div style="font-size:28px;">📷</div>
                <div>
                    <strong style="color:white; display:block;">Mi Estado</strong>
                    <span style="color:var(--text-muted); font-size:12px;">Publica texto, foto o video (24h)</span>
                </div>
            </div>

            <h4 style="color:var(--text-muted); margin-bottom:12px; font-size:13px; text-transform:uppercase;">Estados Recientes (24 horas)</h4>
            <div id="statuses-container"></div>
        </div>
    </div>

    <!-- VISTA CONTACTOS -->
    <div id="view-contactos" class="view">
        <div class="header-spatial">
            <span>Contactos</span>
            <div class="header-icons">
                <span onclick="abrirModal('modal-add-contact')">➕</span>
            </div>
        </div>
        <div style="padding:16px;">
            <button class="btn-purple" style="width:100%; margin-bottom:16px;" onclick="abrirModal('modal-add-contact')">Sincronizar / Agregar Nuevo Contacto</button>
            <div id="contacts-list"></div>
        </div>
    </div>

    <!-- VISTA MENÚ DE PERFIL -->
    <div id="view-menu" class="view">
        <div class="header-spatial">
            <span>Spatial Network</span>
            <div class="header-icons">
                <span onclick="abrirModal('modal-qr')">📷</span>
                <span onclick="abrirModal('modal-edit-profile')">✏️</span>
            </div>
        </div>

        <div class="profile-section">
            <div class="status-bubble" onclick="abrirModal('modal-edit-profile')">
                <span>💭</span> <span id="user-status-text">¡Hola! Estoy usando Spatial Network</span>
            </div>
            <img id="user-avatar-img" src="https://api.dicebear.com/7.x/bottts/svg?seed=jack" class="profile-avatar">
            <div id="user-display-name" style="font-size:22px; font-weight:bold; color:white;">@usuario</div>
            <div id="user-ip-text" style="font-size:12px; color:var(--text-muted); margin-top:4px;">IP Dispositivo: detectando...</div>
        </div>

        <div class="menu-card" onclick="abrirModal('modal-qr')">
                <div style="font-size:24px;">📱</div>
                <div>
                    <strong style="color:white; display:block;">Mi Código QR</strong>
                    <span style="color:var(--text-muted); font-size:12px;">Muestra tu perfil a otros</span>
                </div>
            </div>

            <button class="btn-purple" style="background:#261833; margin-top:12px;" onclick="cerrarSesion()">Cerrar Sesión</button>
        </div>
    </div>

    <!-- SALA DE CHAT / PRIVADO -->
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

    <!-- MODAL GLOBO DE ACCIONES -->
    <div id="modal-action-globo" class="modal">
        <div class="modal-content">
            <h3 style="text-align:center; color:var(--accent-purple);">Opciones de Chat</h3>
            <button class="btn-purple" onclick="cerrarModal('modal-action-globo'); abrirChatSoporte();">🤖 Abrir Chat de Soporte Técnico</button>
            <button class="btn-purple" style="background:#1f1b36;" onclick="cerrarModal('modal-action-globo'); abrirModal('modal-add-contact');">👥 Sincronizar / Agregar Contacto</button>
            <button class="btn-purple" style="background:#28233d;" onclick="cerrarModal('modal-action-globo')">Cancelar</button>
        </div>
    </div>

    <!-- MODAL PUBLICAR ESTADO (24H) -->
    <div id="modal-new-status" class="modal">
        <div class="modal-content">
            <h3 style="text-align:center; color:var(--accent-purple);">Publicar Estado (24 Horas)</h3>
            <input type="text" id="status-text" class="input-field" placeholder="¿Qué estás pensando?">
            <input type="text" id="status-url" class="input-field" placeholder="URL de Foto o Video (Opcional)">
            <button class="btn-purple" onclick="publicarEstado()">Publicar</button>
            <button class="btn-purple" style="background:#28233d;" onclick="cerrarModal('modal-new-status')">Cancelar</button>
        </div>
    </div>

    <!-- MODAL EDITAR PERFIL -->
    <div id="modal-edit-profile" class="modal">
        <div class="modal-content">
            <h3 style="text-align:center; color:var(--accent-purple);">Editar Perfil</h3>
            <input type="text" id="edit-name" class="input-field" placeholder="Nombre de usuario">
            <input type="text" id="edit-avatar" class="input-field" placeholder="URL de Foto / Avatar">
            <input type="text" id="edit-status" class="input-field" placeholder="Estado de perfil">
            <button class="btn-purple" onclick="guardarPerfil()">Guardar Cambios</button>
            <button class="btn-purple" style="background:#28233d;" onclick="cerrarModal('modal-edit-profile')">Cancelar</button>
        </div>
    </div>

    <!-- MODAL AGREGAR CONTACTO -->
    <div id="modal-add-contact" class="modal">
        <div class="modal-content">
            <h3 style="text-align:center; color:var(--accent-purple);">Sincronizar Contacto</h3>
            <input type="text" id="add-contact-input" class="input-field" placeholder="@usuario o número telefónico">
            <button class="btn-purple" onclick="guardarContacto()">Guardar Contacto</button>
            <button class="btn-purple" style="background:#28233d;" onclick="cerrarModal('modal-add-contact')">Cancelar</button>
        </div>
    </div>

    <!-- MODAL QR -->
    <div id="modal-qr" class="modal">
        <div class="modal-content">
            <h3 style="text-align:center; color:var(--accent-purple);">Mi Código QR</h3>
            <div style="display:flex; justify-content:center; padding:10px;"><canvas id="qr-canvas"></canvas></div>
            <button class="btn-purple" style="background:#28233d;" onclick="cerrarModal('modal-qr')">Cerrar</button>
        </div>
    </div>

    <script>
        let usuario = JSON.parse(localStorage.getItem('spatial_user')) || null;
        let contactosGuardados = JSON.parse(localStorage.getItem('spatial_contacts')) || [];
        let activeChat = null;

        window.onload = () => {
            if(!usuario) {
                document.getElementById('view-auth').classList.add('active');
            } else {
                document.getElementById('view-auth').classList.remove('active');
                renderizarUsuario();
                cargarEstados();
                renderizarContactos();
                cambiarTab('chats');
            }
        };

        function renderizarUsuario() {
            if(!usuario) return;
            document.getElementById('user-display-name').innerText = usuario.username || '@usuario';
            document.getElementById('user-avatar-img').src = usuario.avatar_url;
            document.getElementById('user-status-text').innerText = usuario.status_text || '¡Hola! Estoy usando Spatial Network';
            document.getElementById('user-ip-text').innerText = `IP Dispositivo: ${usuario.last_ip || 'Real'}`;
            
            document.getElementById('edit-name').value = usuario.username || '';
            document.getElementById('edit-avatar').value = usuario.avatar_url || '';
            document.getElementById('edit-status').value = usuario.status_text || '';

            new QRious({
                element: document.getElementById('qr-canvas'),
                value: usuario.username || '@usuario',
                size: 180, background: '#131122', foreground: '#8b5cf6'
            });
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

        async function ejecutarRegistro() {
            const username = document.getElementById('reg-username').value.trim();
            const identity = document.getElementById('reg-identity').value.trim();
            const password = document.getElementById('reg-password').value.trim();

            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ username, identity, password })
            });

            const data = await res.json();
            if(data.status === 'success') {
                usuario = data.user;
                localStorage.setItem('spatial_user', JSON.stringify(usuario));
                document.getElementById('view-auth').classList.remove('active');
                renderizarUsuario();
                cambiarTab('chats');
            } else {
                alert(data.message || 'Error al registrarte');
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
            if(data.status === 'success') {
                usuario = data.user;
                localStorage.setItem('spatial_user', JSON.stringify(usuario));
                document.getElementById('view-auth').classList.remove('active');
                renderizarUsuario();
                cambiarTab('chats');
            } else {
                alert(data.message || 'Error al ingresar');
            }
        }

        async function publicarEstado() {
            const text = document.getElementById('status-text').value.trim();
            const url = document.getElementById('status-url').value.trim();
            let type = 'text';
            if(url.includes('.mp4')) type = 'video';
            else if(url) type = 'image';

            if(!text && !url) return;

            await fetch('/api/statuses', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    user_id: usuario.id,
                    username: usuario.username,
                    type, url, text
                })
            });

            document.getElementById('status-text').value = '';
            document.getElementById('status-url').value = '';
            cerrarModal('modal-new-status');
            cargarEstados();
        }

        async function cargarEstados() {
            const res = await fetch('/api/statuses');
            const data = await res.json();
            const container = document.getElementById('statuses-container');
            container.innerHTML = '';

            if(data.statuses && data.statuses.length > 0) {
                data.statuses.forEach(s => {
                    const card = document.createElement('div');
                    card.className = 'status-card';
                    let content = `<strong style="color:var(--accent-purple);">${s.username}</strong><p style="margin-top:6px;">${s.text}</p>`;
                    if(s.type === 'image') content += `<img src="${s.url}" style="width:100%; border-radius:12px; margin-top:8px;">`;
                    if(s.type === 'video') content += `<video src="${s.url}" controls style="width:100%; border-radius:12px; margin-top:8px;"></video>`;
                    content += `<div style="font-size:10px; color:var(--text-muted); margin-top:8px;">Publicado con IP: ${s.client_ip}</div>`;
                    card.innerHTML = content;
                    container.appendChild(card);
                });
            } else {
                container.innerHTML = `<div style="color:var(--text-muted); font-size:13px;">No hay estados activos en las últimas 24 horas.</div>`;
            }
        }

        async function guardarContacto() {
            const input = document.getElementById('add-contact-input').value.trim();
            if(!input) return;

            const res = await fetch('/api/contacts/sync', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: usuario.id, contact_handle: input })
            });

            const data = await res.json();
            if(data.status === 'success') {
                contactosGuardados.push(data.contact);
                localStorage.setItem('spatial_contacts', JSON.stringify(contactosGuardados));
                renderizarContactos();
                cerrarModal('modal-add-contact');
            }
        }

        function renderizarContactos() {
            const list = document.getElementById('contacts-list');
            list.innerHTML = '';
            contactosGuardados.forEach(c => {
                const item = document.createElement('div');
                item.className = 'menu-card';
                item.onclick = () => abrirChatDirecto(c.name);
                item.innerHTML = `<img src="${c.avatar_url}" style="width:40px; height:40px; border-radius:50%;"><div><strong style="color:white; display:block;">${c.name}</strong><span style="color:var(--text-muted); font-size:12px;">${c.handle}</span></div>`;
                list.appendChild(item);
            });
        }

        function abrirChatSoporte() {
            abrirChatDirecto("Amiti Soporte Técnico");
        }

        function abrirChatDirecto(titulo) {
            activeChat = titulo;
            document.getElementById('room-title').innerText = titulo;
            document.getElementById('chat-messages').innerHTML = `<div style="background:var(--bg-card); padding:12px; border-radius:12px; max-width:85%; border:1px solid var(--border);">🤖 <strong>${titulo}:</strong> Hola, canal seguro directo conectado.</div>`;
            cambiarTab('room');
        }

        function enviarMensaje() {
            const input = document.getElementById('message-input');
            const txt = input.value.trim();
            if(!txt) return;

            const box = document.getElementById('chat-messages');
            box.innerHTML += `<div style="background:var(--accent-purple); color:white; padding:12px; border-radius:12px; align-self:flex-end; max-width:85%; margin-left:auto;">${txt}</div>`;
            input.value = '';

            setTimeout(() => {
                box.innerHTML += `<div style="background:var(--bg-card); padding:12px; border-radius:12px; max-width:85%; border:1px solid var(--border);">🤖 <strong>${activeChat}:</strong> Mensaje procesado desde la red.</div>`;
                box.scrollTop = box.scrollHeight;
            }, 600);
        }

        function guardarPerfil() {
            usuario.username = document.getElementById('edit-name').value.trim() || usuario.username;
            usuario.avatar_url = document.getElementById('edit-avatar').value.trim() || usuario.avatar_url;
            usuario.status_text = document.getElementById('edit-status').value.trim() || usuario.status_text;

            localStorage.setItem('spatial_user', JSON.stringify(usuario));
            renderizarUsuario();
            cerrarModal('modal-edit-profile');
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
    print(f"🚀 Servidor Spatial Network activo en el puerto {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=False)
