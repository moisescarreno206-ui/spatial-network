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

# --- RUTAS ---
@app.route("/manifest.json")
def manifest():
    return jsonify({
        "short_name": "SpatialNet",
        "name": "Spatial Social Network",
        "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/2097/2097276.png", "type": "image/png", "sizes": "192x192"}],
        "start_url": "/",
        "background_color": "#0d0e15",
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
        body { background: #000; color: #ffffff; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        
        /* PANTALLA DE INGRESO */
        .auth-container { background: radial-gradient(circle at top, #1a1c2e, #0d0e15); width: 100%; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; width: 100%; max-width: 400px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); text-align: center; }
        h1 { font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #a855f7, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 6px; }
        p.sub { font-size: 0.85rem; color: #94a3b8; margin-bottom: 20px; }
        
        .tabs { display: flex; border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px; }
        .tab-btn { flex: 1; padding: 10px; background: none; border: none; color: #94a3b8; font-size: 0.95rem; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; transition: 0.3s; }
        .tab-btn.active { color: #a855f7; border-bottom-color: #a855f7; }
        
        .form-group { margin-bottom: 15px; text-align: left; }
        label { font-size: 0.8rem; color: #cbd5e1; display: block; margin-bottom: 5px; }
        input, select { width: 100%; padding: 12px; background: rgba(255, 255, 255, 0.07); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 10px; color: #fff; font-size: 0.95rem; outline: none; }
        input:focus { border-color: #a855f7; }
        
        /* Contenedor de la foto de perfil */
        .avatar-picker { display: flex; align-items: center; gap: 15px; margin-top: 5px; }
        .avatar-preview { width: 50px; height: 50px; border-radius: 50%; background: #a855f7; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; overflow: hidden; }
        .avatar-preview img { width: 100%; height: 100%; object-fit: cover; }
        
        button.btn-submit { width: 100%; padding: 12px; background: linear-gradient(135deg, #8b5cf6, #6366f1); border: none; border-radius: 10px; color: #fff; font-size: 1rem; font-weight: 700; cursor: pointer; margin-top: 10px; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4); }

        /* INTERFAZ PRINCIPAL */
        #app-view { display: none; flex-direction: column; width: 100%; height: 100vh; background-color: #000; }
        .header-app { padding: 15px; font-size: 1.4em; font-weight: 800; background: linear-gradient(135deg, #a855f7, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: flex; justify-content: space-between; align-items: center; }
        .sync-btn { font-size: 0.8rem; background: rgba(168, 85, 247, 0.2); color: #a855f7; border: 1px solid #a855f7; padding: 6px 12px; border-radius: 15px; cursor: pointer; }

        /* Historias */
        .stories-bar { display: flex; overflow-x: auto; padding: 10px 15px; gap: 12px; border-bottom: 1px solid #222; }
        .story-item { display: flex; flex-direction: column; align-items: center; gap: 5px; font-size: 0.75em; color: #aaa; flex-shrink: 0; }
        .story-circle { width: 60px; height: 60px; background: #333; border-radius: 50%; border: 2px solid #a855f7; display: flex; align-items: center; justify-content: center; font-size: 1.5em; color: white; overflow: hidden; }
        .story-circle img { width: 100%; height: 100%; object-fit: cover; }
        
        /* Lista de Chats */
        .chat-list { display: flex; flex-direction: column; padding: 5px 0; overflow-y: auto; flex-grow: 1; padding-bottom: 70px; }
        .chat-item { display: flex; align-items: center; padding: 12px 15px; gap: 15px; text-decoration: none; color: white; cursor: pointer; }
        .chat-item:active { background-color: #111; }
        .avatar { width: 55px; height: 55px; background: #30363d; border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-weight: bold; overflow: hidden; }
        .avatar img { width: 100%; height: 100%; object-fit: cover; }
        .chat-info { display: flex; flex-direction: column; gap: 4px; overflow: hidden; width: 100%; }
        .chat-name { font-weight: bold; font-size: 1em; }
        .chat-preview { font-size: 0.85em; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

        /* Barra de Navegación */
        .nav-bar { position: fixed; bottom: 0; width: 100%; display: flex; justify-content: space-around; padding: 12px 0; background: #121212; border-top: 1px solid #222; font-size: 0.9em; }
        .nav-item { color: #888; text-align: center; text-decoration: none; cursor: pointer; }
        .nav-item.active { color: #a855f7; font-weight: bold; }
        
        /* Modal de Sincronización */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(5px); justify-content: center; align-items: center; z-index: 10; }
        .modal-content { background: #161b22; padding: 20px; border-radius: 15px; width: 90%; max-width: 350px; border: 1px solid #30363d; }
    </style>
</head>
<body>
    
    <!-- PANTALLA DE INGRESO / REGISTRO -->
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
                    <label>Nombre completo</label>
                    <input type="text" id="username" placeholder="Tu Nombre">
                </div>

                <!-- Foto de perfil (Galería o Genérica) -->
                <div class="form-group" id="grp-avatar" style="display:none;">
                    <label>Foto de Perfil</label>
                    <div class="avatar-picker">
                        <div class="avatar-preview" id="avatar-preview-box">👤</div>
                        <input type="file" id="file-avatar" accept="image/*" onchange="cargarFoto(event)" style="display:none;">
                        <button type="button" onclick="document.getElementById('file-avatar').click()" style="padding: 8px 12px; background: #30363d; border: none; color: white; border-radius: 8px; cursor: pointer;">Galería</button>
                    </div>
                </div>

                <div class="form-group">
                    <label>Correo o Teléfono</label>
                    <input type="text" id="identificador" placeholder="correo@ejemplo.com o +58..." required>
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
        <!-- Cabecera corregida sin plagio -->
        <div class="header-app">
            <span>Spatial Network</span>
            <button class="sync-btn" onclick="abrirSincronizacion()">+ Sincronizar</button>
        </div>

        <!-- Historias -->
        <div class="stories-bar">
            <div class="story-item">
                <div class="story-circle" id="user-my-story">+</div>
                <span>Crear historia</span>
            </div>
            <div class="story-item">
                <div class="story-circle" style="border-color: #555;"></div>
                <span>Ricky</span>
            </div>
            <div class="story-item">
                <div class="story-circle" style="border-color: #555;"></div>
                <span>Momo</span>
            </div>
        </div>

        <!-- Lista de Chats -->
        <div class="chat-list" id="chats-container">
            <!-- Soporte Oficial Amiti -->
            <div class="chat-item">
                <div class="avatar" style="background-color: #a855f7;">🤖</div>
                <div class="chat-info">
                    <span class="chat-name">Amiti Soporte</span>
                    <span class="chat-preview">Reporta aquí cualquier falla o queja...</span>
                </div>
            </div>
        </div>

        <!-- Navegación -->
        <div class="nav-bar">
            <div class="nav-item active">Chats</div>
            <div class="nav-item" onclick="abrirSincronizacion()">Buscar</div>
            <div class="nav-item">Notificaciones</div>
            <div class="nav-item">Menú</div>
        </div>
    </div>

    <!-- MODAL DE SINCRONIZACIÓN / BÚSQUEDA DE CONTACTOS -->
    <div class="modal" id="sync-modal">
        <div class="modal-content">
            <h3 style="margin-bottom: 15px; color: #a855f7;">Añadir o Sincronizar</h3>
            <p style="font-size: 0.85rem; color: #aaa; margin-bottom: 15px;">Escribe el correo o teléfono de un contacto para iniciar chat:</p>
            <input type="text" id="sync-input" placeholder="Correo o número de teléfono..." style="margin-bottom: 15px;">
            <div style="display: flex; gap: 10px;">
                <button class="btn-submit" onclick="sincronizarContacto()" style="margin-top:0;">Agregar</button>
                <button type="button" onclick="cerrarSincronizacion()" style="padding: 12px; background: #333; border: none; color: white; border-radius: 10px; cursor: pointer;">Cerrar</button>
            </div>
        </div>
    </div>

    <!-- JAVASCRIPT -->
    <script>
        let fotoPerfilData = null;

        function setModo(modo) {
            const btnLogin = document.getElementById('tab-login');
            const btnReg = document.getElementById('tab-reg');
            const grpUser = document.getElementById('grp-user');
            const grpAvatar = document.getElementById('grp-avatar');
            const btnText = document.getElementById('btn-text');

            if (modo === 'login') {
                btnLogin.classList.add('active');
                btnReg.classList.remove('active');
                grpUser.style.display = 'none';
                grpAvatar.style.display = 'none';
                btnText.innerText = 'Ingresar a la Red';
            } else {
                btnReg.classList.add('active');
                btnLogin.classList.remove('active');
                grpUser.style.display = 'block';
                grpAvatar.style.display = 'block';
                btnText.innerText = 'Crear cuenta';
            }
        }

        // Cargar vista previa de la imagen de galería
        function cargarFoto(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    fotoPerfilData = e.target.result;
                    document.getElementById('avatar-preview-box').innerHTML = `<img src="${fotoPerfilData}">`;
                }
                reader.readAsDataURL(file);
            }
        }

        function procesarAuth(event) {
            event.preventDefault();
            document.getElementById('auth-view').style.display = 'none';
            document.getElementById('app-view').style.display = 'flex';

            if (fotoPerfilData) {
                document.getElementById('user-my-story').innerHTML = `<img src="${fotoPerfilData}">`;
            }
        }

        // Funciones del Modal de Contactos
        function abrirSincronizacion() {
            document.getElementById('sync-modal').style.display = 'flex';
        }

        function cerrarSincronizacion() {
            document.getElementById('sync-modal').style.display = 'none';
        }

        function sincronizarContacto() {
            const val = document.getElementById('sync-input').value.trim();
            if (val) {
                const chatContainer = document.getElementById('chats-container');
                const nuevoChat = document.createElement('div');
                nuevoChat.className = 'chat-item';
                nuevoChat.innerHTML = `
                    <div class="avatar">${val.charAt(0).toUpperCase()}</div>
                    <div class="chat-info">
                        <span class="chat-name">${val}</span>
                        <span class="chat-preview">Contacto vinculado correctamente</span>
                    </div>
                `;
                chatContainer.appendChild(nuevoChat);
                document.getElementById('sync-input').value = '';
                cerrarSincronizacion();
            }
        }
    </script>
</body>
</html>
    """
    return render_template_string(html_publico)

if __name__ == '__main__':
    app.run(debug=True)
    
