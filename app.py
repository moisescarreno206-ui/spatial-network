import os
import json
import time
from datetime import datetime
import requests
from flask import Flask, render_template_string, jsonify, request, Response

app = Flask(__name__)

# ==========================================
# CONFIGURACIÓN Y VARIABLES DE ENTORNO
# ==========================================
PORT = int(os.environ.get("PORT", 5000))
SERVIDOR_1_URL = os.environ.get("SERVIDOR_1_URL", "https://amiti-spatial-network.onrender.com")
TOKEN_ENLACE = os.environ.get("TOKEN_ENLACE", "spatial-secure-token-2026")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xyzcompany.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "public-anon-key")

# ==========================================
# INICIALIZACIÓN DE SUPABASE DATABASE
# ==========================================
supabaseClient = None
if "supabase.co" in SUPABASE_URL:
    try:
        from supabase import create_client
        supabaseClient = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase iniciado en Servidor 2.")
    except Exception as e:
        print(f"⚠️ No se pudo inicializar Supabase SDK: {e}")

# ==========================================
# RUTAS DE API REST
# ==========================================

@app.route('/api/v1/estado', methods=['GET'])
def estado():
    return jsonify({
        "status": "online",
        "modulo": "Servidor 2 - Mensajería & Contenido Multimedial",
        "centro_de_mando": SERVIDOR_1_URL,
        "supabase_activo": supabaseClient is not None,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/api/v1/recibir', methods=['POST'])
def recibir_desde_servidor1():
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '').strip()

    if token != TOKEN_ENLACE:
        return jsonify({"status": "error", "message": "Token inválido."}), 403

    datos = request.get_json() or {}
    sender_id = datos.get('sender_id', 'sistema_s1')
    receiver_id = datos.get('receiver_id', 'usuario_s2')
    content = datos.get('content', '')

    if not content:
        return jsonify({"status": "error", "message": "Mensaje vacío"}), 400

    if supabaseClient:
        try:
            supabaseClient.table('messages').insert([
                {"sender_id": sender_id, "receiver_id": receiver_id, "content": content}
            ]).execute()
        except Exception as e:
            print(f"Error guardando en Supabase desde S1: {e}")

    return jsonify({
        "status": "success",
        "message": "Mensaje recibido en Servidor 2",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/api/v1/enviar', methods=['POST'])
def enviar_a_servidor1():
    datos = request.get_json() or {}
    usuario_id = datos.get('usuario_id', 'anonimo_s2')
    destino_id = datos.get('destino_id', 'amiti_ia')
    mensaje = datos.get('mensaje', '').strip()

    if not mensaje:
        return jsonify({"status": "error", "message": "El mensaje no puede estar vacío"}), 400

    if supabaseClient:
        try:
            supabaseClient.table('messages').insert([
                {"sender_id": usuario_id, "receiver_id": destino_id, "content": mensaje}
            ]).execute()
        except Exception as e:
            print(f"Error guardando mensaje local: {e}")

    endpoint_s1 = f"{SERVIDOR_1_URL.rstrip('/')}/api/v1/mensaje_entrante"
    headers = {
        "Authorization": f"Bearer {TOKEN_ENLACE}",
        "Content-Type": "application/json"
    }
    payload = {
        "sender_id": usuario_id,
        "receiver_id": destino_id,
        "content": mensaje,
        "origen": "Servidor_2_Mensajeria"
    }

    try:
        res = requests.post(endpoint_s1, json=payload, headers=headers, timeout=10)
        if res.status_code == 200:
            data_respuesta = res.json()
            return jsonify({
                "status": "success",
                "servidor_1_response": data_respuesta,
                "respuesta_amiti": data_respuesta.get("respuesta_amiti", None)
            }), 200
        else:
            return jsonify({"status": "warning", "detalle": res.text}), 502
    except Exception as e:
        return jsonify({"status": "error", "error_detalle": str(e)}), 504

# ==========================================
# PWA ARCHIVOS DE SOPORTE
# ==========================================

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Mensajería & Videos S2",
        "short_name": "SpatialS2",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#050508",
        "theme_color": "#10b981",
        "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/2665/2665038.png", "sizes": "512x512", "type": "image/png"}]
    })

@app.route('/sw.js')
def service_worker():
    sw_code = """
    const CACHE_NAME = 'spatial-v2';
    self.addEventListener('install', (e) => {
        e.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(['/', '/manifest.json'])));
    });
    self.addEventListener('fetch', (e) => {
        e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
    });
    """
    return Response(sw_code, mimetype='application/javascript')

