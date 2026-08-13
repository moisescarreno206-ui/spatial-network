class SpatialWebSocket {
  constructor(userId, token, onMessageReceived, onPresenceUpdate) {
    this.userId = userId;
    this.token = token;
    this.onMessageReceived = onMessageReceived;
    this.onPresenceUpdate = onPresenceUpdate;
    this.socket = null;
    this.reconnectInterval = 3000;
  }

  connect() {
    // Reemplaza con la URL pública de tu servidor FastAPI
    const wsUrl = `wss://tu-servidor.com/ws/chat?user_id=${this.userId}&token=${this.token}`;
    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log("🟢 Conectado a Spatial Network Engine");
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'new_message') {
        this.onMessageReceived(data);
      } else if (data.type === 'presence_status') {
        this.onPresenceUpdate(data);
      }
    };

    this.socket.onclose = () => {
      console.warn("🔴 Conexión perdida. Reintentando...");
      setTimeout(() => this.connect(), this.reconnectInterval);
    };

    this.socket.onerror = (error) => {
      console.error("Error WebSocket:", error);
      this.socket.close();
    };
  }

  sendMessage(recipientId, content, mediaUrl = null) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      const payload = {
        type: 'send_message',
        message_id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        recipient_id: recipientId,
        content: content,
        media_url: mediaUrl,
        timestamp: new Date().toISOString()
      };
      this.socket.send(JSON.stringify(payload));
    }
  }

  sendTypingStatus(recipientId, isTyping, mode = 'text') {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type: 'typing_status',
        recipient_id: recipientId,
        is_typing: isTyping,
        mode: mode // 'text' o 'audio'
      }));
    }
  }
}

export default SpatialWebSocket;
