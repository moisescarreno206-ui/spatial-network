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

        /* VISTAS PRINCIPALES */
        .view { display: none; flex-direction: column; height: 100%; width: 100%; position: absolute; top: 0; left: 0; background-color: #08090e; padding-bottom: 65px; }
        .view.active { display: flex; }

        /* CABECERA SUPERIOR */
        .app-header { padding: 14px 16px; display: flex; align-items: center; justify-content: space-between; background-color: #0e1017; border-bottom: 1px solid rgba(255,255,255,0.06); position: relative; }
        .app-title-box { display: flex; align-items: center; gap: 10px; }
        .app-title { font-size: 20px; font-weight: 800; background: linear-gradient(135deg, #a855f7, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        
        #connection-status { font-size: 9px; padding: 2px 6px; border-radius: 4px; background: #ef4444; font-weight: 600; text-transform: uppercase; }
        #connection-status.connected { background: #22c55e; }

        .header-icons { display: flex; gap: 14px; align-items: center; }
        .icon-btn { font-size: 18px; cursor: pointer; color: #cbd5e1; }

        /* MENÚ DESPLEGABLE DE TRES PUNTOS (POPUP) */
        .dropdown-menu { display: none; position: absolute; top: 55px; right: 12px; background: #151821; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; width: 180px; box-shadow: 0 8px 24px rgba(0,0,0,0.6); z-index: 2000; overflow: hidden; }
        .dropdown-menu.show { display: flex; flex-direction: column; }
        .dropdown-item { padding: 12px 16px; font-size: 14px; color: #f1f5f9; display: flex; align-items: center; gap: 10px; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.04); }
        .dropdown-item:active { background: rgba(59, 130, 246, 0.2); }

        /* FILTROS TIPO WHATSAPP (Todos, No leídos, Favoritos, Grupos) */
        .filters-scroll { display: flex; gap: 8px; padding: 10px 16px; background-color: #08090e; overflow-x: auto; white-space: nowrap; scrollbar-width: none; }
        .filters-scroll::-webkit-scrollbar { display: none; }
        .filter-pill { padding: 6px 14px; background: #12151f; border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; font-size: 13px; font-weight: 500; color: #94a3b8; cursor: pointer; flex-shrink: 0; }
        .filter-pill.active { background: rgba(59, 130, 246, 0.2); border-color: #3b82f6; color: #fff; font-weight: 600; }

        /* BARRA DE BÚSQUEDA */
        .search-section { padding: 4px 16px 10px 16px; background-color: #08090e; }
        .search-bar { display: flex; align-items: center; background-color: #12151f; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 20px; padding: 9px 14px; gap: 10px; }
        .search-bar input { background: transparent; border: none; outline: none; width: 100%; font-size: 14px; color: #fff; }
        .search-bar input::placeholder { color: #64748b; }
        .search-bar span { color: #3b82f6; font-size: 15px; }

        /* CONTENIDO PRINCIPAL */
        .main-content { flex: 1; overflow-y: auto; padding: 0 16px 16px 16px; display: flex; flex-direction: column; gap: 10px; }
        
        .archived-box { display: flex; align-items: center; gap: 14px; padding: 10px 14px; color: #94a3b8; font-size: 14px; cursor: pointer; }
        .archived-box span { font-size: 16px; color: #3b82f6; }

        /* TARJETAS DE CHAT */
        .chat-card { display: flex; align-items: center; background: #12151f; border: 1px solid rgba(59, 130, 246, 0.15); border-radius: 14px; padding: 10px 12px; gap: 12px; cursor: pointer; transition: background 0.2s; }
        .chat-card:active { background: #1a1e2e; }
        
        .chat-avatar { width: 48px; height: 48px; background: linear-gradient(135deg, #3b82f6, #1d4ed8); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 18px; color: #fff; flex-shrink: 0; }
        .chat-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px; }
        .chat-row { display: flex; justify-content: space-between; align-items: baseline; }
        .chat-name { font-size: 15px; font-weight: 600; color: #f1f5f9; }
        .chat-time { font-size: 11px; color: #64748b; }
        .chat-preview { font-size: 13px; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

        /* BOTÓN FLOTANTE ESTILO WHATSAPP */
        .fab-whatsapp { position: fixed; bottom: 75px; right: 20px; background: linear-gradient(135deg, #3b82f6, #2563eb); color: #fff; width: 52px; height: 52px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 22px; cursor: pointer; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); z-index: 99; }

        /* BARRA DE NAVEGACIÓN INFERIOR (4 PESTAÑAS EXACTAS) */
        .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; height: 60px; background-color: #0e1017; border-top: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-around; align-items: center; z-index: 1000; }
        .nav-item { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; font-size: 11px; cursor: pointer; flex: 1; height: 100%; color: #64748b; transition: color 0.2s; font-weight: 500; }
        .nav-item.active { color: #3b82f6; font-weight: 600; }
        .nav-item span { font-size: 18px; }

        /* SECCIONES SECUNDARIAS (Novedades, Comunidades, Llamadas) */
        .section-header-title { font-size: 16px; font-weight: 700; color: #f8fafc; margin-bottom: 10px; }
        
        /* PANTALLA DE PERFIL (Accesible desde los tres puntos) */
        #view-profile { background-color: #08090e; }
        .profile-header-banner { display: flex; flex-direction: column; align-items: center; padding: 24px 16px; background: #0e1017; border-bottom: 1px solid rgba(255,255,255,0.06); gap: 12px; }
        .profile-big-avatar { width: 90px; height: 90px; border-radius: 50%; background: linear-gradient(135deg, #a855f7, #3b82f6); display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: bold; border: 2px solid rgba(59,130,246,0.5); }
        .profile-name { font-size: 18px; font-weight: 700; color: #fff; }
        .profile-username { font-size: 13px; color: #94a3b8; }
        
        .profile-options-list { display: flex; flex-direction: column; }
        .profile-option-item { display: flex; align-items: center; gap: 14px; padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); cursor: pointer; }
        .profile-option-item:active { background: rgba(59, 130, 246, 0.1); }
        .profile-option-item span { font-size: 18px; color: #3b82f6; }
        .profile-option-text h4 { font-size: 14px; font-weight: 600; color: #f1f5f9; }
        .profile-option-text p { font-size: 12px; color: #94a3b8; }

        /* SALA DE CHAT INDIVIDUAL */
        #view-chat-room { display: none; flex-direction: column; height: 100%; width: 100%; position: absolute; top: 0; left: 0; background-color: #08090e; z-index: 1500; }
        #view-chat-room.active { display: flex; }
        .chat-room-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background-color: #0e1017; border-bottom: 1px solid rgba(255,255,255,0.06); }
        .room-back-btn { display: flex; align-items: center; gap: 10px; cursor: pointer; }
        .room-back-btn span { font-size: 20px; color: #3b82f6; }
        .room-title { font-size: 15px; font-weight: 600; color: #fff; }
        
        .messages-container { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 10px; background-color: #08090e; }
        .bubble { max-width: 78%; padding: 10px 14px; border-radius: 12px; font-size: 14px; display: flex; flex-direction: column; gap: 3px; }
        .bubble.received { background-color: #12151f; align-self: flex-start; border-top-left-radius: 4px; color: #e2e8f0; }
        .bubble.sent { background: linear-gradient(135deg, #3b82f6, #1d4ed8); align-self: flex-end; border-top-right-radius: 4px; color: #fff; }
        .bubble-time { font-size: 10px; align-self: flex-end; color: rgba(255,255,255,0.7); }

        .chat-input-bar { display: flex; align-items: center; padding: 10px 12px; background-color: #0e1017; border-top: 1px solid rgba(255,255,255,0.06); gap: 8px; }
        .chat-input-bar input { flex: 1; background: #12151f; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 20px; padding: 9px 14px; outline: none; font-size: 14px; color: #fff; }
        .send-btn { width: 40px; height: 40px; background: #3b82f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 15px; }
    </style>
</head>
<body onclick="closeDropdowns(event)">

    <!-- VISTA 1: CHATS -->
    <div id="view-chats" class="view active">
        <div class="app-header">
            <div class="app-title-box">
                <div class="app-title">Spatial Network</div>
                <span id="connection-status">...</span>
            </div>
            <div class="header-icons">
                <span class="icon-btn" title="Cámara">📷</span>
                <span class="icon-btn" title="Opciones" onclick="toggleMenu(event)">⋮</span>
            </div>
            <!-- Menú desplegable con Perfil -->
            <div id="app-dropdown" class="dropdown-menu">
                <div class="dropdown-item" onclick="openProfileView()"><span>👤</span> Mi Perfil</div>
                <div class="dropdown-item" onclick="alert('Nuevo grupo')"><span>👥</span> Nuevo grupo</div>
                <div class="dropdown-item" onclick="alert('Ajustes generales')"><span>⚙️</span> Ajustes</div>
            </div>
        </div>

        <!-- Filtros estilo WhatsApp -->
        <div class="filters-scroll">
            <div class="filter-pill active">Todos</div>
            <div class="filter-pill">No leídos</div>
            <div class="filter-pill">Favoritos</div>
            <div class="filter-pill">Grupos</div>
        </div>

        <div class="search-section">
            <div class="search-bar">
                <span>🔍</span>
                <input type="text" placeholder="Buscar chat o canal...">
            </div>
        </div>

        <div class="main-content">
            <div class="archived-box">
                <span>📁</span>
                <div>Archivados</div>
            </div>

            <!-- SOPORTE GENERAL -->
            <div class="chat-card" onclick="openChat('Soporte General', 'user_system')">
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
            <div class="chat-card" onclick="openChat('Canal Oficial', 'channel_official')">
                <div class="chat-avatar" style="background: linear-gradient(135deg, #22c55e, #15803d);">📢</div>
                <div class="chat-info">
                    <div class="chat-row">
                        <span class="chat-name">Canal Oficial</span>
                        <span class="chat-time">Ayer</span>
                    </div>
                    <div class="chat-preview">Actualizaciones de la red espacial</div>
                </div>
            </div>
        </div>

        <div class="fab-whatsapp" onclick="alert('Crear nuevo chat')">
            <span>💬</span>
        </div>
    </div>

    <!-- VISTA 2: NOVEDADES -->
    <div id="view-novedades" class="view">
        <div class="app-header">
            <div class="app-title">Novedades</div>
            <div class="header-icons">
                <span class="icon-btn">🔍</span>
                <span class="icon-btn" onclick="toggleMenu(event)">⋮</span>
            </div>
        </div>
        <div class="main-content" style="padding-top: 16px;">
            <div class="section-header-title">Estados</div>
            <div class="chat-card">
                <div class="chat-avatar" style="border: 2px solid #22c55e;">+</div>
                <div class="chat-info">
                    <span class="chat-name">Mi estado</span>
                    <span class="chat-preview">Añade una actualización</span>
                </div>
            </div>
        </div>
    </div>

    <!-- VISTA 3: COMUNIDADES -->
    <div id="view-communities" class="view">
        <div class="app-header">
            <div class="app-title">Comunidades</div>
            <div class="header-icons">
                <span class="icon-btn" onclick="toggleMenu(event)">⋮</span>
            </div>
        </div>
        <div class="main-content" style="align-items: center; justify-content: center; text-align: center; gap: 16px;">
            <div style="font-size: 50px; color: #3b82f6;">👥</div>
            <h3 style="font-size: 18px; font-weight: 700;">Usa una comunidad para mantenerte en contacto</h3>
            <p style="font-size: 13px; color: #94a3b8; max-width: 280px;">Las comunidades reúnen a los miembros en grupos por temas y facilitan avisos.</p>
            <div style="background: #3b82f6; color: white; padding: 10px 20px; border-radius: 20px; font-weight: 600; font-size: 14px; cursor: pointer;" onclick="alert('Crear comunidad')">Iniciar tu comunidad</div>
        </div>
    </div>

    <!-- VISTA 4: LLAMADAS -->
    <div id="view-calls" class="view">
        <div class="app-header">
            <div class="app-title">Llamadas</div>
            <div class="header-icons">
                <span class="icon-btn">🔍</span>
                <span class="icon-btn" onclick="toggleMenu(event)">⋮</span>
            </div>
        </div>
        <div class="main-content" style="padding-top: 16px;">
            <div class="section-header-title">Favoritos</div>
            <div class="chat-card" style="margin-bottom: 10px;">
                <div class="chat-avatar" style="background: #1e293b;">❤️</div>
                <div class="chat-info">
                    <span class="chat-name">Crear enlace de llamada</span>
                    <span class="chat-preview">Comparte un enlace para tu llamada</span>
                </div>
            </div>
            <div class="section-header-title">Recientes</div>
        </div>
    </div>

    <!-- VISTA DE PERFIL (Abierta desde los tres puntos) -->
    <div id="view-profile" class="view">
        <div class="app-header">
            <div class="room-back-btn" onclick="closeProfileView()">
                <span>←</span>
                <div class="room-title">Perfil</div>
            </div>
        </div>
        <div class="profile-header-banner">
            <div class="profile-big-avatar">M</div>
            <div class="profile-name">Moisés Carreño</div>
            <div class="profile-username">@Jack12747</div>
        </div>
        <div class="profile-options-list">
            <div class="profile-option-item" onclick="alert('Editar nombre o información')">
                <span>✏️</span>
                <div class="profile-option-text">
                    <h4>Nombre y Estado</h4>
                    <p>Moisés Carreño</p>
                </div>
            </div>
            <div class="profile-option-item" onclick="alert('Dispositivos vinculados')">
                <span>💻</span>
                <div class="profile-option-text">
                    <h4>Dispositivos vinculados</h4>
                    <p>Gestiona tus sesiones activas</p>
                </div>
            </div>
            <div class="profile-option-item" onclick="alert('Privacidad y seguridad')">
                <span>🔒</span>
                <div class="profile-option-text">
                    <h4>Privacidad</h4>
                    <p>Bloqueos y mensajes temporales</p>
                </div>
            </div>
        </div>
    </div>

    <!-- SALA DE CHAT INDIVIDUAL -->
    <div id="view-chat-room">
        <div class="chat-room-header">
            <div class="room-back-btn" onclick="closeChat()">
                <span>←</span>
                <div class="chat-avatar" id="room-avatar" style="width: 34px; height: 34px; font-size: 13px;">S</div>
                <div class="room-title" id="room-name">Soporte General</div>
            </div>
            <div class="header-icons">
                <span class="icon-btn">📹</span>
                <span class="icon-btn">📞</span>
            </div>
        </div>

        <div class="messages-container" id="messages-list"></div>

        <div class="chat-input-bar">
            <input type="text" id="message-input" placeholder="Escribe un mensaje..." onkeypress="handleKey(event)">
            <div class="send-btn" onclick="sendMessage()">➤</div>
        </div>
    </div>

    <!-- BARRA DE NAVEGACIÓN INFERIOR (4 PESTAÑAS EXACTAS) -->
    <div class="bottom-nav">
        <div class="nav-item active" onclick="switchTab('chats', this)">
            <span>💬</span>Chats
        </div>
        <div class="nav-item" onclick="switchTab('novedades', this)">
            <span>⚡</span>Novedades
        </div>
        <div class="nav-item" onclick="switchTab('communities', this)">
            <span>👥</span>Comunidades
        </div>
        <div class="nav-item" onclick="switchTab('calls', this)">
            <span>📞</span>Llamadas
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
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

            const target = document.getElementById(`view-${tabName}`);
            if (target) target.classList.add('active');
            if (element) element.classList.add('active');
        }

        function toggleMenu(event) {
            event.stopPropagation();
            const menu = document.getElementById('app-dropdown');
            menu.classList.toggle('show');
        }

        function closeDropdowns(event) {
            const menu = document.getElementById('app-dropdown');
            if (menu && !menu.contains(event.target)) {
                menu.classList.remove('show');
            }
        }

        function openProfileView() {
            document.getElementById('app-dropdown').classList.remove('show');
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.getElementById('view-profile').classList.add('active');
        }

        function closeProfileView() {
            document.getElementById('view-profile').classList.remove('active');
            document.getElementById('view-chats').classList.add('active');
        }

        function openChat(name, recipientId) {
            currentRecipientId = recipientId;
            document.getElementById('room-name').innerText = name;
            document.getElementById('room-avatar').innerText = name.charAt(0);
            document.getElementById('view-chat-room').classList.add('active');
        }

        function closeChat() {
            document.getElementById('view-chat-room').classList.remove('active');
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