# ==========================================
# INTERFAZ FRONTEND (CON FEED DE VIDEOS)
# ==========================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>Servidor 2 - Mensajería & Videos</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#050508">

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
        
        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            height: 100vh;
            width: 100vw;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* Views Layout */
        .view { display: none; flex: 1; flex-direction: column; height: calc(100vh - 60px); overflow: hidden; position: relative; }
        .view.active { display: flex; }

        /* Auth Screen */
        .auth-container { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 24px; background: radial-gradient(circle at center, #062e22 0%, var(--bg-dark) 100%); }
        .auth-box { width: 100%; max-width: 380px; background: var(--bg-card); border: 1px solid var(--border); padding: 28px; border-radius: 20px; display: flex; flex-direction: column; gap: 16px; }

        /* UI Base Elements */
        .input-field { background: var(--bg-input); border: 1px solid var(--border); padding: 14px; border-radius: 12px; color: white; outline: none; font-size: 15px; }
        .input-field:focus { border-color: var(--accent); }
        .btn-primary { background: var(--accent); color: white; border: none; padding: 14px; border-radius: 12px; font-weight: bold; font-size: 15px; cursor: pointer; text-align: center; }
        .btn-primary:active { background: var(--accent-hover); }

        /* Navigation */
        .nav-bar { display: flex; background: var(--bg-card); border-top: 1px solid var(--border); height: 60px; position: fixed; bottom: 0; left: 0; right: 0; z-index: 50; }
        .nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; color: var(--text-muted); font-size: 11px; cursor: pointer; }
        .nav-item.active { color: var(--accent); font-weight: bold; }

        .header-bar { padding: 14px 16px; background: var(--bg-card); border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-weight: bold; font-size: 17px; }

        /* Chat Components */
        .chat-list { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 10px; }
        .chat-item { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 14px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
        .chat-messages { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; background: #08090f; }
        .message-bubble { max-width: 82%; padding: 12px 16px; border-radius: 18px; font-size: 14px; line-height: 1.4; word-break: break-word; }
        .message-bubble.sent { background: var(--accent); color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
        .message-bubble.received { background: var(--bg-input); color: var(--text-main); align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid var(--border); }
        .message-bubble.amiti { background: var(--amiti-purple); color: white; align-self: flex-start; border-bottom-left-radius: 4px; }

        /* TikTok Feed Component */
        .tiktok-feed { flex: 1; overflow-y: scroll; scroll-snap-type: y mandatory; background: #000; height: 100%; }
        .tiktok-card { height: 100%; width: 100%; scroll-snap-align: start; scroll-snap-stop: always; position: relative; display: flex; justify-content: center; align-items: center; background: #000; }
        .tiktok-card video, .tiktok-card iframe { width: 100%; height: 100%; object-fit: cover; border: none; }

        .badge { background: rgba(16, 185, 129, 0.2); color: var(--accent); padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; }
        .badge-s1 { background: rgba(124, 58, 237, 0.2); color: var(--amiti-purple); padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; }

        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 100; flex-direction: column; justify-content: center; align-items: center; padding: 20px; }
        .modal.active { display: flex; }
        .modal-content { background: var(--bg-card); border-radius: 20px; padding: 20px; border: 1px solid var(--border); width: 100%; max-width: 400px; display: flex; flex-direction: column; gap: 14px; }
    </style>
</head>
<body>

    <!-- VISTA 0: LOGIN -->
    <div id="view-auth" class="view active" style="height: 100vh;">
        <div class="auth-container">
            <div class="auth-box">
                <h2 style="color:var(--accent); text-align:center;">Servidor 2</h2>
                <p style="color:var(--text-muted); font-size:13px; text-align:center;">Mensajería & Videos Verticales</p>
                <input type="text" id="auth-name" class="input-field" placeholder="Tu Nombre">
                <input type="text" id="auth-handle" class="input-field" placeholder="@usuario">
                <button class="btn-primary" onclick="iniciarSesion()">Ingresar</button>
            </div>
        </div>
    </div>

    <!-- VISTA 1: CHATS -->
    <div id="view-chats" class="view">
        <div class="header-bar">
            <span>Mensajes</span>
            <span class="badge">S2 Online</span>
        </div>
        <div id="chats-list" class="chat-list"></div>
    </div>

    <!-- VISTA 2: CHAT ACTIVO -->
    <div id="view-room" class="view">
        <div class="header-bar">
            <div style="display:flex; align-items:center; gap:10px;">
                <button onclick="cerrarChat()" style="background:none; border:none; color:white; font-size:20px; cursor:pointer;">←</button>
                <span id="room-title">@Chat</span>
            </div>
            <span class="badge-s1">S1 Enlazado</span>
        </div>
        <div id="chat-messages" class="chat-messages"></div>
        <div style="padding: 12px; background: var(--bg-card); border-top: 1px solid var(--border); display: flex; gap: 8px;">
            <input type="text" id="message-input" class="input-field" style="flex:1;" placeholder="Mensaje para S1 o Amiti IA..." onkeypress="if(event.key==='Enter') enviarMensajeLocal()">
            <button class="btn-primary" style="padding:0 18px;" onclick="enviarMensajeLocal()">➤</button>
        </div>
    </div>

    <!-- VISTA 3: REPRODUCTOR DE VIDEOS (TIKTOK FEED) -->
    <div id="view-videos" class="view">
        <div id="tiktok-feed" class="tiktok-feed"></div>
    </div>

    <!-- VISTA 4: AJUSTES -->
    <div id="view-menu" class="view">
        <div class="header-bar">Ajustes del Nodo</div>
        <div style="padding: 16px; display: flex; flex-direction: column; gap: 14px;">
            <div style="background:var(--bg-card); padding:16px; border-radius:14px; border:1px solid var(--border);">
                <div style="font-weight:bold;" id="menu-user-name">Usuario</div>
                <div style="color:var(--text-muted); font-size:13px;" id="menu-user-handle">@handle</div>
            </div>
            <button class="btn-primary" onclick="abrirModal('modal-qr')">📷 Código QR y Escáner</button>
            <button class="btn-primary" style="background:#374151;" onclick="cerrarSesion()">Cerrar Sesión</button>
        </div>
    </div>

    <!-- BARRA NAVEGACIÓN -->
    <div id="main-nav" class="nav-bar" style="display:none;">
        <div class="nav-item active" id="nav-chats" onclick="cambiarTab('chats')">💬 Chats</div>
        <div class="nav-item" id="nav-videos" onclick="cambiarTab('videos')">▶️ Videos</div>
        <div class="nav-item" id="nav-menu" onclick="cambiarTab('menu')">⚙️ Menú</div>
    </div>

    <!-- MODAL QR -->
    <div id="modal-qr" class="modal">
        <div class="modal-content">
            <h3 style="text-align:center;">Mi QR</h3>
            <div style="display:flex; justify-content:center; padding:10px;"><canvas id="qr-canvas"></canvas></div>
            <div id="qr-reader" style="width:100%;"></div>
            <button class="btn-primary" onclick="iniciarEscaner()">📷 Escanear Cámara</button>
            <button class="btn-primary" style="background:#374151;" onclick="cerrarModal('modal-qr')">Cerrar</button>
        </div>
    </div>

    <script>
        const SERVIDOR_1_URL = "{{ servidor_1_url }}";
        const SUPABASE_URL = "{{ supabase_url }}";
        const SUPABASE_KEY = "{{ supabase_key }}";

        let supabaseClient = null;
        if (SUPABASE_URL.includes("supabase.co")) {
            supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
        }

        let usuario = JSON.parse(localStorage.getItem('spatial_s2_user')) || null;
        let chatActivo = null;

        // Lista de videos MP4 e Embeds
        const listaVideos = [
            "https://www.w3schools.com/html/mov_bbb.mp4",
            "https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&mute=1"
        ];

        window.onload = () => {
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js').catch(e => console.log(e));
            }
            if (usuario) {
                iniciarApp();
            }
        };

        function iniciarSesion() {
            const name = document.getElementById('auth-name').value.trim();
            const handle = document.getElementById('auth-handle').value.trim();
            if(!name || !handle) return alert('Completa todos los campos');

            usuario = { id: handle.replace('@','').toLowerCase(), name, handle: handle.startsWith('@') ? handle : '@' + handle };
            localStorage.setItem('spatial_s2_user', JSON.stringify(usuario));
            iniciarApp();
        }

        function cerrarSesion() {
            localStorage.removeItem('spatial_s2_user');
            location.reload();
        }

        function iniciarApp() {
            document.getElementById('view-auth').classList.remove('active');
            document.getElementById('main-nav').style.display = 'flex';
            document.getElementById('menu-user-name').innerText = usuario.name;
            document.getElementById('menu-user-handle').innerText = usuario.handle;
            
            generarQR();
            cambiarTab('chats');
            cargarVideos();
            setInterval(sincronizarMensajes, 2500);
        }

        function cambiarTab(tab) {
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            
            const viewTarget = document.getElementById(`view-${tab}`);
            const navTarget = document.getElementById(`nav-${tab}`);
            if(viewTarget) viewTarget.classList.add('active');
            if(navTarget) navTarget.classList.add('active');

            if(tab === 'chats') cargarListaChats();
        }

        function cargarVideos() {
            const feed = document.getElementById('tiktok-feed');
            feed.innerHTML = '';
            listaVideos.forEach(url => {
                const card = document.createElement('div');
                card.className = 'tiktok-card';
                if(url.endsWith('.mp4')) {
                    card.innerHTML = `<video src="${url}" controls loop playsinline></video>`;
                } else {
                    card.innerHTML = `<iframe src="${url}" allow="autoplay; encrypted-media" allowfullscreen></iframe>`;
                }
                feed.appendChild(card);
            });
        }

        function abrirChatCon(id, nombre) {
            chatActivo = id;
            document.getElementById('room-title').innerText = nombre;
            document.getElementById('chat-messages').innerHTML = '';
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.getElementById('view-room').classList.add('active');
            sincronizarMensajes();
        }

        function cerrarChat() {
            chatActivo = null;
            cambiarTab('chats');
        }

        async function enviarMensajeLocal() {
            const input = document.getElementById('message-input');
            const texto = input.value.trim();
            if(!texto || !chatActivo) return;

            renderBubble(texto, 'sent');
            input.value = '';

            try {
                const res = await fetch('/api/v1/enviar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        usuario_id: usuario.id,
                        destino_id: chatActivo,
                        mensaje: texto
                    })
                });
                const data = await res.json();
                
                if (data.respuesta_amiti) {
                    renderBubble(data.respuesta_amiti, 'amiti');
                }
            } catch(e) {
                renderBubble("⚠️ Error al conectar con S1", 'received');
            }
        }

        async function sincronizarMensajes() {
            if(!chatActivo || !supabaseClient) return;

            try {
                const { data } = await supabaseClient
                    .from('messages')
                    .select('*')
                    .or(`and(sender_id.eq.${usuario.id},receiver_id.eq.${chatActivo}),and(sender_id.eq.${chatActivo},receiver_id.eq.${usuario.id})`)
                    .order('created_at', { ascending: true });

                if(data) {
                    const contenedor = document.getElementById('chat-messages');
                    contenedor.innerHTML = '';
                    data.forEach(m => {
                        let clase = m.sender_id === usuario.id ? 'sent' : (m.sender_id === 'amiti_ia' ? 'amiti' : 'received');
                        renderBubble(m.content, clase);
                    });
                }
            } catch(e) {
                console.log(e);
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

        function cargarListaChats() {
            const list = document.getElementById('chats-list');
            list.innerHTML = `
                <div class="chat-item" onclick="abrirChatCon('amiti_ia', '🤖 Amiti IA (Centro de Mando S1)')">
                    <div>
                        <strong style="color:var(--amiti-purple);">🤖 Amiti IA - Centro de Mando</strong>
                        <div style="font-size:12px; color:var(--text-muted);">Servidor 1 Conectado</div>
                    </div>
                    <span class="badge-s1">S1</span>
                </div>
            `;
        }

        function generarQR() {
            new QRious({
                element: document.getElementById('qr-canvas'),
                value: usuario ? usuario.handle : '@usuario',
                size: 180,
                background: '#0f111a',
                foreground: '#10b981'
            });
        }

        function abrirModal(id) { document.getElementById(id).classList.add('active'); }
        function cerrarModal(id) { 
            document.getElementById(id).classList.remove('active');
            try { Html5Qrcode.stop(); } catch(e){}
        }

        function iniciarEscaner() {
            const html5QrCode = new Html5Qrcode("qr-reader");
            html5QrCode.start(
                { facingMode: "environment" },
                { fps: 10, qrbox: 220 },
                (decodedText) => {
                    html5QrCode.stop();
                    cerrarModal('modal-qr');
                    abrirChatCon(decodedText.replace('@','').toLowerCase(), decodedText);
                }
            ).catch(err => alert("Cámara no disponible: " + err));
        }
    </script>
</body>
</html>
"""

# ==========================================
# RUTA PRINCIPAL Y ARRANQUE
# ==========================================

@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        servidor_1_url=SERVIDOR_1_URL,
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY
    )

if __name__ == '__main__':
    print(f"🚀 Iniciando Servidor 2 con Videos en puerto {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=False)
