from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

chats_bp = APIRouter()


@chats_bp.get("/", response_class=HTMLResponse)
@chats_bp.get("/chats", response_class=HTMLResponse)
async def chats_view(request: Request):
  html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Spatial Network</title>
    <style>
        * { 
            box-sizing: border-box; 
            margin: 0; 
            padding: 0; 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            color: #ffffff;
        }
        
        body { background-color: #08090e; display: flex; flex-direction: column; height: 100dvh; height: 100vh; overflow: hidden; position: relative; }

        /* CONTENEDOR DE VISTAS (Dejando espacio a la derecha para el menú vertical del boceto) */
        .view { display: none; flex-direction: column; height: 100%; width: calc(100% - 75px); position: absolute; top: 0; left: 0; background-color: #08090e; padding-bottom: 20px; }
        .view.active { display: flex; }

        /* CABECERA SUPERIOR (Según boceto) */
        .app-header { padding: 12px 14px; display: flex; align-items: center; justify-content: space-between; background-color: #0e1017; border-bottom: 1px solid rgba(255,255,255,0.06); }
        .app-title-box { display: flex; flex-direction: column; gap: 2px; }
        .app-title { font-size: 16px; font-weight: 800; background: linear-gradient(135deg, #a855f7, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        
        #connection-status { font-size: 8px; padding: 1px 5px; border-radius: 3px; background: #ef4444; font-weight: 600; width: fit-content; text-transform: uppercase; }
        #connection-status.connected { background: #22c55e; }

        /* GRUPO DE ICONOS SUPERIOR DERECHA (Cápsula del boceto) */
        .top-pill-group { display: flex; background: #151821; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 20px; padding: 4px 8px; gap: 6px; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.4); }
        .top-pill-group span { font-size: 13px; cursor: pointer; }

        /* BARRA DE BÚSQUEDA */
        .search-section { padding: 10px 14px; background-color: #08090e; }
        .search-bar { display: flex; align-items: center; background-color: #12151f; border: 1px solid rgba(34, 197, 94, 0.4); border-radius: 16px; padding: 8px 12px; gap: 8px; }
        .search-bar input { background: transparent; border: none; outline: none; width: 100%; font-size: 13px; color: #fff; }
        .search-bar input::placeholder { color: #64748b; }
        .search-bar span { color: #22c55e; font-size: 14px; }

        /* CONTENIDO PRINCIPAL */
        .main-content { flex: 1; overflow-y: auto; padding: 10px 14px; display: flex; flex-direction: column; gap: 12px; }
        
        .welcome-chats-banner { display: flex; align-items: center; gap: 10px; padding: 12px 14px; background: #12151f; border-radius: 12px; border: 1px solid rgba(168, 85, 247, 0.25); }
        .welcome-chats-banner span { font-size: 22px; color: #a855f7; }
        .welcome-chats-banner h2 { font-size: 14px; font-weight: 700; color: #f8fafc; }

        /* TARJETAS DE CHAT */
        .chat-card { display: flex; align-items: center; background: #12151f; border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 12px; padding: 10px 12px; gap: 10px; cursor: pointer; }
        .chat-avatar { width: 38px; height: 38px; background: linear-gradient(135deg, #3b82f6, #1d4ed8); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; color: #fff; flex-shrink: 0; }
        .chat-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
        .chat-row { display: flex; justify-content: space-between; align-items: baseline; }
        .chat-name { font-size: 14px; font-weight: 600; color: #f1f5f9; }
        .chat-time { font-size: 10px; color: #64748b; }
        .chat-preview { font-size: 12px; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

        /* BOTÓN FLOTANTE (+) */
        .fab-card { background: #12151f; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 12px; display: flex; align-items: center; justify-content: center; gap: 8px; cursor: pointer; margin-top: auto; }
        .fab-card span { font-size: 16px; color: #3b82f6; font-weight: bold; }

        /* MENÚ VERTICAL LATERAL DERECHO (EXACTO AL BOCETO) */
        .vertical-sidebar { position: fixed; top: 0; right: 0; width: 75px; height: 100vh; background-color: #0e1017; border-left: 1px solid rgba(255,255,255,0.08); display: flex; flex-direction: column; justify-content: space-evenly; align-items: center; padding: 15px 0; z-index: 1000; box-shadow: -4px 0 15px rgba(0,0,0,0.5); }
        .v-menu-item { display: flex; flex-direction: column; align-items: center; gap: 3px; font-size: 10px; cursor: pointer; color: #64748b; transition: all 0.2s; font-weight: 600; padding: 8px 4px; border-radius: 8px; width: 60px; text-align: center; }
        .v-menu-item.active { color: #3b82f6; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); }
        .v-menu-item span { font-size: 18px; }

        /* SALA DE CHAT INDIVIDUAL */
        #view-chat-room { width: 100%; padding-right: 0; }
        .chat-room-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; background-color: #0e1017; border-bottom: 1px solid rgba(255,255,255,0.06); }
        .room-back-btn { display: flex; align-items: center; gap: 8px; cursor: pointer; }
        .room-back-btn span { font-size: 18px; color: #3b82f6; }
        .room-title { font-size: 14px; font-weight: 600; color: #fff; }
        
        .messages-container { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; background-color: #08090e; }
        .bubble { max-width: 80%; padding: 9px 12px; border-radius: 10px; font-size: 13px; display: flex; flex-direction: column; gap: 3px; }
        .bubble.received { background-color: #12151f; align-self: flex-start; border-top-left-radius: 4px; color: #e2e8f0; }
        .bubble.sent { background: linear-gradient(135deg, #3b82f6, #1d4ed8); align-self: flex-end; border-top-right-radius: 4px; color: #fff; }
        .bubble-time { font-size: 9px; align-self: flex-end; color: rgba(255,255,255,0.7); }

        .chat-input-bar { display: flex; align-items: center; padding: 10px 12px; background-color: #0e1017; border-top: 1px solid rgba(255,255,255,0.06); gap: 8px; }
        .chat-input-bar input { flex: 1; background: #12151f; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 18px; padding: 8px 12px; outline: none; font-size: 13px; color: #fff; }
        .send-btn { width: 36px; height: 36px; background: #3b82f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 14px; }

        .placeholder-view { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; text-align: center; padding: 20px; color: #64748b; }
        .placeholder-view span { font-size: 32px; color: #3b82f6; }
        .placeholder-view p { font-size: 13px; color: #94a3b8; }
    </style>
</head>
<body>

    <!-- VISTA 1: CHATS -->
    <div id="view-chats" class="view active">
        <div class="app-header">
            <div class="app-title-box">
                <div class="app-title">Spatial Network</div>
                <span id="connection-status">...</span>
            </div>
            <!-- Grupo superior derecho exacto al boceto -->
            <div class="top-pill-group">
                <span title="Cámara">📷</span>
                <span title="Buscar">🔍</span>
                <span title="Opciones">⋮</span>
            </div>
        </div>

        <div class="search-section">
            <div class="search-bar">
                <span>🔍</span>
                <input type="text" placeholder="Buscar chat o canal...">
            </div>
        </div>

        <div class="main-content">
            <div class="welcome-chats-banner">
                <span>💬</span>
                <div>
                    <h2>Inicio de tus Chats</h2>
                    <p style="font-size: 11px; color: #94a3b8;">Conversaciones en tiempo real</p>
                </div>
            </div>

            <!-- SOPORTE GENERAL -->
            <div class="chat-card" onclick="openChat('Soporte General', 'user_system', 'online')">
                <div class="chat-avatar">S</div>
                <div class="chat-info">
                    <div class="chat-row">
                        <span class="chat-name">Soporte General</span>
                        <span class="chat-time" id="last-time">Ahora</span>
                    </div>
                    <div class="chat-preview" id="last-msg-preview">Conectado al servidor WebSocket...</div>
                </div>
            </div>

            <!-- CANAL OFICIAL -->
            <div class="chat-card">
                <div class="chat-avatar" style="background: linear-gradient(135deg, #22c55e, #15803d);">📢</div>
                <div class="chat-info">
                    <div class="chat-row">
                        <span class="chat-name">Canal Oficial</span>
                        <span class="chat-time">Ayer</span>
                    </div>
                    <div class="chat-preview">Actualizaciones de la red espacial</div>
                </div>
            </div>

            <div class="fab-card" onclick="alert('Crear nuevo chat o canal')">
                <span>➕</span> <span style="font-size: 13px; font-weight: 600; color: #3b82f6;">Crear Nuevo</span>
            </div>
        </div>
    </div>

    <!-- VISTA 2: NOVEDADES -->
    <div id="view-novedades" class="view">
        <div class="app-header">
            <div class="app-title">Novedades</div>
        </div>
        <div class="placeholder-view">
            <span>⚡</span>
            <p>Estados e historias en tiempo real</p>
        </div>
    </div>

    <!-- VISTA 3: MAMÁ / GRUPOS -->
    <div id="view-mama" class="view">
        <div class="app-header">
            <div class="app-title">Mamá</div>
        </div>
        <div class="placeholder-view">
            <span>💬</span>
            <p>Chat personal y conexiones especiales</p>
        </div>
    </div>

    <!-- VISTA 4: PERFIL -->
    <div id="view-profile" class="view">
        <div class="app-header">
            <div class="app-title">Perfil</div>
        </div>
        <div class="placeholder-view">
            <span>👤</span>
            <p>Configuración de tu cuenta</p>
        </div>
    </div>

    <!-- VISTA 5: SALA DE CHAT -->
    <div id="view-chat-room" class="view">
        <div class="chat-room-header">
            <div class="room-back-btn" onclick="closeChat()">
                <span>←</span>
                <div class="chat-avatar" id="room-avatar" style="width: 32px; height: 32px; font-size: 12px;">S</div>
                <div class="room-title" id="room-name">Soporte General</div>
            </div>
            <div class="top-pill-group">
                <span>📹</span>
                <span>📞</span>
            </div>
        </div>

        <div class="messages-container" id="messages-list"></div>

        <div class="chat-input-bar">
            <input type="text" id="message-input" placeholder="Escribe un mensaje..." onkeypress="handleKey(event)">
            <div class="send-btn" onclick="sendMessage()">➤</div>
        </div>
    </div>

    <!-- MENÚ VERTICAL LATERAL DERECHO (EXACTO AL BOCETO) -->
    <div class="vertical-sidebar">
        <div class="v-menu-item active" onclick="switchTab('chats', this)">
            <span>💬</span>chats
        </div>
        <div class="v-menu-item" onclick="switchTab('novedades', this)">
            <span>⚡</span>Novedades
        </div>
        <div class="v-menu-item" onclick="switchTab('mama', this)">
            <span>💖</span>Mamá
        </div>
        <div class="v-menu-item" onclick="switchTab('profile', this)">
            <span>👤</span>Perfil
        </div>
    </div>

    <script>
        let ws;
        let currentRecipientId = 'user_system';
        const userId = localStorage.getItem('spatial_user_id') || 'user_' + Math.floor(Math.random() * 90000 + 10000);
        localStorage.setItem('spatial_user_id', userId);

        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/chat?user_id=${userId}&token=active_session`;
            
            ws = new WebSocket(wsUrl);

            ws.onopen = function() {
                const status = document.getElementById('connection-status');
                if(status) {
                    status.innerText = "Online";
                    status.classList.add('connected');
                }
            };

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'new_message') {
                    appendMessage(data.content, 'received', data.timestamp || 'Ahora');
                    updatePreview(data.content);
                }
            };

            ws.onclose = function() {
                const status = document.getElementById('connection-status');
                if(status) {
                    status.innerText = "Offline";
                    status.classList.remove('connected');
                }
                setTimeout(initWebSocket, 3000);
            };
        }

        initWebSocket();

        function switchTab(tabName, element) {
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.v-menu-item').forEach(m => m.classList.remove('active'));

            const target = document.getElementById(`view-${tabName}`);
            if (target) target.classList.add('active');
            if (element) element.classList.add('active');
        }

        function openChat(name, recipientId, status) {
            currentRecipientId = recipientId;
            document.getElementById('room-name').innerText = name;
            document.getElementById('room-avatar').innerText = name.charAt(0);
            
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.getElementById('view-chat-room').classList.add('active');
        }

        function closeChat() {
            document.getElementById('view-chat-room').classList.remove('active');
            document.getElementById('view-chats').classList.add('active');
        }

        function handleKey(e) {
            if (e.key === 'Enter') sendMessage();
        }

        function sendMessage() {
            const input = document.getElementById('message-input');
            const text = input.value.trim();
            if (!text) return;

            const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const messageId = 'msg_' + Date.now();

            const payload = {
                type: "send_message",
                recipient_id: currentRecipientId,
                message_id: messageId,
                content: text,
                timestamp: timeStr
            };

            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify(payload));
                appendMessage(text, 'sent', timeStr + ' ✓');
                updatePreview(text);
                input.value = '';
            }
        }

        function appendMessage(text, type, timeStr) {
            const container = document.getElementById('messages-list');
            const bubble = document.createElement('div');
            bubble.className = `bubble ${type}`;
            bubble.innerHTML = `${text} <span class="bubble-time">${timeStr}</span>`;
            container.appendChild(bubble);
            container.scrollTop = container.scrollHeight;
        }

        function updatePreview(text) {
            const preview = document.getElementById('last-msg-preview');
            const time = document.getElementById('last-time');
            if(preview) preview.innerText = text;
            if(time) time.innerText = 'Ahora';
        }
    </script>
</body>
</html>
"""
  return HTMLResponse(content=html_content)
  
