from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

chats_bp = APIRouter()

@chats_bp.get("/chats", response_class=HTMLResponse)
async def chats_view(request: Request):
    # Opcional: si manejas sesiones, verifica aquí; si no, quítalo temporalmente para probar
    # if "user" not in request.session:
    #     return RedirectResponse(url="/", status_code=303)
    
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spatial Network - Chats</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #0d0f18; color: #fff; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }

        /* VISTAS */
        .view { display: none; flex-direction: column; height: 100%; width: 100%; }
        .view.active { display: flex; }

        /* --- VISTA 1: LISTA DE CHATS --- */
        .header-list { padding: 16px 20px 10px 20px; display: flex; align-items: center; justify-content: space-between; background-color: #0d0f18; }
        .header-title { font-size: 22px; font-weight: 800; background: linear-gradient(90deg, #c084fc, #e879f9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header-icons { display: flex; gap: 20px; color: #94a3b8; font-size: 18px; cursor: pointer; }

        .search-container { padding: 0 16px 12px 16px; }
        .search-box { display: flex; align-items: center; background-color: #16192b; border: 1px solid #232742; border-radius: 24px; padding: 10px 16px; gap: 12px; }
        .search-box input { background: transparent; border: none; outline: none; color: #fff; font-size: 14px; width: 100%; }
        .search-box input::placeholder { color: #64748b; }
        .search-box span { color: #64748b; }

        .archived-row { display: flex; align-items: center; gap: 16px; padding: 12px 20px; color: #cbd5e1; font-size: 14px; font-weight: 500; cursor: pointer; }
        .archived-row span:first-child { color: #c084fc; font-size: 16px; }

        .chats-list { flex: 1; overflow-y: auto; padding-bottom: 70px; }
        .chat-item { display: flex; align-items: center; padding: 12px 20px; gap: 14px; cursor: pointer; transition: background 0.2s; }
        .chat-item:hover { background-color: rgba(192, 132, 252, 0.05); }

        .avatar-wrapper { position: relative; width: 50px; height: 50px; flex-shrink: 0; }
        .avatar { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; background-color: #232742; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #c084fc; }
        .avatar-wrapper.online::after { content: ''; position: absolute; bottom: 2px; right: 2px; width: 12px; height: 12px; background-color: #22c55e; border: 2px solid #0d0f18; border-radius: 50%; }

        .chat-info { flex: 1; min-width: 0; border-bottom: 1px solid rgba(35, 39, 66, 0.4); padding-bottom: 12px; }
        .chat-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
        .chat-name { font-size: 15px; font-weight: 600; color: #fff; }
        .chat-time { font-size: 11px; color: #64748b; }
        .chat-preview { font-size: 13px; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 4px; }

        /* FAB (Floating Action Button) */
        .fab { position: fixed; bottom: 85px; right: 20px; width: 56px; height: 56px; background: linear-gradient(135deg, #8b5cf6, #a855f7); border-radius: 16px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 22px; box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4); cursor: pointer; z-index: 10; }

        /* Bottom Nav */
        .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; height: 65px; background-color: #121526; border-top: 1px solid #232742; display: flex; justify-content: space-around; align-items: center; z-index: 9; }
        .nav-item { display: flex; flex-direction: column; align-items: center; gap: 4px; color: #64748b; font-size: 11px; cursor: pointer; text-decoration: none; }
        .nav-item.active { color: #c084fc; font-weight: 600; }
        .nav-item span { font-size: 18px; }

        /* --- VISTA 2: SALA DE CHAT --- */
        .chat-room-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background-color: #16192b; border-bottom: 1px solid #232742; }
        .chat-room-user { display: flex; align-items: center; gap: 12px; cursor: pointer; }
        .chat-room-user img, .chat-room-user .avatar { width: 40px; height: 40px; border-radius: 50%; }
        .chat-room-name { font-size: 15px; font-weight: 600; }
        .chat-room-status { font-size: 11px; color: #22c55e; }
        .chat-room-actions { display: flex; gap: 20px; color: #c084fc; font-size: 18px; }

        .messages-container { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; background-color: #0d0f18; }
        
        .message-bubble { max-width: 75%; padding: 10px 14px; border-radius: 14px; font-size: 14px; line-height: 1.4; position: relative; display: flex; flex-direction: column; gap: 4px; }
        .message-bubble.received { background-color: #16192b; align-self: flex-start; border-top-left-radius: 4px; color: #cbd5e1; }
        .message-bubble.sent { background: linear-gradient(135deg, #8b5cf6, #a855f7); align-self: flex-end; border-top-right-radius: 4px; color: #fff; }
        
        .message-time { font-size: 10px; align-self: flex-end; color: rgba(255,255,255,0.7); margin-top: 2px; }
        .received .message-time { color: #64748b; }

        /* Estilo Nota de Voz en Chat */
        .voice-note { display: flex; align-items: center; gap: 10px; min-width: 200px; }
        .play-btn { width: 32px; height: 32px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 12px; }
        .waveform { flex: 1; height: 20px; display: flex; align-items: center; gap: 2px; }
        .bar { width: 3px; background: currentColor; border-radius: 2px; opacity: 0.6; }

        /* Input de mensaje inferior */
        .chat-input-bar { display: flex; align-items: center; padding: 10px 12px; background-color: #16192b; border-top: 1px solid #232742; gap: 8px; }
        .input-pill { flex: 1; display: flex; align-items: center; background-color: #0d0f18; border: 1px solid #232742; border-radius: 24px; padding: 8px 14px; gap: 10px; }
        .input-pill input { flex: 1; background: transparent; border: none; outline: none; color: #fff; font-size: 14px; }
        .input-pill input::placeholder { color: #64748b; }
        .input-pill span { color: #94a3b8; font-size: 18px; cursor: pointer; }
        
        .mic-fab { width: 45px; height: 45px; background: #8b5cf6; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; cursor: pointer; flex-shrink: 0; }

        /* Placeholder Content for Tabs */
        .placeholder-content { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #64748b; gap: 12px; padding-bottom: 70px; }
        .placeholder-content span { font-size: 36px; }
        .placeholder-content p { font-size: 15px; font-weight: 500; color: #94a3b8; }
    </style>
</head>
<body>

    <!-- ================= VIEW 1: LISTA DE CHATS ================= -->
    <div id="view-chats" class="view active">
        <div class="header-list">
            <div class="header-title">Spatial Network</div>
            <div class="header-icons">
                <span>📷</span>
                <span>⋮</span>
            </div>
        </div>

        <div class="search-container">
            <div class="search-box">
                <span>🔍</span>
                <input type="text" placeholder="Buscar chats o mensajes...">
            </div>
        </div>

        <div class="archived-row">
            <span>📥</span>
            <span>Archivados (3)</span>
        </div>

        <div class="chats-list">
            <!-- Chat Item 1 -->
            <div class="chat-item" onclick="openChat('Mamá', 'online')">
                <div class="avatar-wrapper online">
                    <div class="avatar">M</div>
                </div>
                <div class="chat-info">
                    <div class="chat-header-row">
                        <span class="chat-name">Mamá</span>
                        <span class="chat-time">2:50 p. m.</span>
                    </div>
                    <div class="chat-preview">🎵 Nota de voz (0:06)</div>
                </div>
            </div>

            <!-- Chat Item 2 -->
            <div class="chat-item" onclick="openChat('Juan Luis', 'online')">
                <div class="avatar-wrapper online">
                    <div class="avatar">J</div>
                </div>
                <div class="chat-info">
                    <div class="chat-header-row">
                        <span class="chat-name">Juan Luis</span>
                        <span class="chat-time">Ayer</span>
                    </div>
                    <div class="chat-preview"><span>✓✓</span> Sticker</div>
                </div>
            </div>

            <!-- Chat Item 3 -->
            <div class="chat-item" onclick="openChat('Lobby de jugadores', 'offline')">
                <div class="avatar-wrapper">
                    <div class="avatar" style="background:#2a2f55; color:#c084fc;">🎮</div>
                </div>
                <div class="chat-info">
                    <div class="chat-header-row">
                        <span class="chat-name">Lobby de jugadores</span>
                        <span class="chat-time">11/8/26</span>
                    </div>
                    <div class="chat-preview">+58 412-8544081 actualizó la duración...</div>
                </div>
            </div>

            <!-- Chat Item 4 -->
            <div class="chat-item" onclick="openChat('Esdrar', 'online')">
                <div class="avatar-wrapper online">
                    <div class="avatar" style="background:linear-gradient(135deg, #8b5cf6, #22c55e);">E</div>
                </div>
                <div class="chat-info">
                    <div class="chat-header-row">
                        <span class="chat-name">Esdrar (Core Team)</span>
                        <span class="chat-time">Ahora</span>
                    </div>
                    <div class="chat-preview">🚀 Despliegue completado con éxito en Render.</div>
                </div>
            </div>
        </div>

        <div class="fab">💬</div>
    </div>


    <!-- ================= VIEW 2: NOVEDADES ================= -->
    <div id="view-novedades" class="view">
        <div class="placeholder-content">
            <span>⚡</span>
            <p>Novedades de Spatial Network</p>
        </div>
    </div>


    <!-- ================= VIEW 3: COMUNIDADES ================= -->
    <div id="view-communities" class="view">
        <div class="placeholder-content">
            <span>👥</span>
            <p>Comunidades de Spatial Network</p>
        </div>
    </div>


    <!-- ================= VIEW 4: LLAMADAS ================= -->
    <div id="view-calls" class="view">
        <div class="placeholder-content">
            <span>📞</span>
            <p>Historial de llamadas espaciales</p>
        </div>
    </div>


    <!-- ================= VIEW 5: SALA DE CHAT INDIVIDUAL ================= -->
    <div id="view-chat-room" class="view">
        <div class="chat-room-header">
            <div class="chat-room-user" onclick="closeChat()">
                <span style="font-size: 20px; margin-right: 4px;">←</span>
                <div class="avatar" id="room-avatar">M</div>
                <div>
                    <div class="chat-room-name" id="room-name">Mamá</div>
                    <div class="chat-room-status" id="room-status">en línea</div>
                </div>
            </div>
            <div class="chat-room-actions">
                <span>📹</span>
                <span>📞</span>
                <span>⋮</span>
            </div>
        </div>

        <div class="messages-container" id="messages-list">
            <!-- Mensaje recibido (Nota de voz) -->
            <div class="message-bubble received">
                <div class="voice-note">
                    <div class="play-btn">▶</div>
                    <div class="waveform">
                        <div class="bar" style="height: 10px;"></div>
                        <div class="bar" style="height: 18px;"></div>
                        <div class="bar" style="height: 8px;"></div>
                        <div class="bar" style="height: 22px;"></div>
                        <div class="bar" style="height: 14px;"></div>
                        <div class="bar" style="height: 20px;"></div>
                        <div class="bar" style="height: 12px;"></div>
                    </div>
                    <span style="font-size: 11px; color: #64748b;">0:15</span>
                </div>
                <span class="message-time">2:39 p. m.</span>
            </div>

            <!-- Mensaje enviado (Texto) -->
            <div class="message-bubble sent">
                En la Movistar de la señora Omaira pusieron cachea
                <span class="message-time">2:46 p. m. ✓✓</span>
            </div>

            <!-- Mensaje recibido (Texto) -->
            <div class="message-bubble received">
                Ok
                <span class="message-time">2:46 p. m.</span>
            </div>

            <!-- Mensaje enviado (Nota de voz) -->
            <div class="message-bubble sent">
                <div class="voice-note">
                    <div class="play-btn">▶</div>
                    <div class="waveform">
                        <div class="bar" style="height: 14px;"></div>
                        <div class="bar" style="height: 22px;"></div>
                        <div class="bar" style="height: 10px;"></div>
                        <div class="bar" style="height: 18px;"></div>
                        <div class="bar" style="height: 24px;"></div>
                    </div>
                    <span style="font-size: 11px; color: rgba(255,255,255,0.8);">0:06</span>
                </div>
                <span class="message-time">2:50 p. m. ✓✓</span>
            </div>
        </div>

        <div class="chat-input-bar">
            <div class="input-pill">
                <span>😊</span>
                <input type="text" id="message-input" placeholder="Mensaje" onkeypress="handleKey(event)">
                <span>📎</span>
                <span>📷</span>
            </div>
            <div class="mic-fab" onclick="sendMessage()">🎤</div>
        </div>
    </div>


    <!-- ================= BOTTOM NAVIGATION BAR ================= -->
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
        function switchTab(tabName, element) {
            document.querySelectorAll('.view').forEach(v => {
                v.classList.remove('active');
            });
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

            const targetView = document.getElementById(`view-${tabName}`);
            if (targetView) {
                targetView.classList.add('active');
            }
            element.classList.add('active');
        }

        function openChat(name, status) {
            document.getElementById('room-name').innerText = name;
            document.getElementById('room-avatar').innerText = name.charAt(0);
            document.getElementById('room-status').innerText = status === 'online' ? 'en línea' : 'últ. vez hoy';
            
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.getElementById('view-chat-room').classList.add('active');
        }

        function closeChat() {
            document.getElementById('view-chat-room').classList.remove('active');
            document.getElementById('view-chats').classList.add('active');
        }

        function handleKey(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        }

        function sendMessage() {
            const input = document.getElementById('message-input');
            const text = input.value.trim();
            if (!text) return;

            const container = document.getElementById('messages-list');
            const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            const bubble = document.createElement('div');
            bubble.className = 'message-bubble sent';
            bubble.innerHTML = `${text} <span class="message-time">${timeStr} ✓✓</span>`;
            
            container.appendChild(bubble);
            input.value = '';
            container.scrollTop = container.scrollHeight;
        }
    </script>
</body>
</html>"""
    
    return HTMLResponse(content=html_content)
    
