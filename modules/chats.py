from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

chats_bp = APIRouter()


@chats_bp.get("/chats", response_class=HTMLResponse)
async def chats_view(request: Request):
  html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Spatial Network - Chats</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        
        /* Usar 100dvh para evitar que la barra móvil recorte el contenido */
        body { background-color: #0d0f18; color: #fff; display: flex; flex-direction: column; height: 100dvh; height: 100vh; overflow: hidden; position: relative; }

        .view { display: none; flex-direction: column; height: 100%; width: 100%; position: absolute; top: 0; left: 0; background-color: #0d0f18; padding-bottom: 65px; }
        .view.active { display: flex; }

        .header-list { padding: 16px 20px 10px 20px; display: flex; align-items: center; justify-content: space-between; background-color: #0d0f18; }
        .header-title { font-size: 20px; font-weight: 800; background: linear-gradient(90deg, #c084fc, #e879f9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 0.5px; }
        .header-icons { display: flex; gap: 20px; color: #94a3b8; font-size: 18px; cursor: pointer; }

        .search-container { padding: 0 16px 12px 16px; background-color: #0d0f18; }
        .search-box { display: flex; align-items: center; background-color: #16192b; border: 1px solid #232742; border-radius: 24px; padding: 10px 16px; gap: 12px; }
        .search-box input { background: transparent; border: none; outline: none; color: #fff; font-size: 14px; width: 100%; }
        .search-box input::placeholder { color: #64748b; }
        .search-box span { color: #64748b; }

        .chats-list { flex: 1; overflow-y: auto; width: 100%; }
        .chat-item { display: flex; align-items: center; padding: 12px 20px; gap: 14px; cursor: pointer; transition: background 0.2s; }
        .chat-item:hover { background-color: rgba(192, 132, 252, 0.05); }

        .avatar-wrapper { position: relative; width: 50px; height: 50px; flex-shrink: 0; }
        .avatar { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; background-color: #232742; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #c084fc; font-size: 18px; }
        .avatar-wrapper.online::after { content: ''; position: absolute; bottom: 2px; right: 2px; width: 12px; height: 12px; background-color: #22c55e; border: 2px solid #0d0f18; border-radius: 50%; }

        .chat-info { flex: 1; min-width: 0; border-bottom: 1px solid rgba(35, 39, 66, 0.4); padding-bottom: 12px; }
        .chat-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
        .chat-name { font-size: 15px; font-weight: 600; color: #fff; }
        .chat-time { font-size: 11px; color: #64748b; }
        .chat-preview { font-size: 13px; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

        .fab { position: fixed; bottom: 80px; right: 20px; width: 52px; height: 52px; background: linear-gradient(135deg, #8b5cf6, #a855f7); border-radius: 16px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 20px; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4); cursor: pointer; z-index: 100; }

        /* BARRA DE NAVEGACIÓN INFERIOR ESTILO WHATSAPP */
        .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; height: 60px; background-color: #121526; border-top: 1px solid #232742; display: flex; justify-content: space-around; align-items: center; z-index: 1000; }
        .nav-item { display: flex; flex-direction: column; align-items: center; gap: 3px; color: #64748b; font-size: 11px; cursor: pointer; text-decoration: none; flex: 1; }
        .nav-item.active { color: #c084fc; font-weight: 600; }
        .nav-item span { font-size: 18px; }

        .chat-room-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background-color: #16192b; border-bottom: 1px solid #232742; }
        .chat-room-user { display: flex; align-items: center; gap: 12px; cursor: pointer; }
        .chat-room-user .avatar { width: 38px; height: 38px; border-radius: 50%; font-size: 14px; }
        .chat-room-name { font-size: 15px; font-weight: 600; }
        .chat-room-status { font-size: 11px; color: #22c55e; }
        .chat-room-actions { display: flex; gap: 20px; color: #c084fc; font-size: 18px; }

        .messages-container { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; background-color: #0d0f18; }
        
        .message-bubble { max-width: 75%; padding: 10px 14px; border-radius: 14px; font-size: 14px; line-height: 1.4; display: flex; flex-direction: column; gap: 4px; }
        .message-bubble.received { background-color: #16192b; align-self: flex-start; border-top-left-radius: 4px; color: #cbd5e1; }
        .message-bubble.sent { background: linear-gradient(135deg, #8b5cf6, #a855f7); align-self: flex-end; border-top-right-radius: 4px; color: #fff; }
        
        .message-time { font-size: 10px; align-self: flex-end; color: rgba(255,255,255,0.7); margin-top: 2px; }

        .chat-input-bar { display: flex; align-items: center; padding: 10px 12px; background-color: #16192b; border-top: 1px solid #232742; gap: 8px; }
        .input-pill { flex: 1; display: flex; align-items: center; background-color: #0d0f18; border: 1px solid #232742; border-radius: 24px; padding: 8px 14px; gap: 10px; }
        .input-pill input { flex: 1; background: transparent; border: none; outline: none; color: #fff; font-size: 14px; }
        .input-pill input::placeholder { color: #64748b; }
        .input-pill span { color: #94a3b8; font-size: 18px; cursor: pointer; }
        
        .mic-fab { width: 42px; height: 42px; background: #8b5cf6; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 16px; cursor: pointer; flex-shrink: 0; }

        .placeholder-content { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #64748b; gap: 12px; }
        .placeholder-content span { font-size: 36px; }
        .placeholder-content p { font-size: 15px; font-weight: 500; color: #94a3b8; }
        
        #connection-status { font-size: 10px; padding: 2px 6px; border-radius: 4px; background: #ef4444; color: #fff; margin-left: 8px; }
        #connection-status.connected { background: #22c55e; }
    </style>
</head>
<body>

    <!-- VISTA 1: LISTA DE CHATS -->
    <div id="view-chats" class="view active">
        <div class="header-list">
            <div class="header-title">SPATIAL NETWORK <span id="connection-status">...</span></div>
            <div class="header-icons">
                <span>📷</span>
                <span>⋮</span>
            </div>
        </div>

        <div class="search-container">
            <div class="search-box">
                <span>🔍</span>
                <input type="text" placeholder="Busca un chat o inicia uno...">
            </div>
        </div>

        <div class="chats-list" id="active-chats-list">
            <div class="chat-item" onclick="openChat('Soporte General', 'user_system', 'online')">
                <div class="avatar-wrapper online">
                    <div class="avatar">S</div>
                </div>
                <div class="chat-info">
                    <div class="chat-header-row">
                        <span class="chat-name">Soporte General</span>
                        <span class="chat-time" id="last-time">Ahora</span>
                    </div>
                    <div class="chat-preview" id="last-msg-preview">Conectado al servidor WebSocket...</div>
                </div>
            </div>
        </div>

        <div class="fab">💬</div>
    </div>

    <!-- VISTA 2: NOVEDADES -->
    <div id="view-novedades" class="view">
        <div class="header-list">
            <div class="header-title">Novedades</div>
        </div>
        <div class="placeholder-content">
            <span>⚡</span>
            <p>Estados e historias en tiempo real</p>
        </div>
    </div>

    <!-- VISTA 3: COMUNIDADES -->
    <div id="view-communities" class="view">
        <div class="header-list">
            <div class="header-title">Comunidades</div>
        </div>
        <div class="placeholder-content">
            <span>👥</span>
            <p>Grupos y comunidades espaciales</p>
        </div>
    </div>

    <!-- VISTA 4: LLAMADAS -->
    <div id="view-calls" class="view">
        <div class="header-list">
            <div class="header-title">Llamadas</div>
        </div>
        <div class="placeholder-content">
            <span>📞</span>
            <p>Historial de llamadas de voz y video</p>
        </div>
    </div>

    <!-- VISTA 5: SALA DE CHAT INDIVIDUAL -->
    <div id="view-chat-room" class="view">
        <div class="chat-room-header">
            <div class="chat-room-user" onclick="closeChat()">
                <span style="font-size: 20px; margin-right: 4px;">←</span>
                <div class="avatar" id="room-avatar">S</div>
                <div>
                    <div class="chat-room-name" id="room-name">Soporte General</div>
                    <div class="chat-room-status" id="room-status">en línea</div>
                </div>
            </div>
            <div class="chat-room-actions">
                <span>📹</span>
                <span>📞</span>
                <span>⋮</span>
            </div>
        </div>

        <div class="messages-container" id="messages-list"></div>

        <div class="chat-input-bar">
            <div class="input-pill">
                <span>😊</span>
                <input type="text" id="message-input" placeholder="Escribe un mensaje..." onkeypress="handleKey(event)">
                <span>📎</span>
                <span>📷</span>
            </div>
            <div class="mic-fab" onclick="sendMessage()">➤</div>
        </div>
    </div>

    <!-- BARRA DE NAVEGACIÓN INFERIOR FIJA -->
    <div class="bottom-nav">
        <div class="nav-item active" onclick="switchTab('chats', this)">
            <span>💬</span>
            Chats
        </div>
        <div class="nav-item" onclick="switchTab('novedades', this)">
            <span>⚡</span>
            Novedades
        </div>
        <div class="nav-item" onclick="switchTab('communities', this)">
            <span>👥</span>
            Comunidades
        </div>
        <div class="nav-item" onclick="switchTab('calls', this)">
            <span>📞</span>
            Llamadas
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
                const statusBadge = document.getElementById('connection-status');
                if(statusBadge) {
                    statusBadge.innerText = "En línea";
                    statusBadge.classList.add('connected');
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
                const statusBadge = document.getElementById('connection-status');
                if(statusBadge) {
                    statusBadge.innerText = "Offline";
                    statusBadge.classList.remove('connected');
                }
                setTimeout(initWebSocket, 3000);
            };
        }

        initWebSocket();

        function switchTab(tabName, element) {
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

            const targetView = document.getElementById(`view-${tabName}`);
            if (targetView) targetView.classList.add('active');
            if (element) element.classList.add('active');
        }

        function openChat(name, recipientId, status) {
            currentRecipientId = recipientId;
            document.getElementById('room-name').innerText = name;
            document.getElementById('room-avatar').innerText = name.charAt(0);
            document.getElementById('room-status').innerText = status === 'online' ? 'en línea' : 'desconectado';
            
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
            bubble.className = `message-bubble ${type}`;
            bubble.innerHTML = `${text} <span class="message-time">${timeStr}</span>`;
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
  
