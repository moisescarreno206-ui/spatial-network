import os
import requests
from flask import Flask, jsonify, render_template_string
from supabase import create_client, Client

app = Flask(__name__)

# --- CONFIGURACIÓN DE ENLACES Y BASE DE DATOS ---
SERVIDOR_1_URL = os.environ.get("SERVIDOR_1_URL", "https://tu-amiti-core.onrender.com")
TOKEN_ENLACE = os.environ.get("TOKEN_ENLACE", "AMITI_LINK_SECURE_KEY_2026")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

# --- RUTAS ---
@app.route("/manifest.json")
def manifest():
    return jsonify({
        "short_name": "SpatialNet",
        "name": "Spatial Social Network",
        "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/2097/2097276.png", "type": "image/png", "sizes": "192x192"}],
        "start_url": "/",
        "background_color": "#090a10",
        "theme_color": "#a855f7",
        "display": "standalone"
    })

@app.route("/")
def portada():
    html_publico = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spatial Network</title>
    <link rel="manifest" href="/manifest.json">
    <!-- Librerías para QR Code y Escáner de Cámara -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrious/4.0.2/qrious.min.js"></script>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #090a10; color: #ffffff; min-height: 100vh; overflow: hidden; }
        
        /* AUTH CONTAINER */
        .auth-container { background: radial-gradient(circle at top, #1c1335, #090a10); width: 100%; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .card { background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(16px); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 24px; padding: 25px; width: 100%; max-width: 400px; box-shadow: 0 20px 40px rgba(0,0,0,0.6); text-align: center; }
        h1 { font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #c084fc, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 6px; }
        p.sub { font-size: 0.85rem; color: #94a3b8; margin-bottom: 20px; }
        
        .tabs { display: flex; border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px; }
        .tab-btn { flex: 1; padding: 10px; background: none; border: none; color: #94a3b8; font-size: 0.85rem; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab-btn.active { color: #a855f7; border-bottom-color: #a855f7; }
        
        .form-group { margin-bottom: 15px; text-align: left; }
        label { font-size: 0.8rem; color: #cbd5e1; display: block; margin-bottom: 5px; }
        input, select, textarea { width: 100%; padding: 12px; background: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 12px; color: #fff; font-size: 0.95rem; outline: none; }
        
        button.btn-submit { width: 100%; padding: 12px; background: linear-gradient(135deg, #a855f7, #6366f1); border: none; border-radius: 12px; color: #fff; font-size: 1rem; font-weight: 700; cursor: pointer; margin-top: 10px; box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4); }

        /* INTERFAZ PRINCIPAL */
        #app-view { display: none; flex-direction: column; width: 100%; height: 100vh; background-color: #090a10; position: relative; }
        .header-app { padding: 16px; font-size: 1.3em; font-weight: 800; background: #0f111a; border-bottom: 1px solid #1e202e; display: flex; justify-content: space-between; align-items: center; }
        .header-title { background: linear-gradient(135deg, #c084fc, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header-icons { display: flex; gap: 15px; font-size: 1.2rem; cursor: pointer; color: #a855f7; }

        /* SECCIONES DE NAVEGACIÓN */
        .section-view { display: none; flex-direction: column; flex: 1; overflow-y: auto; padding-bottom: 75px; }
        .section-view.active { display: flex; }

        .search-box { padding: 12px 16px; }
        .search-input { width: 100%; padding: 10px 16px; background: #151824; border: 1px solid #252836; border-radius: 20px; color: #fff; font-size: 0.9rem; outline: none; }

        /* LISTA DE CHATS Y CONTACTOS */
        .chat-list { display: flex; flex-direction: column; }
        .chat-item { display: flex; align-items: center; padding: 12px 16px; gap: 14px; text-decoration: none; color: white; cursor: pointer; border-bottom: 1px solid #121420; }
        .chat-item:active { background-color: #151824; }
        .avatar { width: 50px; height: 50px; background: #252836; border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-weight: bold; overflow: hidden; font-size: 1.1rem; color: #a855f7; position: relative; }
        .avatar img, .avatar video { width: 100%; height: 100%; object-fit: cover; }
        .chat-info { display: flex; flex-direction: column; gap: 3px; flex: 1; overflow: hidden; }
        .chat-top-line { display: flex; justify-content: space-between; align-items: center; }
        .chat-name { font-weight: 700; font-size: 0.98rem; color: #f1f5f9; }
        .chat-time { font-size: 0.75rem; color: #64748b; }
        .chat-preview { font-size: 0.85rem; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

        .badge-type { background: rgba(168, 85, 247, 0.2); color: #c084fc; font-size: 0.68rem; padding: 2px 6px; border-radius: 6px; border: 1px solid rgba(168, 85, 247, 0.4); margin-left: 6px; }

        .empty-state { padding: 40px 20px; text-align: center; color: #64748b; font-size: 0.9rem; }

        /* BOTONES FLOTANTES (FAB) */
        .fab { position: fixed; bottom: 80px; right: 20px; width: 56px; height: 56px; background: linear-gradient(135deg, #a855f7, #6366f1); border-radius: 18px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: white; box-shadow: 0 8px 20px rgba(168, 85, 247, 0.5); cursor: pointer; z-index: 5; }
        
        /* BOTÓN FLOTANTE DE SOPORTE AMITI (ENCIMA DEL FAB DE CONTACTOS) */
        .fab-support { position: fixed; bottom: 148px; right: 20px; width: 50px; height: 50px; background: linear-gradient(135deg, #10b981, #059669); border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; color: white; box-shadow: 0 6px 15px rgba(16, 185, 129, 0.4); cursor: pointer; z-index: 5; transition: transform 0.2s; }
        .fab-support:active { transform: scale(0.92); }

        /* NOVEDADES / ESTADOS */
        .section-subtitle { padding: 15px 16px 5px; font-size: 0.85rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
        .status-ring { padding: 2px; border: 2px solid #a855f7; border-radius: 50%; }
        .add-status-badge { position: absolute; bottom: 0; right: 0; background: #a855f7; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; color: white; border: 2px solid #090a10; }

        /* ACCIONES Y LISTAS */
        .action-item { display: flex; align-items: center; padding: 12px 16px; gap: 15px; cursor: pointer; border-bottom: 1px solid #121420; }
        .action-icon { width: 44px; height: 44px; background: rgba(168, 85, 247, 0.15); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: #a855f7; }
        .action-text { font-weight: 600; font-size: 0.95rem; color: #f1f5f9; }

        /* PERFIL Y MENÚ */
        .profile-header-card { padding: 25px 20px; display: flex; flex-direction: column; align-items: center; text-align: center; background: radial-gradient(circle at top, #1b1333, transparent); border-bottom: 1px solid #1e202e; cursor: pointer; transition: background 0.2s; }
        .profile-header-card:hover { background: rgba(168, 85, 247, 0.08); }
        .profile-avatar-lg { width: 100px; height: 100px; border-radius: 50%; background: #252836; border: 3px solid #a855f7; overflow: hidden; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; margin-bottom: 10px; }
        .profile-avatar-lg img { width: 100%; height: 100%; object-fit: cover; }
        .status-thought-bubble { background: #1e2030; border: 1px solid #33374d; padding: 6px 14px; border-radius: 15px; font-size: 0.8rem; color: #cbd5e1; margin-bottom: 8px; }
        .profile-name-lg { font-size: 1.25rem; font-weight: 800; color: #fff; }
        .profile-handle { font-size: 0.85rem; color: #94a3b8; }
        .profile-contact-info { font-size: 0.8rem; color: #a855f7; margin-top: 4px; font-weight: 600; }

        .settings-list { padding: 15px 16px; display: flex; flex-direction: column; gap: 8px; }
        .setting-card { display: flex; align-items: center; padding: 14px; background: #121420; border-radius: 16px; gap: 15px; border: 1px solid #1e202e; cursor: pointer; }
        .setting-icon { font-size: 1.2rem; color: #a855f7; width: 30px; text-align: center; }
        .setting-info { display: flex; flex-direction: column; gap: 2px; }
        .setting-title { font-size: 0.95rem; font-weight: 700; color: #f1f5f9; }
        .setting-desc { font-size: 0.8rem; color: #64748b; }

        /* VISTA CHAT INDIVIDUAL */
        #chat-room-view { display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: #090a10; z-index: 20; flex-direction: column; }
        .chat-room-header { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: #0f111a; border-bottom: 1px solid #1e202e; }
        .back-btn { font-size: 1.4rem; color: #a855f7; background: none; border: none; cursor: pointer; }
        .messages-container { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; background: #06070a; }
        .msg-bubble { max-width: 75%; padding: 10px 14px; border-radius: 16px; font-size: 0.92rem; line-height: 1.35; }
        .msg-bubble.received { background: #151824; color: #fff; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #202436; }
        .msg-bubble.sent { background: linear-gradient(135deg, #8b5cf6, #6366f1); color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; }
        .chat-input-bar { display: flex; padding: 12px 16px; background: #0f111a; border-top: 1px solid #1e202e; gap: 10px; align-items: center; }
        .chat-input-bar input { flex: 1; padding: 10px 16px; background: #151824; border: 1px solid #252836; border-radius: 20px; color: #fff; outline: none; }
        .send-btn { background: #a855f7; color: white; border: none; padding: 10px 18px; border-radius: 20px; font-weight: bold; cursor: pointer; }

        /* BARRA DE NAVEGACIÓN INFERIOR */
        .nav-bar { position: fixed; bottom: 0; width: 100%; display: flex; justify-content: space-around; padding: 10px 0; background: #0f111a; border-top: 1px solid #1e202e; font-size: 0.8rem; z-index: 10; }
        .nav-item { color: #64748b; text-align: center; text-decoration: none; cursor: pointer; flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; }
        .nav-item .icon { font-size: 1.2rem; }
        .nav-item.active { color: #a855f7; font-weight: bold; }

        /* MODALES */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); justify-content: center; align-items: center; z-index: 30; }
        .modal-content { background: #121420; padding: 22px; border-radius: 20px; width: 90%; max-width: 380px; border: 1px solid #252836; max-height: 90vh; overflow-y: auto; }

        .qr-box { display: flex; flex-direction: column; align-items: center; gap: 15px; margin: 15px 0; }
        .qr-box canvas { background: white; padding: 10px; border-radius: 12px; }
        
        #qr-reader { width: 100%; border-radius: 12px; overflow: hidden; border: 1px solid #a855f7; margin-top: 10px; }
        
        .status-viewer-media { width: 100%; max-height: 350px; object-fit: contain; border-radius: 12px; margin-top: 10px; }
        
        /* REPRODUCTOR DE VIDEO EMBUTIDO */
        .video-player-frame { width: 100%; height: 210px; border-radius: 12px; border: none; margin-top: 10px; }
    </style>
</head>
<body>
    
    <!-- INGRESO / REGISTRO -->
    <div class="auth-container" id="auth-view">
        <div class="card">
            <h1>SPATIAL NETWORK</h1>
            <p class="sub">Red Social y Mensajería Global</p>
            
            <div class="tabs">
                <button class="tab-btn active" id="tab-login" onclick="setModo('login')">Ingresar</button>
                <button class="tab-btn" id="tab-reg" onclick="setModo('reg')">Registrarse</button>
            </div>

            <form onsubmit="procesarAuth(event)">
                <div class="form-group" id="grp-user" style="display:none;">
                    <label>Nombre Completo</label>
                    <input type="text" id="reg-name" placeholder="Tu nombre">
                </div>
                <div class="form-group" id="grp-handle" style="display:none;">
                    <label>Usuario (@tag)</label>
                    <input type="text" id="reg-handle" placeholder="@usuario">
                </div>

                <div class="form-group">
                    <label>Correo o Teléfono</label>
                    <input type="text" id="identificador" placeholder="Correo o Teléfono" required>
                </div>
                <div class="form-group">
                    <label>Contraseña</label>
                    <input type="password" id="password" placeholder="••••••••" required>
                </div>
                <button class="btn-submit" type="submit" id="btn-text">Ingresar a la Red</button>
            </form>
        </div>
    </div>

    <!-- INTERFAZ PRINCIPAL -->
    <div id="app-view">
        <div class="header-app">
            <span class="header-title" id="header-main-title">Spatial Network</span>
            <div class="header-icons">
                <span onclick="abrirSincronizacion('scan')" title="Escanear QR">📷</span>
                <span onclick="abrirSincronizacion('num')" title="Agregar contacto">➕</span>
                <span onclick="abrirModalEditarPerfil()" title="Editar Perfil">✏️</span>
            </div>
        </div>

        <!-- PANTALLA 1: CHATS -->
        <div class="section-view active" id="sec-chats">
            <div class="search-box">
                <input type="text" class="search-input" placeholder="🔍 Buscar chats..." onkeyup="filtrarLista(this.value, 'chats-container')">
            </div>

            <div class="chat-list" id="chats-container">
                <div class="empty-state">No tienes chats iniciados.<br>Agrega contactos, grupos o escanea un QR.</div>
            </div>

            <!-- GLOBO DE SOPORTE AMITI (ENCIMA DEL GLOBO DE AGREGAR CONTACTOS) -->
            <div class="fab-support" onclick="abrirChatSoporteAmiti()" title="Soporte Técnico Amiti IA">🤖</div>
            
            <!-- GLOBO DE AGREGAR CONTACTOS -->
            <div class="fab" onclick="cambiarSeccion('sec-contactos', document.querySelectorAll('.nav-item')[2])">💬</div>
        </div>

        <!-- PANTALLA 2: NOVEDADES / ESTADOS -->
        <div class="section-view" id="sec-novedades">
            <div class="section-subtitle">Mi Estado</div>
            
            <div class="chat-item" onclick="abrirModalPublicarEstado()">
                <div class="avatar" id="my-status-avatar-box">
                    <span id="my-status-avatar-txt">👤</span>
                    <div class="add-status-badge">+</div>
                </div>
                <div class="chat-info">
                    <span class="chat-name">Añadir estado</span>
                    <span class="chat-preview">Sube una imagen, video o texto (24h)</span>
                </div>
            </div>

            <div class="section-subtitle">Estados Recientes</div>
            <div class="chat-list" id="status-list-container">
                <div class="empty-state">No hay estados recientes.</div>
            </div>
        </div>

        <!-- PANTALLA 3: CONTACTOS, GRUPOS Y COMUNIDADES -->
        <div class="section-view" id="sec-contactos">
            <div class="search-box">
                <input type="text" class="search-input" placeholder="🔍 Buscar contactos o comunidades..." onkeyup="filtrarLista(this.value, 'contacts-list-container')">
            </div>

            <div class="action-item" onclick="abrirChatSoporteAmiti()">
                <div class="action-icon">🤖</div>
                <span class="action-text">Soporte Técnico Amiti IA</span>
            </div>

            <div class="action-item" onclick="abrirSincronizacion('num')">
                <div class="action-icon">👤➕</div>
                <span class="action-text">Nuevo Contacto / Escanear QR</span>
            </div>

            <div class="action-item" onclick="abrirModalCrearGrupo()">
                <div class="action-icon">👥➕</div>
                <span class="action-text">Crear Grupo</span>
            </div>

            <div class="action-item" onclick="abrirModalCrearComunidad()">
                <div class="action-icon">🌐➕</div>
                <span class="action-text">Crear Comunidad</span>
            </div>

            <div class="section-subtitle">Contactos y Espacios Sincronizados</div>
            <div class="chat-list" id="contacts-list-container">
                <div class="chat-item" onclick="abrirMiChatPropio()">
                    <div class="avatar" id="contact-self-avatar">👤</div>
                    <div class="chat-info">
                        <span class="chat-name" id="contact-self-name">Mi Espacio (Tú)</span>
                        <span class="chat-preview">Mensajes y notas personales</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- PANTALLA 4: MENÚ / PERFIL -->
        <div class="section-view" id="sec-perfil">
            <div class="profile-header-card" onclick="abrirModalEditarPerfil()">
                <div class="status-thought-bubble">
                    💭 <span id="profile-thought-text">Ahora mismo estoy...</span>
                </div>

                <div class="profile-avatar-lg" id="profile-lg-box">👤</div>
                
                <div class="profile-name-lg" id="profile-lg-name">Usuario</div>
                <div class="profile-handle" id="profile-lg-handle">@usuario</div>
                <div class="profile-contact-info" id="profile-lg-contact">Contacto: Privado</div>
            </div>

            <div class="settings-list">
                <div class="setting-card" onclick="abrirModalReproductorVideo()">
                    <div class="setting-icon">🎬</div>
                    <div class="setting-info">
                        <span class="setting-title">Reproductor de Video</span>
                        <span class="setting-desc">Ver videos de YouTube, TikTok o enlaces Web</span>
                    </div>
                </div>
                <div class="setting-card" onclick="abrirModalEditarPerfil()">
                    <div class="setting-icon">✏️</div>
                    <div class="setting-info">
                        <span class="setting-title">Editar Perfil</span>
                        <span class="setting-desc">Foto, nombre, usuario y privacidad</span>
                    </div>
                </div>
                <div class="setting-card" onclick="abrirSincronizacion('qr')">
                    <div class="setting-icon">📱</div>
                    <div class="setting-info">
                        <span class="setting-title">Mi Código QR / Escáner</span>
                        <span class="setting-desc">Muestra o escanea un código con tu cámara</span>
                    </div>
                </div>
                <div class="setting-card" onclick="abrirModalCrearGrupo()">
                    <div class="setting-icon">👥</div>
                    <div class="setting-info">
                        <span class="setting-title">Crear Nuevo Grupo</span>
                        <span class="setting-desc">Chatea con múltiples personas</span>
                    </div>
                </div>
                <div class="setting-card" onclick="abrirModalCrearComunidad()">
                    <div class="setting-icon">🌐</div>
                    <div class="setting-info">
                        <span class="setting-title">Crear Comunidad</span>
                        <span class="setting-desc">Organiza canales y salas temáticas</span>
                    </div>
                </div>
                <div class="setting-card" onclick="cerrarSesion()" style="border-color: rgba(239, 68, 68, 0.3);">
                    <div class="setting-icon" style="color: #ef4444;">🚪</div>
                    <div class="setting-info">
                        <span class="setting-title" style="color: #ef4444;">Cerrar Sesión</span>
                        <span class="setting-desc">Salir de tu cuenta</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- VISTA SALA DE CHAT INDIVIDUAL O GRUPAL -->
        <div id="chat-room-view">
            <div class="chat-room-header">
                <button class="back-btn" onclick="cerrarChat()">←</button>
                <div class="avatar" id="room-avatar" style="width:40px; height:40px; font-size:1rem;">?</div>
                <div>
                    <h4 id="room-name" style="font-size: 0.98rem;">Contacto</h4>
                    <span id="room-status" style="font-size: 0.75rem; color: #a855f7;">En línea</span>
                </div>
            </div>

            <div class="messages-container" id="room-messages"></div>

            <div class="chat-input-bar">
                <input type="text" id="input-msg" placeholder="Escribe un mensaje..." onkeypress="if(event.key==='Enter') enviarMensaje()">
                <button class="send-btn" onclick="enviarMensaje()">Enviar</button>
            </div>
        </div>

        <!-- BARRA DE NAVEGACIÓN INFERIOR -->
        <div class="nav-bar">
            <div class="nav-item active" onclick="cambiarSeccion('sec-chats', this)">
                <span class="icon">💬</span>
                <span>Chats</span>
            </div>
            <div class="nav-item" onclick="cambiarSeccion('sec-novedades', this)">
                <span class="icon">⭕</span>
                <span>Novedades</span>
            </div>
            <div class="nav-item" onclick="cambiarSeccion('sec-contactos', this)">
                <span class="icon">👥</span>
                <span>Contactos</span>
            </div>
            <div class="nav-item" onclick="cambiarSeccion('sec-perfil', this)">
                <span class="icon">⚙️</span>
                <span>Menú</span>
            </div>
        </div>
    </div>

    <!-- MODAL REPRODUCTOR DE VIDEO MULTIPLATAFORMA -->
    <div class="modal" id="video-player-modal">
        <div class="modal-content">
            <h3 style="margin-bottom: 15px; color: #a855f7;">Reproductor de Video</h3>
            <div class="form-group">
                <label>Enlace del Video (YouTube, MP4, Vimeo, etc.)</label>
                <input type="text" id="video-url-input" placeholder="https://www.youtube.com/watch?v=...">
            </div>
            <button class="btn-submit" onclick="cargarVideoPlataforma()" style="margin-top:5px;">Cargar Video</button>
            
            <div id="video-container-box" style="margin-top:15px;"></div>

            <button type="button" onclick="cerrarModalReproductorVideo()" style="margin-top:15px; padding: 12px; background: #1a1c2e; border: none; color: white; border-radius: 12px; cursor: pointer; width:100%;">Cerrar</button>
        </div>
    </div>

    <!-- MODAL EDITAR PERFIL -->
    <div class="modal" id="edit-profile-modal">
        <div class="modal-content">
            <h3 style="margin-bottom: 15px; color: #a855f7;">Editar Perfil</h3>
            <div class="form-group">
                <label>Foto de Perfil (Galería)</label>
                <input type="file" id="edit-avatar-file" accept="image/*" onchange="previewEditAvatar(event)">
            </div>
            <div class="form-group">
                <label>Nombre Completo</label>
                <input type="text" id="edit-name-input">
            </div>
            <div class="form-group">
                <label>Usuario (@tag)</label>
                <input type="text" id="edit-handle-input">
            </div>
            <div class="form-group">
                <label>Teléfono o Correo</label>
                <input type="text" id="edit-contact-input">
            </div>
            <div class="form-group">
                <label>Visibilidad de mi Teléfono/Correo</label>
                <select id="edit-privacy-select">
                    <option value="publico">Público (Visible en el chat)</option>
                    <option value="privado">Privado (Oculto para todos)</option>
                </select>
            </div>
            <div class="form-group">
                <label>Pensamiento / Estado Actual</label>
                <input type="text" id="edit-thought-input">
            </div>
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <button class="btn-submit" onclick="guardarPerfil()" style="margin-top:0;">Guardar</button>
                <button type="button" onclick="cerrarModalEditarPerfil()" style="padding: 12px; background: #1a1c2e; border: none; color: white; border-radius: 12px; cursor: pointer;">Cancelar</button>
            </div>
        </div>
    </div>

    <!-- MODAL PUBLICAR ESTADO -->
    <div class="modal" id="publish-status-modal">
        <div class="modal-content">
            <h3 style="margin-bottom: 15px; color: #a855f7;">Publicar Estado</h3>
            <div class="form-group">
                <label>Seleccionar Imagen o Video</label>
                <input type="file" id="status-media-file" accept="image/*,video/*" onchange="previewStatusMedia(event)">
            </div>
            <div class="form-group">
                <label>Texto / Comentario (Opcional)</label>
                <input type="text" id="status-text-input" placeholder="Escribe un comentario...">
            </div>
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <button class="btn-submit" onclick="guardarEstado()" style="margin-top:0;">Publicar</button>
                <button type="button" onclick="cerrarModalPublicarEstado()" style="padding: 12px; background: #1a1c2e; border: none; color: white; border-radius: 12px; cursor: pointer;">Cancelar</button>
            </div>
        </div>
    </div>

    <!-- MODAL CREAR GRUPO -->
    <div class="modal" id="create-group-modal">
        <div class="modal-content">
            <h3 style="margin-bottom: 15px; color: #a855f7;">Crear Nuevo Grupo</h3>
            <div class="form-group">
                <label>Nombre del Grupo</label>
                <input type="text" id="group-name-input" placeholder="Ej. Equipo Spatial">
            </div>
            <div class="form-group">
                <label>Descripción</label>
                <input type="text" id="group-desc-input" placeholder="Propósito del grupo...">
            </div>
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <button class="btn-submit" onclick="crearGrupo()" style="margin-top:0;">Crear Grupo</button>
                <button type="button" onclick="cerrarModalCrearGrupo()" style="padding: 12px; background: #1a1c2e; border: none; color: white; border-radius: 12px; cursor: pointer;">Cancelar</button>
            </div>
        </div>
    </div>
    <!-- MODAL CREAR COMUNIDAD -->
    <div class="modal" id="create-community-modal">
        <div class="modal-content">
            <h3 style="margin-bottom: 15px; color: #a855f7;">Crear Comunidad</h3>
            <div class="form-group">
                <label>Nombre de la Comunidad</label>
                <input type="text" id="community-name-input" placeholder="Ej. Developers Latam">
            </div>
            <div class="form-group">
                <label>Descripción de la Comunidad</label>
                <textarea id="community-desc-input" rows="3" placeholder="Información temática..."></textarea>
            </div>
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <button class="btn-submit" onclick="crearComunidad()" style="margin-top:0;">Crear Comunidad</button>
                <button type="button" onclick="cerrarModalCrearComunidad()" style="padding: 12px; background: #1a1c2e; border: none; color: white; border-radius: 12px; cursor: pointer;">Cancelar</button>
            </div>
        </div>
    </div>

    <!-- MODAL VER ESTADO -->
    <div class="modal" id="view-status-modal">
        <div class="modal-content" style="text-align:center;">
            <h3 id="status-view-title" style="color: #a855f7;">Estado</h3>
            <p id="status-view-text" style="font-size:0.9rem; color:#cbd5e1; margin-top:5px;"></p>
            <div id="status-view-media-container"></div>
            <button type="button" onclick="cerrarModalVerEstado()" style="margin-top:15px; padding: 10px 20px; background: #a855f7; border: none; color: white; border-radius: 12px; cursor: pointer; width:100%;">Cerrar</button>
        </div>
    </div>

    <!-- MODAL SINCRONIZAR, MI QR Y ESCÁNER DE CÁMARA -->
    <div class="modal" id="sync-modal">
        <div class="modal-content">
            <h3 style="margin-bottom: 15px; color: #a855f7;">Sincronizar y QR</h3>
            
            <div class="tabs">
                <button class="tab-btn active" id="tab-sync-num" onclick="setSyncMode('num')">Agregar</button>
                <button class="tab-btn" id="tab-sync-qr" onclick="setSyncMode('qr')">Mi QR</button>
                <button class="tab-btn" id="tab-sync-scan" onclick="setSyncMode('scan')">Escanear</button>
            </div>

            <!-- TAB 1: INGRESAR MANUAL -->
            <div id="sync-sec-num">
                <div class="form-group">
                    <label>Ingresa el número o correo del usuario</label>
                    <input type="text" id="sync-input" placeholder="Ingrese número o correo">
                </div>
                <button class="btn-submit" onclick="sincronizarContacto()">Agregar Amigo</button>
            </div>

            <!-- TAB 2: CÓDIGO QR GENERADO -->
            <div id="sync-sec-qr" style="display:none;" class="qr-box">
                <p style="font-size:0.85rem; color:#aaa; text-align:center;">Muestra este código para que te agreguen:</p>
                <canvas id="qr-canvas"></canvas>
            </div>

            <!-- TAB 3: ESCÁNER DE CÁMARA QR -->
            <div id="sync-sec-scan" style="display:none;">
                <p style="font-size:0.85rem; color:#aaa; text-align:center;">Apunta con tu cámara al código QR de tu amigo:</p>
                <div id="qr-reader"></div>
            </div>

            <button type="button" onclick="cerrarSincronizacion()" style="margin-top:15px; padding: 12px; background: #1a1c2e; border: none; color: white; border-radius: 12px; cursor: pointer; width:100%;">Cerrar</button>
        </div>
    </div>

    <!-- JAVASCRIPT DE FUNCIONALIDAD, ESCÁNER, NOTIFICACIONES Y REPRODUCTOR -->
    <script>
        // ESTADO GLOBAL CON PERSISTENCIA LOCAL
        let usuarioActual = JSON.parse(localStorage.getItem('spatial_user')) || null;
        let contactosBD = JSON.parse(localStorage.getItem('spatial_contacts')) || [];
        let chatsBD = JSON.parse(localStorage.getItem('spatial_chats')) || {};
        let estadosBD = JSON.parse(localStorage.getItem('spatial_statuses')) || [];
        let ticketsSoporteBD = JSON.parse(localStorage.getItem('spatial_support_tickets')) || [];

        let tempAvatarData = null;
        let tempStatusMediaData = null;
        let tempStatusMediaType = "";
        let chatActualKey = "";
        let html5QrCodeScanner = null;

        // CONTACTO DE SOPORTE AMITI
        const AMITI_SUPPORT_OBJ = {
            id: "amiti_support",
            nombre: "Amiti (Soporte IA)",
            contacto: "Centro de Soporte y Reportes",
            tipo: "Soporte",
            avatar: "🤖"
        };

        // INICIALIZAR AL CÁRGAR PÁGINA
        window.onload = function() {
            solicitarPermisoNotificaciones();
            if (usuarioActual) {
                mostrarAppPrincipal();
            }
        };

        // SISTEMA DE NOTIFICACIONES WEB
        function solicitarPermisoNotificaciones() {
            if ("Notification" in window && Notification.permission !== "granted" && Notification.permission !== "denied") {
                Notification.requestPermission();
            }
        }

        function lanzarNotificacion(titulo, cuerpo) {
            if ("Notification" in window && Notification.permission === "granted") {
                new Notification(titulo, {
                    body: cuerpo,
                    icon: "https://cdn-icons-png.flaticon.com/512/2097/2097276.png"
                });
            }
        }

        function setModo(modo) {
            const btnLogin = document.getElementById('tab-login');
            const btnReg = document.getElementById('tab-reg');
            const grpUser = document.getElementById('grp-user');
            const grpHandle = document.getElementById('grp-handle');
            const btnText = document.getElementById('btn-text');

            if (modo === 'login') {
                btnLogin.classList.add('active');
                btnReg.classList.remove('active');
                grpUser.style.display = 'none';
                grpHandle.style.display = 'none';
                btnText.innerText = 'Ingresar a la Red';
            } else {
                btnReg.classList.add('active');
                btnLogin.classList.remove('active');
                grpUser.style.display = 'block';
                grpHandle.style.display = 'block';
                btnText.innerText = 'Crear cuenta';
            }
        }

        function procesarAuth(event) {
            event.preventDefault();
            const regName = document.getElementById('reg-name').value.trim();
            const regHandle = document.getElementById('reg-handle').value.trim();
            const identificador = document.getElementById('identificador').value.trim();
            
            usuarioActual = {
                nombre: regName || "Usuario",
                handle: regHandle ? (regHandle.startsWith('@') ? regHandle : '@' + regHandle) : "@usuario",
                contacto: identificador,
                privacidadContacto: "privado",
                pensamiento: "¡Hola! Estoy usando Spatial Network",
                fotoData: null
            };

            guardarSesion();
            mostrarAppPrincipal();
        }

        function guardarSesion() {
            localStorage.setItem('spatial_user', JSON.stringify(usuarioActual));
        }

        function cerrarSesion() {
            localStorage.removeItem('spatial_user');
            location.reload();
        }

        function mostrarAppPrincipal() {
            document.getElementById('auth-view').style.display = 'none';
            document.getElementById('app-view').style.display = 'flex';
            actualizarPerfilDOM();
            renderizarContactos();
            renderizarChats();
            renderizarEstados();
        }

        // SOPORTE AMITI IA
        function abrirChatSoporteAmiti() {
            abrirChat(AMITI_SUPPORT_OBJ);
        }

        // REPRODUCTOR DE VIDEO
        function abrirModalReproductorVideo() {
            document.getElementById('video-player-modal').style.display = 'flex';
        }

        function cerrarModalReproductorVideo() {
            document.getElementById('video-player-modal').style.display = 'none';
            document.getElementById('video-container-box').innerHTML = "";
        }

        function cargarVideoPlataforma() {
            const url = document.getElementById('video-url-input').value.trim();
            const box = document.getElementById('video-container-box');
            if (!url) return;

            let htmlEmbed = "";

            if (url.includes("youtube.com") || url.includes("youtu.be")) {
                let videoId = "";
                if (url.includes("youtu.be/")) {
                    videoId = url.split("youtu.be/")[1].split("?")[0];
                } else if (url.includes("watch?v=")) {
                    videoId = url.split("watch?v=")[1].split("&")[0];
                }
                if (videoId) {
                    htmlEmbed = `<iframe class="video-player-frame" src="https://www.youtube.com/embed/${videoId}" allowfullscreen></iframe>`;
                }
            } else if (url.includes("vimeo.com")) {
                let vimeoId = url.split("vimeo.com/")[1].split("?")[0];
                htmlEmbed = `<iframe class="video-player-frame" src="https://player.vimeo.com/video/${vimeoId}" allowfullscreen></iframe>`;
            } else {
                htmlEmbed = `<video src="${url}" controls style="width:100%; border-radius:12px; margin-top:10px;"></video>`;
            }

            box.innerHTML = htmlEmbed || `<p style="color:#ef4444; font-size:0.85rem; margin-top:10px;">Formato de enlace no soportado o no válido.</p>`;
        }

        // PERFIL
        function abrirModalEditarPerfil() {
            document.getElementById('edit-name-input').value = usuarioActual.nombre;
            document.getElementById('edit-handle-input').value = usuarioActual.handle;
            document.getElementById('edit-contact-input').value = usuarioActual.contacto || "";
            document.getElementById('edit-privacy-select').value = usuarioActual.privacidadContacto || "privado";
            document.getElementById('edit-thought-input').value = usuarioActual.pensamiento || "";
            document.getElementById('edit-profile-modal').style.display = 'flex';
        }

        function cerrarModalEditarPerfil() {
            document.getElementById('edit-profile-modal').style.display = 'none';
        }

        function previewEditAvatar(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    tempAvatarData = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        }

        function guardarPerfil() {
            usuarioActual.nombre = document.getElementById('edit-name-input').value;
            usuarioActual.handle = document.getElementById('edit-handle-input').value;
            usuarioActual.contacto = document.getElementById('edit-contact-input').value;
            usuarioActual.privacidadContacto = document.getElementById('edit-privacy-select').value;
            usuarioActual.pensamiento = document.getElementById('edit-thought-input').value;
            
            if (tempAvatarData) {
                usuarioActual.fotoData = tempAvatarData;
            }

            guardarSesion();
            actualizarPerfilDOM();
            cerrarModalEditarPerfil();
        }

        function actualizarPerfilDOM() {
            document.getElementById('profile-lg-name').innerText = usuarioActual.nombre;
            document.getElementById('profile-lg-handle').innerText = usuarioActual.handle;
            document.getElementById('profile-thought-text').innerText = usuarioActual.pensamiento;
            document.getElementById('profile-lg-contact').innerText = "Contacto: " + (usuarioActual.privacidadContacto === "publico" ? usuarioActual.contacto : "Privado 🔒");
            document.getElementById('contact-self-name').innerText = usuarioActual.nombre + " (Tú)";

            if (usuarioActual.fotoData) {
                const imgHTML = `<img src="${usuarioActual.fotoData}">`;
                document.getElementById('profile-lg-box').innerHTML = imgHTML;
                document.getElementById('contact-self-avatar').innerHTML = imgHTML;
                document.getElementById('my-status-avatar-box').innerHTML = imgHTML + `<div class="add-status-badge">+</div>`;
            }
        }

        // GRUPOS Y COMUNIDADES
        function abrirModalCrearGrupo() {
            document.getElementById('create-group-modal').style.display = 'flex';
        }

        function cerrarModalCrearGrupo() {
            document.getElementById('create-group-modal').style.display = 'none';
        }
        function crearGrupo() {
            const nombre = document.getElementById('group-name-input').value.trim();
            const desc = document.getElementById('group-desc-input').value.trim();

            if (!nombre) return;

            const grupoObj = {
                id: "g_" + Date.now(),
                nombre: nombre,
                contacto: desc || "Grupo público",
                tipo: "Grupo",
                avatar: "👥"
            };

            contactosBD.push(grupoObj);
            localStorage.setItem('spatial_contacts', JSON.stringify(contactosBD));
            
            renderizarContactos();
            document.getElementById('group-name-input').value = "";
            document.getElementById('group-desc-input').value = "";
            cerrarModalCrearGrupo();
            abrirChat(grupoObj);
        }

        function abrirModalCrearComunidad() {
            document.getElementById('create-community-modal').style.display = 'flex';
        }

        function cerrarModalCrearComunidad() {
            document.getElementById('create-community-modal').style.display = 'none';
        }

        function crearComunidad() {
            const nombre = document.getElementById('community-name-input').value.trim();
            const desc = document.getElementById('community-desc-input').value.trim();

            if (!nombre) return;

            const comunidadObj = {
                id: "com_" + Date.now(),
                nombre: nombre,
                contacto: desc || "Comunidad de Spatial",
                tipo: "Comunidad",
                avatar: "🌐"
            };

            contactosBD.push(comunidadObj);
            localStorage.setItem('spatial_contacts', JSON.stringify(contactosBD));
            
            renderizarContactos();
            document.getElementById('community-name-input').value = "";
            document.getElementById('community-desc-input').value = "";
            cerrarModalCrearComunidad();
            abrirChat(comunidadObj);
        }

        // ESTADOS
        function abrirModalPublicarEstado() {
            document.getElementById('publish-status-modal').style.display = 'flex';
        }

        function cerrarModalPublicarEstado() {
            document.getElementById('publish-status-modal').style.display = 'none';
            tempStatusMediaData = null;
        }

        function previewStatusMedia(event) {
            const file = event.target.files[0];
            if (file) {
                tempStatusMediaType = file.type.startsWith('video') ? 'video' : 'image';
                const reader = new FileReader();
                reader.onload = function(e) {
                    tempStatusMediaData = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        }

        function guardarEstado() {
            const texto = document.getElementById('status-text-input').value;
            if (!tempStatusMediaData && !texto) return;

            const nuevoEstado = {
                id: Date.now(),
                usuario: usuarioActual.nombre,
                fotoPerfil: usuarioActual.fotoData,
                media: tempStatusMediaData,
                tipoMedia: tempStatusMediaType,
                texto: texto,
                hora: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };

            estadosBD.unshift(nuevoEstado);
            localStorage.setItem('spatial_statuses', JSON.stringify(estadosBD));
            renderizarEstados();
            cerrarModalPublicarEstado();
        }

        function renderizarEstados() {
            const container = document.getElementById('status-list-container');
            if (estadosBD.length === 0) {
                container.innerHTML = '<div class="empty-state">No hay estados recientes.</div>';
                return;
            }

            container.innerHTML = "";
            estadosBD.forEach(st => {
                const item = document.createElement('div');
                item.className = 'chat-item';
                item.onclick = function() { verEstado(st); };
                item.innerHTML = `
                    <div class="status-ring">
                        <div class="avatar">${st.fotoPerfil ? `<img src="${st.fotoPerfil}">` : '👤'}</div>
                    </div>
                    <div class="chat-info">
                        <span class="chat-name">${st.usuario}</span>
                        <span class="chat-time">${st.hora}</span>
                    </div>
                `;
                container.appendChild(item);
            });
        }

        function verEstado(st) {
            document.getElementById('status-view-title').innerText = "Estado de " + st.usuario;
            document.getElementById('status-view-text').innerText = st.texto || "";
            
            const mediaBox = document.getElementById('status-view-media-container');
            mediaBox.innerHTML = "";

            if (st.media) {
                if (st.tipoMedia === 'video') {
                    mediaBox.innerHTML = `<video src="${st.media}" class="status-viewer-media" controls autoplay></video>`;
                } else {
                    mediaBox.innerHTML = `<img src="${st.media}" class="status-viewer-media">`;
                }
            }

            document.getElementById('view-status-modal').style.display = 'flex';
        }

        function cerrarModalVerEstado() {
            document.getElementById('view-status-modal').style.display = 'none';
        }

        // ESCÁNER DE CÁMARA Y CÓDIGOS QR
        function abrirSincronizacion(modoInicial = 'num') {
            document.getElementById('sync-modal').style.display = 'flex';
            setSyncMode(modoInicial);
        }

        function cerrarSincronizacion() {
            detenerEscanerCámara();
            document.getElementById('sync-modal').style.display = 'none';
        }

        function setSyncMode(modo) {
            document.getElementById('tab-sync-num').classList.toggle('active', modo === 'num');
            document.getElementById('tab-sync-qr').classList.toggle('active', modo === 'qr');
            document.getElementById('tab-sync-scan').classList.toggle('active', modo === 'scan');

            document.getElementById('sync-sec-num').style.display = modo === 'num' ? 'block' : 'none';
            document.getElementById('sync-sec-qr').style.display = modo === 'qr' ? 'flex' : 'none';
            document.getElementById('sync-sec-scan').style.display = modo === 'scan' ? 'block' : 'none';

            if (modo === 'qr') {
                generarQR();
                detenerEscanerCámara();
            } else if (modo === 'scan') {
                iniciarEscanerCámara();
            } else {
                detenerEscanerCámara();
            }
        }

        function generarQR() {
            if (usuarioActual) {
                new QRious({
                    element: document.getElementById('qr-canvas'),
                    value: usuarioActual.handle + "|" + usuarioActual.contacto,
                    size: 180
                });
            }
        }

        function iniciarEscanerCámara() {
            if (!html5QrCodeScanner) {
                html5QrCodeScanner = new Html5Qrcode("qr-reader");
            }

            html5QrCodeScanner.start(
                { facingMode: "environment" },
                { fps: 10, qrbox: { width: 220, height: 220 } },
                (decodedText) => {
                    procesarQREscaneado(decodedText);
                },
                () => {}
            ).catch(err => {
                console.error("Error al iniciar cámara: ", err);
            });
        }

        function detenerEscanerCámara() {
            if (html5QrCodeScanner && html5QrCodeScanner.isScanning) {
                html5QrCodeScanner.stop().then(() => {
                    html5QrCodeScanner.clear();
                }).catch(err => console.error(err));
            }
        }

        function procesarQREscaneado(codigoTexto) {
            detenerEscanerCámara();
            const partes = codigoTexto.split('|');
            const handle = partes[0] || codigoTexto;
            const contactoVal = partes[1] || codigoTexto;

            const nuevoContacto = {
                id: "c_" + Date.now(),
                nombre: handle,
                contacto: contactoVal,
                privacidadContacto: "publico",
                avatar: "👤"
            };

            contactosBD.push(nuevoContacto);
            localStorage.setItem('spatial_contacts', JSON.stringify(contactosBD));
            renderizarContactos();
            cerrarSincronizacion();
            abrirChat(nuevoContacto);
        }

        function sincronizarContacto() {
            const val = document.getElementById('sync-input').value.trim();
            if (!val) return;

            const nuevoContacto = {
                id: "c_" + Date.now(),
                nombre: val,
                contacto: val,
                privacidadContacto: "publico",
                avatar: "👤"
            };

            contactosBD.push(nuevoContacto);
            localStorage.setItem('spatial_contacts', JSON.stringify(contactosBD));
            
            renderizarContactos();
            document.getElementById('sync-input').value = '';
            cerrarSincronizacion();
            abrirChat(nuevoContacto);
        }

        // CHATS Y CONTACTOS
        function renderizarContactos() {
            const container = document.getElementById('contacts-list-container');
            const selfItem = container.firstElementChild; 
            container.innerHTML = "";
            container.appendChild(selfItem);

            contactosBD.forEach(c => {
                const item = document.createElement('div');
                item.className = 'chat-item';
                item.onclick = function() { abrirChat(c); };
                const tipoBadge = c.tipo ? `<span class="badge-type">${c.tipo}</span>` : '';
                item.innerHTML = `
                    <div class="avatar">${c.avatar.startsWith('data:') ? `<img src="${c.avatar}">` : c.avatar}</div>
                    <div class="chat-info">
                        <span class="chat-name">${c.nombre}${tipoBadge}</span>
                        <span class="chat-preview">${c.contacto}</span>
                    </div>
                `;
                container.appendChild(item);
            });
        }

        function renderizarChats() {
            const container = document.getElementById('chats-container');
            const keys = Object.keys(chatsBD);

            if (keys.length === 0) {
                container.innerHTML = '<div class="empty-state">No tienes chats iniciados.<br>Agrega contactos, grupos o escanea un QR.</div>';
                return;
            }

            container.innerHTML = "";
            keys.forEach(k => {
                const chat = chatsBD[k];
                const ultimoMsg = chat.mensajes.length > 0 ? chat.mensajes[chat.mensajes.length - 1].texto : "Sin mensajes";
                const item = document.createElement('div');
                item.className = 'chat-item';
                item.onclick = function() { abrirChat(chat.contactoObj); };
                const tipoBadge = chat.contactoObj.tipo ? `<span class="badge-type">${chat.contactoObj.tipo}</span>` : '';
                item.innerHTML = `
                    <div class="avatar">${chat.contactoObj.avatar && chat.contactoObj.avatar.startsWith('data:') ? `<img src="${chat.contactoObj.avatar}">` : (chat.contactoObj.avatar || '👤')}</div>
                    <div class="chat-info">
                        <div class="chat-top-line">
                            <span class="chat-name">${chat.contactoObj.nombre}${tipoBadge}</span>
                            <span class="chat-time">${chat.mensajes.length > 0 ? chat.mensajes[chat.mensajes.length - 1].hora : ''}</span>
                        </div>
                        <span class="chat-preview">${ultimoMsg}</span>
                    </div>
                `;
                container.appendChild(item);
            });
        }

        function abrirChat(contactoObj) {
            chatActualKey = contactoObj.id || contactoObj.nombre;
            
            if (!chatsBD[chatActualKey]) {
                chatsBD[chatActualKey] = {
                    contactoObj: contactoObj,
                    mensajes: []
                };
            }
            function abrirMiChatPropio() {
            abrirChat({
                id: "self",
                nombre: usuarioActual.nombre + " (Tú)",
                contacto: usuarioActual.contacto,
                privacidadContacto: usuarioActual.privacidadContacto,
                avatar: usuarioActual.fotoData || "👤"
            });
        }

        function cerrarChat() {
            document.getElementById('chat-room-view').style.display = 'none';
            renderizarChats();
        }

        function enviarMensaje() {
            const input = document.getElementById('input-msg');
            const texto = input.value.trim();
            if (!texto || !chatActualKey) return;

            const horaActual = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            const nuevoMsg = {
                emisor: usuarioActual.nombre,
                texto: texto,
                hora: horaActual
            };

            chatsBD[chatActualKey].mensajes.push(nuevoMsg);
            localStorage.setItem('spatial_chats', JSON.stringify(chatsBD));

            input.value = "";
            cargarMensajesDOM();

            // RESPUESTA AUTOMÁTICA DE AMITI Y REGISTRO DE SOPORTE
            if (chatActualKey === "amiti_support") {
                ticketsSoporteBD.push({
                    usuario: usuarioActual.nombre,
                    handle: usuarioActual.handle,
                    contacto: usuarioActual.contacto,
                    mensaje: texto,
                    fecha: new Date().toLocaleString()
                });
                localStorage.setItem('spatial_support_tickets', JSON.stringify(ticketsSoporteBD));

                setTimeout(() => {
                    const respuestaAmiti = {
                        emisor: "Amiti (Soporte IA)",
                        texto: "¡Hola! He guardado tu mensaje para el equipo de desarrollo y soporte. Si se trata de un reporte de falla, pronto se revisará. ¿Hay algo más en lo que pueda ayudarte?",
                        hora: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    };
                    chatsBD[chatActualKey].mensajes.push(respuestaAmiti);
                    localStorage.setItem('spatial_chats', JSON.stringify(chatsBD));
                    cargarMensajesDOM();
                    lanzarNotificacion("Amiti (Soporte)", "Te ha enviado una respuesta sobre tu reporte.");
                }, 1000);
            }
        }

        function cargarMensajesDOM() {
            const msgBox = document.getElementById('room-messages');
            msgBox.innerHTML = "";

            const lista = chatsBD[chatActualKey].mensajes;
            lista.forEach(m => {
                const bubble = document.createElement('div');
                bubble.className = 'msg-bubble ' + (m.emisor === usuarioActual.nombre ? 'sent' : 'received');
                bubble.innerText = m.texto;
                msgBox.appendChild(bubble);
            });

            msgBox.scrollTop = msgBox.scrollHeight;
        }

        // NAVEGACIÓN
        function cambiarSeccion(seccionId, elementoTab) {
            document.querySelectorAll('.section-view').forEach(sec => sec.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            
            document.getElementById(seccionId).classList.add('active');
            if (elementoTab) elementoTab.classList.add('active');
        }

        function filtrarLista(texto, containerId) {
            const filtro = texto.toLowerCase();
            const items = document.getElementById(containerId).getElementsByClassName('chat-item');
            for (let item of items) {
                const nombre = item.querySelector('.chat-name')?.innerText.toLowerCase() || "";
                item.style.display = nombre.includes(filtro) ? "flex" : "none";
            }
        }
    </script>
</body>
</html>
    """
    return render_template_string(html_publico)

if __name__ == '__main__':
    app.run(debug=True)
