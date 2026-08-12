import os
import requests
from flask import Flask, request, jsonify, render_template_string
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

# --- LÓGICA DE MODERACIÓN ---
def es_comportamiento_indebido(mensaje):
    palabras_prohibidas = ['spam', 'ilegal', 'hackeo', 'abuso']
    return any(p in mensaje.lower() for p in palabras_prohibidas)

def reportar_al_servidor_principal(usuario, mensaje):
    try:
        data = {"usuario": usuario, "alerta": "comportamiento_indebido", "contenido": mensaje}
        headers = {"X-Amiti-Auth": TOKEN_ENLACE}
        requests.post(f"{SERVIDOR_1_URL}/api/v1/alertas", json=data, headers=headers, timeout=5)
    except Exception as e:
        print(f"Fallo reporte: {e}")

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
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #090a10; color: #ffffff; min-height: 100vh; overflow: hidden; }
        
        /* AUTH CONTAINER */
        .auth-container { background: radial-gradient(circle at top, #1c1335, #090a10); width: 100%; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .card { background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(16px); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 24px; padding: 25px; width: 100%; max-width: 400px; box-shadow: 0 20px 40px rgba(0,0,0,0.6); text-align: center; }
        h1 { font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #c084fc, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 6px; }
        p.sub { font-size: 0.85rem; color: #94a3b8; margin-bottom: 20px; }
        
        .tabs { display: flex; border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px; }
        .tab-btn { flex: 1; padding: 10px; background: none; border: none; color: #94a3b8; font-size: 0.95rem; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab-btn.active { color: #a855f7; border-bottom-color: #a855f7; }
        
        .form-group { margin-bottom: 15px; text-align: left; }
        label { font-size: 0.8rem; color: #cbd5e1; display: block; margin-bottom: 5px; }
        input, textarea { width: 100%; padding: 12px; background: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 12px; color: #fff; font-size: 0.95rem; outline: none; }
        
        button.btn-submit { width: 100%; padding: 12px; background: linear-gradient(135deg, #a855f7, #6366f1); border: none; border-radius: 12px; color: #fff; font-size: 1rem; font-weight: 700; cursor: pointer; margin-top: 10px; box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4); }

        /* INTERFAZ PRINCIPAL */
        #app-view { display: none; flex-direction: column; width: 100%; height: 100vh; background-color: #090a10; position: relative; }
        .header-app { padding: 16px; font-size: 1.3em; font-weight: 800; background: #0f111a; border-bottom: 1px solid #1e202e; display: flex; justify-content: space-between; align-items: center; }
        .header-title { background: linear-gradient(135deg, #c084fc, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header-icons { display: flex; gap: 15px; font-size: 1.2rem; cursor: pointer; color: #a855f7; }

        /* SECCIONES DE NAVEGACIÓN */
        .section-view { display: none; flex-direction: column; flex: 1; overflow-y: auto; padding-bottom: 75px; }
        .section-view.active { display: flex; }

        /* BUSCADOR ESTILO IMAGEN 1 */
        .search-box { padding: 12px 15px; }
        .search-input { width: 100%; padding: 10px 16px; background: #151824; border: 1px solid #252836; border-radius: 20px; color: #fff; font-size: 0.9rem; outline: none; }

        /* LISTA DE CHATS Y CONTACTOS */
        .chat-list { display: flex; flex-direction: column; }
        .chat-item { display: flex; align-items: center; padding: 12px 16px; gap: 14px; text-decoration: none; color: white; cursor: pointer; border-bottom: 1px solid #121420; }
        .chat-item:active { background-color: #151824; }
        .avatar { width: 50px; height: 50px; background: #252836; border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-weight: bold; overflow: hidden; font-size: 1.1rem; color: #a855f7; position: relative; }
        .avatar img { width: 100%; height: 100%; object-fit: cover; }
        .chat-info { display: flex; flex-direction: column; gap: 3px; flex: 1; overflow: hidden; }
        .chat-top-line { display: flex; justify-content: space-between; align-items: center; }
        .chat-name { font-weight: 700; font-size: 0.98rem; color: #f1f5f9; }
        .chat-time { font-size: 0.75rem; color: #64748b; }
        .chat-preview { font-size: 0.85rem; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

        /* FAB (BOTÓN FLOTANTE ESTILO IMAGEN 1) */
        .fab { position: fixed; bottom: 80px; right: 20px; width: 56px; height: 56px; background: linear-gradient(135deg, #a855f7, #6366f1); border-radius: 18px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: white; box-shadow: 0 8px 20px rgba(168, 85, 247, 0.5); cursor: pointer; z-index: 5; }

        /* PANTALLA NOVEDADES / ESTADOS (IMAGEN 3) */
        .section-subtitle { padding: 15px 16px 5px; font-size: 0.85rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
        .status-ring { padding: 2px; border: 2px solid #a855f7; border-radius: 50%; }
        .add-status-badge { position: absolute; bottom: 0; right: 0; background: #a855f7; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; color: white; border: 2px solid #090a10; }

        /* PANTALLA CONTACTOS (IMAGEN 2) */
        .action-item { display: flex; align-items: center; padding: 14px 16px; gap: 15px; cursor: pointer; }
        .action-icon { width: 44px; height: 44px; background: rgba(168, 85, 247, 0.15); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: #a855f7; }
        .action-text { font-weight: 600; font-size: 0.95rem; color: #f1f5f9; }

        /* PANTALLA PERFIL / MENÚ (IMAGEN 4) */
        .profile-header { padding: 30px 20px 20px; display: flex; flex-direction: column; align-items: center; text-align: center; position: relative; background: radial-gradient(circle at top, #1b1333, transparent); }
        .profile-avatar-container { position: relative; margin-bottom: 12px; }
        .profile-avatar-lg { width: 110px; height: 110px; border-radius: 50%; background: #252836; border: 3px solid #a855f7; overflow: hidden; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; }
        .profile-avatar-lg img { width: 100%; height: 100%; object-fit: cover; }
        .status-thought-bubble { background: #1e2030; border: 1px solid #33374d; padding: 6px 14px; border-radius: 15px; font-size: 0.8rem; color: #cbd5e1; margin-bottom: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); max-width: 80%; }
        .profile-name-lg { font-size: 1.3rem; font-weight: 800; color: #fff; }
        .profile-handle { font-size: 0.88rem; color: #94a3b8; margin-top: 2px; }
        .btn-edit-header { position: absolute; top: 15px; right: 15px; background: none; border: none; font-size: 1.3rem; color: #a855f7; cursor: pointer; }

        .settings-list { padding: 10px 16px; display: flex; flex-direction: column; gap: 8px; }
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

        /* BARRA DE NAVEGACIÓN INFERIOR (ESTILO IMAGEN 1, 2 y 3) */
        .nav-bar { position: fixed; bottom: 0; width: 100%; display: flex; justify-content: space-around; padding: 10px 0; background: #0f111a; border-top: 1px solid #1e202e; font-size: 0.8rem; z-index: 10; }
        .nav-item { color: #64748b; text-align: center; text-decoration: none; cursor: pointer; flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; }
        .nav-item .icon { font-size: 1.2rem; }
        .nav-item.active { color: #a855f7; font-weight: bold; }

        /* MODALES */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); justify-content: center; align-items: center; z-index: 30; }
        .modal-content { background: #121420; padding: 22px; border-radius: 20px; width: 90%; max-width: 380px; border: 1px solid #252836; }
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
                    <input type="text" id="reg-name" placeholder="Ej. Moisés Carreño">
                </div>
                <div class="form-group" id="grp-handle" style="display:none;">
                    <label>Usuario (@tag)</label>
                    <input type="text" id="reg-handle" placeholder="Ej. @Jack12747">
                </div>

                <div class="form-group">
                    <label>Correo o Teléfono</label>
                    <input type="text" id="identificador" placeholder="correo@ejemplo.com o 0412..." required>
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
                <span onclick="abrirSincronizacion()">➕</span>
                <span onclick="abrirModalEditarPerfil()">✏️</span>
            </div>
        </div>

        <!-- PANTALLA 1: CHATS (IMAGEN 1) -->
        <div class="section-view active" id="sec-chats">
            <div class="search-box">
                <input type="text" class="search-input" placeholder="🔍 Buscar chats o mensajes..." onkeyup="filtrarLista(this.value, 'chats-container')">
            </div>

            <div class="chat-list" id="chats-container">
                <!-- Chat Soporte Amiti -->
                <div class="chat-item" onclick="abrirChat('Amiti Soporte', '🤖', 'En línea')">
                    <div class="avatar" style="background: #a855f7; color:white;">🤖</div>
                    <div class="chat-info">
                        <div class="chat-top-line">
                            <span class="chat-name">Amiti Soporte</span>
                            <span class="chat-time">Ahora</span>
                        </div>
                        <span class="chat-preview">Asistente de inteligencia activo...</span>
                    </div>
                </div>
                
                <!-- Chat Demo -->
                <div class="chat-item" onclick="abrirChat('Ricky', '👨‍💻', 'En línea')">
                    <div class="avatar">👨‍💻</div>
                    <div class="chat-info">
                        <div class="chat-top-line">
                            <span class="chat-name">Ricky</span>
                            <span class="chat-time">1:57 p. m.</span>
                        </div>
                        <span class="chat-preview">¡Hola! ¿Cómo va el despliegue del proyecto?</span>
                    </div>
                </div>
            </div>

            <!-- BOTÓN FLOTANTE (FAB) -->
            <div class="fab" onclick="cambiarSeccion('sec-contactos', document.querySelectorAll('.nav-item')[2])">💬</div>
        </div>

        <!-- PANTALLA 2: NOVEDADES / ESTADOS (IMAGEN 3) -->
        <div class="section-view" id="sec-novedades">
            <div class="section-subtitle">Estados</div>
            
            <!-- Mi Estado -->
            <div class="chat-item" onclick="subirEstadoPrompt()">
                <div class="avatar" id="my-status-avatar-box">
                    <span id="my-status-avatar-txt">👤</span>
                    <div class="add-status-badge">+</div>
                </div>
                <div class="chat-info">
                    <span class="chat-name">Añadir estado</span>
                    <span class="chat-preview">Desaparece después de 24 horas.</span>
                </div>
            </div>

            <div class="section-subtitle">Recientes</div>
            <div class="chat-list" id="status-list-container">
                <div class="chat-item" onclick="verEstado('Joker😎', 'Que se vaya la luz de noche hoy 💡')">
                    <div class="status-ring">
                        <div class="avatar">🕶️</div>
                    </div>
                    <div class="chat-info">
                        <span class="chat-name">Joker😎</span>
                        <span class="chat-time">10:15 a. m.</span>
                    </div>
                </div>
                <div class="chat-item" onclick="verEstado('La Yiyi ❤️', 'Llegó la luz ⚡')">
                    <div class="status-ring">
                        <div class="avatar">👩</div>
                    </div>
                    <div class="chat-info">
                        <span class="chat-name">La Yiyi ❤️</span>
                        <span class="chat-time">Ayer</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- PANTALLA 3: CONTACTOS (IMAGEN 2) -->
        <div class="section-view" id="sec-contactos">
            <div class="search-box">
                <input type="text" class="search-input" placeholder="🔍 Buscar contactos..." onkeyup="filtrarLista(this.value, 'contacts-list-container')">
            </div>

            <!-- Acciones Rapidas -->
            <div class="action-item" onclick="alert('Crear Nuevo Grupo')">
                <div class="action-icon">👥</div>
                <span class="action-text">Nuevo grupo</span>
            </div>
            <div class="action-item" onclick="abrirSincronizacion()">
                <div class="action-icon">👤➕</div>
                <span class="action-text">Nuevo contacto</span>
            </div>
            <div class="action-item" onclick="alert('Crear Nueva Comunidad')">
                <div class="action-icon">🌐</div>
                <span class="action-text">Nueva comunidad</span>
            </div>

            <div class="section-subtitle">Contactos en Spatial Network</div>
            <div class="chat-list" id="contacts-list-container">
                <div class="chat-item" onclick="abrirMiChatPropio()">
                    <div class="avatar" id="contact-self-avatar">👤</div>
                    <div class="chat-info">
                        <span class="chat-name" id="contact-self-name">Moisés Carreño (Tú)</span>
                        <span class="chat-preview">Envía mensajes a este mismo número</span>
                    </div>
                </div>
                <div class="chat-item" onclick="abrirChat('Alejandro Taxi', '🚖', 'Disponible')">
                    <div class="avatar">🚖</div>
                    <div class="chat-info">
                        <span class="chat-name">Alejandro Taxi</span>
                        <span class="chat-preview">@alejandro_taxi</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- PANTALLA 4: MENÚ / PERFIL (IMAGEN 4) -->
        <div class="section-view" id="sec-perfil">
            <div class="profile-header">
                <button class="btn-edit-header" onclick="abrirModalEditarPerfil()">✏️</button>
                
                <div class="status-thought-bubble" id="profile-thought-display">
                    💭 <span id="profile-thought-text">Ahora mismo estoy...</span>
                </div>

                <div class="profile-avatar-container">
                    <div class="profile-avatar-lg" id="profile-lg-box">👤</div>
                </div>
                
                <div class="profile-name-lg" id="profile-lg-name">Moisés Carreño</div>
                <div class="profile-handle" id="profile-lg-handle">@Jack12747</div>
            </div>

            <div class="settings-list">
                <div class="setting-card" onclick="abrirModalEditarPerfil()">
                    <div class="setting-icon">🔑</div>
                    <div class="setting-info">
                        <span class="setting-title">Cuenta</span>
                        <span class="setting-desc">Notificaciones de seguridad, editar perfil</span>
                    </div>
                </div>
                <div class="setting-card" onclick="alert('Configuración de Privacidad')">
                    <div class="setting-icon">🔒</div>
                    <div class="setting-info">
                        <span class="setting-title">Privacidad</span>
                        <span class="setting-desc">Cuentas bloqueadas, mensajes temporales</span>
                    </div>
                </div>
                <div class="setting-card" onclick="alert('Ajustes de Chats')">
                    <div class="setting-icon">💬</div>
                    <div class="setting-info">
                        <span class="setting-title">Chats</span>
                        <span class="setting-desc">Estilo, fondos de pantalla, historial</span>
                    </div>
                </div>
                <div class="setting-card" onclick="alert('Ajustes de Notificaciones')">
                    <div class="setting-icon">🔔</div>
                    <div class="setting-info">
                        <span class="setting-title">Notificaciones</span>
                        <span class="setting-desc">Tonos de mensajes, grupos y llamadas</span>
                    </div>
                </div>
                <div class="setting-card" onclick="location.reload()" style="border-color: rgba(239, 68, 68, 0.3);">
                    <div class="setting-icon" style="color: #ef4444;">🚪</div>
                    <div class="setting-info">
                        <span class="setting-title" style="color: #ef4444;">Cerrar Sesión</span>
                        <span class="setting-desc">Salir de tu cuenta de Spatial Network</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- PANTALLA SALA DE CHAT INDIVIDUAL -->
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

    <!-- MODAL EDITAR PERFIL (IMAGEN 4) -->
    <div class="modal" id="edit-profile-modal">
        <div class="modal-content">
            <h3 style="margin-bottom: 15px; color: #a855f7;">Editar Perfil</h3>
            <div class="form-group">
                <label>Foto de Perfil</label>
                <input type="file" id="edit-avatar-file" accept="image/*" onchange="previewEditAvatar(event)">
            </div>
            <div class="form-group">
                <label>Nombre Completo</label>
                <input type="text" id="edit-name-input" value="Moisés Carreño">
            </div>
            <div class="form-group">
                <label>Usuario (@tag)</label>
                <input type="text" id="edit-handle-input" value="@Jack12747">
            </div>
            <div class="form-group">
                <label>Pensamiento / Estado Actual</label>
                <input type="text" id="edit-thought-input" value="Ahora mismo estoy...">
            </div>
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <button class="btn-submit" onclick="guardarPerfil()" style="margin-top:0;">Guardar</button>
                <button type="button" onclick="cerrarModalEditarPerfil()" style="padding: 12px; background: #1a1c2e; border: none; color: white; border-radius: 12px; cursor: pointer;">Cancelar</button>
            </div>
        </div>
    </div>

    <!-- MODAL SINCRONIZAR CONTACTO -->
    <div class="modal" id="sync-modal">
        <div class="modal-content">
            <h3 style="margin-bottom: 15px; color: #a855f7;">Sincronizar Contacto</h3>
            <p style="font-size: 0.85rem; color: #aaa; margin-bottom: 15px;">Ingresa el número o correo del usuario:</p>
            <input type="text" id="sync-input" placeholder="Ej. 04127780654..." style="margin-bottom: 15px;">
            <div style="display: flex; gap: 10px;">
                <button class="btn-submit" onclick="sincronizarContacto()" style="margin-top:0;">Agregar</button>
                <button type="button" onclick="cerrarSincronizacion()" style="padding: 12px; background: #1a1c2e; border: none; color: white; border-radius: 12px; cursor: pointer;">Cancelar</button>
            </div>
        </div>
    </div>

    <!-- JAVASCRIPT DE FUNCIONALIDAD -->
    <script>
        let perfilUsuario = {
            nombre: "Moisés Carreño",
            handle: "@Jack12747",
            pensamiento: "Ahora mismo estoy...",
            fotoData: null
        };

        let tempAvatarData = null;
        let chatActualNombre = "";

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
            const regName = document.getElementById('reg-name').value;
            const regHandle = document.getElementById('reg-handle').value;
            
            if (regName) perfilUsuario.nombre = regName;
            if (regHandle) perfilUsuario.handle = regHandle.startsWith('@') ? regHandle : '@' + regHandle;

            actualizarPerfilDOM();

            document.getElementById('auth-view').style.display = 'none';
            document.getElementById('app-view').style.display = 'flex';
        }

        // EDICIÓN DE PERFIL
        function abrirModalEditarPerfil() {
            document.getElementById('edit-name-input').value = perfilUsuario.nombre;
            document.getElementById('edit-handle-input').value = perfilUsuario.handle;
            document.getElementById('edit-thought-input').value = perfilUsuario.pensamiento;
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
            perfilUsuario.nombre = document.getElementById('edit-name-input').value;
            perfilUsuario.handle = document.getElementById('edit-handle-input').value;
            perfilUsuario.pensamiento = document.getElementById('edit-thought-input').value;
            if (tempAvatarData) {
                perfilUsuario.fotoData = tempAvatarData;
            }

            actualizarPerfilDOM();
            cerrarModalEditarPerfil();
        }

        function actualizarPerfilDOM() {
            document.getElementById('profile-lg-name').innerText = perfilUsuario.nombre;
            document.getElementById('profile-lg-handle').innerText = perfilUsuario.handle;
            document.getElementById('profile-thought-text').innerText = perfilUsuario.pensamiento;
            document.getElementById('contact-self-name').innerText = perfilUsuario.nombre + " (Tú)";

            if (perfilUsuario.fotoData) {
                const imgHTML = `<img src="${perfilUsuario.fotoData}">`;
                document.getElementById('profile-lg-box').innerHTML = imgHTML;
                document.getElementById('contact-self-avatar').innerHTML = imgHTML;
                document.getElementById('my-status-avatar-box').innerHTML = imgHTML + `<div class="add-status-badge">+</div>`;
            }
        }

        // CAMBIO DE SECCIONES
        function cambiarSeccion(seccionId, elementoTab) {
            document.querySelectorAll('.section-view').forEach(sec => sec.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            
            document.getElementById(seccionId).classList.add('active');
            if (elementoTab) elementoTab.classList.add('active');
        }

        // VISTA CHAT INDIVIDUAL
        function abrirChat(nombre, avatar, estado) {
            chatActualNombre = nombre;
            document.getElementById('room-name').innerText = nombre;
            document.getElementById('room-status').innerText = estado || 'En línea';
            
            const avatarBox = document.getElementById('room-avatar');
            if (avatar.startsWith('data:image') || avatar.startsWith('http')) {
                avatarBox.innerHTML = `<img src="${avatar}">`;
            } else {
                avatarBox.innerText = avatar;
            }

            const msgBox = document.getElementById('room-messages');
            msgBox.innerHTML = `<div class="msg-bubble received">¡Hola! Has iniciado conversación con ${nombre}.</div>`;

            document.getElementById('chat-room-view').style.display = 'flex';
        }

        function abrirMiChatPropio() {
            abrirChat(perfilUsuario.nombre + " (Tú)", perfilUsuario.fotoData || "👤", "Espacio personal");
        }

        function cerrarChat() {
            document.getElementById('chat-room-view').style.display = 'none';
        }

        function enviarMensaje() {
            const input = document.getElementById('input-msg');
            const texto = input.value.trim();
            if (texto === "") return;

            const msgBox = document.getElementById('room-messages');
            const miMsg = document.createElement('div');
            miMsg.className = 'msg-bubble sent';
            miMsg.innerText = texto;
            msgBox.appendChild(miMsg);

            input.value = "";
            msgBox.scrollTop = msgBox.scrollHeight;

            if (chatActualNombre === "Amiti Soporte") {
                setTimeout(() => {
                    const reply = document.createElement('div');
                    reply.className = 'msg-bubble received';
                    reply.innerText = "He recibido tu reporte. El sistema principal lo está procesando.";
                    msgBox.appendChild(reply);
                    msgBox.scrollTop = msgBox.scrollHeight;
                }, 1000);
            }
        }

        // SINCRONIZAR
        function abrirSincronizacion() {
            document.getElementById('sync-modal').style.display = 'flex';
        }

        function cerrarSincronizacion() {
            document.getElementById('sync-modal').style.display = 'none';
        }

        function sincronizarContacto() {
            const val = document.getElementById('sync-input').value.trim();
            if (val) {
                const container = document.getElementById('contacts-container') || document.getElementById('chats-container');
                const nuevoItem = document.createElement('div');
                const inicial = val.charAt(0).toUpperCase();

                nuevoItem.className = 'chat-item';
                nuevoItem.onclick = function() { abrirChat(val, inicial, 'Contacto Vinculado'); };

                nuevoItem.innerHTML = `
                    <div class="avatar">${inicial}</div>
                    <div class="chat-info">
                        <div class="chat-top-line">
                            <span class="chat-name">${val}</span>
                            <span class="chat-time">Ahora</span>
                        </div>
                        <span class="chat-preview">Contacto vinculado correctamente</span>
                    </div>
                `;

                container.appendChild(nuevoItem);
                document.getElementById('sync-input').value = '';
                cerrarSincronizacion();
                abrirChat(val, inicial, 'Contacto Vinculado');
            }
        }

        // FILTRO DE BUSQUEDA
        function filtrarLista(texto, containerId) {
            const filtro = texto.toLowerCase();
            const items = document.getElementById(containerId).getElementsByClassName('chat-item');
            for (let item of items) {
                const nombre = item.querySelector('.chat-name')?.innerText.toLowerCase() || "";
                if (nombre.includes(filtro)) {
                    item.style.display = "flex";
                } else {
                    item.style.display = "none";
                }
            }
        }

        function subirEstadoPrompt() {
            const texto = prompt("Escribe tu nuevo estado (desaparecerá en 24h):");
            if (texto) {
                const list = document.getElementById('status-list-container');
                const item = document.createElement('div');
                item.className = 'chat-item';
                item.onclick = function() { verEstado(perfilUsuario.nombre, texto); };
                item.innerHTML = `
                    <div class="status-ring">
                        <div class="avatar">${perfilUsuario.fotoData ? `<img src="${perfilUsuario.fotoData}">` : '👤'}</div>
                    </div>
                    <div class="chat-info">
                        <span class="chat-name">${perfilUsuario.nombre} (Tú)</span>
                        <span class="chat-time">Hace un momento</span>
                    </div>
                `;
                list.prepend(item);
            }
        }

        function verEstado(nombre, contenido) {
            alert(`Estado de ${nombre}:\n\n"${contenido}"`);
        }
    </script>
</body>
</html>
    """
    return render_template_string(html_publico)

if __name__ == '__main__':
    app.run(debug=True)
