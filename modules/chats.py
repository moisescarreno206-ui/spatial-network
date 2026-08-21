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
            -webkit-text-stroke: 0.5px #000000;
            text-shadow: 1px 1px 0px #000000, -1px -1px 0px #000000, 1px -1px 0px #000000, -1px 1px 0px #000000;
        }
        
        body { background-color: #08090e; display: flex; flex-direction: column; height: 100dvh; height: 100vh; overflow: hidden; position: relative; }

        .view { display: none; flex-direction: column; height: 100%; width: 100%; position: absolute; top: 0; left: 0; background-color: #08090e; padding-right: 65px; }
        .view.active { display: flex; }

        /* CABECERA SUPERIOR SEGÚN BOCETO */
        .app-header { padding: 12px 14px; display: flex; align-items: center; justify-content: space-between; background-color: #0e1017; border-bottom: 1px solid rgba(255,255,255,0.08); }
        .app-title-box { display: flex; flex-direction: column; }
        .app-title { font-size: 17px; font-weight: 800; }
        .sub-title-tag { font-size: 9px; color: #a855f7; font-weight: 700; }
        
        /* GRUPO DE ICONOS SUPERIOR DERECHA (Cámara, Lupa, Opciones) */
        .top-right-group { display: flex; background: #151821; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 20px; padding: 4px 8px; gap: 8px; align-items: center; }
        .top-right-group span { font-size: 14px; cursor: pointer; -webkit-text-stroke: 0px; }

        /* BARRA DE BÚSQUEDA */
        .search-section { padding: 10px 14px; background-color: #08090e; }
        .search-bar { display: flex; align-items: center; background-color: #12151f; border: 1px solid #22c55e; border-radius: 18px; padding: 7px 12px; gap: 8px; }
        .search-bar input { background: transparent; border: none; outline: none; width: 100%; font-size: 13px; -webkit-text-stroke: 0.3px #000; }
        .search-bar input::placeholder { color: #a1a1aa; -webkit-text-stroke: 0px; }
        .search-bar span { color: #22c55e; font-size: 14px; -webkit-text-stroke: 0px; }

        /* CONTENIDO PRINCIPAL */
        .main-content { flex: 1; overflow-y: auto; padding: 12px 14px; display: flex; flex-direction: column; gap: 12px; }
        
        .welcome-chats-banner { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 16px; background: #12151f; border-radius: 14px; border: 1px solid rgba(168, 85, 247, 0.3); gap: 6px; }
        .welcome-chats-banner span { font-size: 26px; color: #a855f7; -webkit-text-stroke: 0px; }
        .welcome-chats-banner h2 { font-size: 14px; font-weight: 700; }

        /* TARJETAS DE CHAT Y CANAL */
        .canal-card { display: flex; align-items: center; background: #12151f; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 8px 12px; gap: 10px; cursor: pointer; }
        .canal-icon { width: 36px; height: 36px; background: #1e2230; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #3b82f6; font-size: 16px; -webkit-text-stroke: 0px; }
        .canal-info h4 { font-size: 13px; font-weight: 600; }
        .canal-info p { font-size: 11px; color: #cbd5e1; }

        /* FILA INFERIOR DE CÍRCULOS Y CANAL (DEL BOCETO) */
        .bottom-sketch-row { display: flex; flex-direction: column; gap: 10px; padding: 4px 0 10px 0; }
        .circles-row { display: flex; justify-content: space-around; align-items: center; background: #12151f; padding: 8px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.05); }
        .circle-item { width: 32px; height: 32px; border-radius: 50%; border: 1px solid #3b82f6; display: flex; align-items: center; justify-content: center; font-size: 12px; background: #181c2b; cursor: pointer; -webkit-text-stroke: 0px; }

        /* MENÚ LATERAL VERTICAL DERECHO (DEL BOCETO) */
        .vertical-sidebar { position: fixed; top: 0; right: 0; width: 65px; height: 100vh; background-color: #0e1017; border-left: 1px solid rgba(255,255,255,0.08); display: flex; flex-direction: column; justify-content: space-around; align-items: center; padding: 20px 0; z-index: 1000; }
        .v-menu-item { display: flex; flex-direction: column; align-items: center; gap: 4px; font-size: 9px; cursor: pointer; color: #94a3b8; transition: color 0.2s; font-weight: 600; }
        .v-menu-item.active { color: #3b82f6; }
        .v-menu-item span { font-size: 16px; -webkit-text-stroke: 0px; }

        /* SALA DE CHAT INDIVIDUAL */
        .chat-room-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; background-color: #0e1017; border-bottom: 1px solid rgba(255,255,255,0.08); }
        .chat-room-back { display: flex; align-items: center; gap: 8px; cursor: pointer; }
        .chat-room-back span { font-size: 18px; color: #3b82f6; -webkit-text-stroke: 0px; }
        .chat-room-name { font-size: 14px; font-weight: 600; }
        
        .messages-container { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; background-color: #08090e; }
        .bubble { max-width: 78%; padding: 9px 12px; border-radius: 10px; font-size: 13px; display: flex; flex-direction: column; gap: 3px; }
        .bubble.received { background-color: #12151f; align-self: flex-start; border-top-left-radius: 4px; }
        .bubble.sent { background: linear-gradient(135deg, #3b82f6, #1d4ed8); align-self: flex-end; border-top-right-radius: 4px; }
        .bubble-time { font-size: 9px; align-self: flex-end; color: rgba(255,255,255,0.8); -webkit-text-stroke: 0.3px #000; }

        .chat-input-bar { display: flex; align-items: center; padding: 10px 12px; background-color: #0e1017; border-top: 1px solid rgba(255,255,255,0.08); gap: 8px; }
        .chat-input-bar input { flex: 1; background: #12151f; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 18px; padding: 8px 12px; outline: none; font-size: 13px; -webkit-text-stroke: 0.3px #000; }
        .send-btn { width: 36px; height: 36px; background: #3b82f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 13px; -webkit-text-stroke: 0px; }

        .placeholder-view { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; text-align: center; padding: 20px; }
        .placeholder-view span { font-size: 28px; color: #3b82f6; -webkit-text-stroke: 0px; }
        
        #connection-status { font-size: 8px; padding: 1px 4px; border-radius: 3px; background: #ef4444; font-weight: 600; -webkit-text-stroke: 0px; }
        #connection-status.connected { background: #22c55e; }
    </style>
</head>
<body>

    <!-- VISTA 1: CHATS -->
    <div id="view-chats" class="view active">
        <div class="app-header">
            <div class="app-title-box">
                <div class="app-title">Spatial Network</div>
                <span id="connection-status">Desconectado</span>
            </div>
            <!-- Grupo superior derecho del boceto -->
            <div class="top-right-group">
                <span title="Cámara">📷</span>
                <span title="Buscar">🔍</span>
                <span title="Opciones">⋮</span>
            </div>
        </div>

        <div class="search-section">
            <div class="search-bar">
                <span>🔍</span>
                <input type="text" placeholder="Bucar chat...">
            </div>
        </div>

        <div class="main-content">
            <div class="welcome-chats-banner">
                <span>💬</span>
                <h2>Inicio de tus Chats</h2>
            </div>

            <div class="canal-card" onclick="openChat('Soporte General', 'user_system', 'online')">
                <div class="canal-icon">S</div>
                <div class="canal-info" style="flex: 1;">
                    <h4>Soporte General</h4>
                    <p id="last-msg-preview">Conectado al servidor WebSocket...</p>
                </div>
                <span style="font-size: 10px;" id="last-time">Ahora</span>
            </div>

            <!-- Fila de círculos y canal de tu boceto inferior -->
            <div class="bottom-sketch-row">
                <div class="circles-row">
                    <div class="circle-item">👤</div>
                    <div class="circle-item">🔹</div>
                    <div class="circle-item">👤</div>
                    <div class="circle-item">🔹</div>
                    <div class="circle-item">👤</div>
                </div>

                <div class="canal-card">
                    <div class="canal-icon" style="color: #22c55e;">📢</div>
                    <div class="canal-info" style="flex: 1;">
                        <h4>CANAL</h4>
                        <p>Canal oficial de la red</p>
                    </div>
                </div>
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
            <p>Estados en tiempo real</p>
        </div>
    </div>

    <!-- VISTA 3: COMUNIDADES / MAMÁ -->
    <div id="view-communities" class="view">
        <div class="app-header">
            <div class="app-title">Comunidades</div>
        </div>
        <div class="placeholder-view">
            <span>👥</span>
            <p>Grupos y comunidades</p>
        </div>
    </div>

    <!-- VISTA 4: LLAMADAS -->
    <div id="view-calls" class="view">
        <div class="app-header">
            <div class="app-title">Llamadas</div>
        </div>
        <div class="placeholder-view">
            <span>📞</span>
            <p>Historial de llamadas</p>
        </div>
    </div>

    <!-- VISTA 5: PERFIL -->
    <div id="view-profile" class="view">
        <div class="app-header">
            <div class="app-title">Perfil</div>
        </div>
        <div class="placeholder-view">
            <span>👤</span>
            <p>Configuración de cuenta</p>
        </div>
    </div>

    <!-- VISTA 6: SALA DE CHAT -->
    <div id="view-chat-room" class="view" style="padding-right: 0;">
        <div class="chat-room-header">
            <div class="chat-room-back" onclick="closeChat()">
                <span>←</span>
                <div class="canal-icon" id="room-avatar" style="width: 30px; height: 30px; font-size: 13px;">S</div>
                <div class="chat-room-name" id="room-name">Soporte General</div>
            </div>
            <div class="top-right-group">
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

    <!-- MENÚ LATERAL VERTICAL DERECHO (DEL BOCETO) -->
    <div class="vertical-sidebar">
        <div class="v-menu-item active" onclick="switchTab('chats', this)">
            <span>💬</span>Chats
        </div>
        <div class="v-menu-item" onclick="switchTab('novedades', this)">
            <span>⚡</span>Novedades
        </div>
        <div class="v-menu-item" onclick="switchTab('communities', this)">
            <span>👥</span>Grupos
        </div>
        <div class="v-menu-item" onclick="switchTab('calls', this)">
            <span>📞</span>Llamadas
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
  
