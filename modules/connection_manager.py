import json
from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:

  def __init__(self):
    # Diccionario con estructura: { user_id: [WebSocket_1, WebSocket_2] }
    self.active_connections: Dict[str, List[WebSocket]] = {}

  async def connect(self, user_id: str, websocket: WebSocket):
    await websocket.accept()
    if user_id not in self.active_connections:
      self.active_connections[user_id] = []
    self.active_connections[user_id].append(websocket)

  def disconnect(self, user_id: str, websocket: WebSocket):
    if user_id in self.active_connections:
      if websocket in self.active_connections[user_id]:
        self.active_connections[user_id].remove(websocket)
      if not self.active_connections[user_id]:
        del self.active_connections[user_id]

  async def send_personal_message(self, message: dict, websocket: WebSocket):
    """Envía un mensaje a un socket específico."""
    await websocket.send_text(json.dumps(message))

  async def send_to_user(self, user_id: str, message: dict) -> bool:
    """Envía un mensaje a todos los dispositivos activos de un usuario."""
    if user_id in self.active_connections:
      for connection in self.active_connections[user_id]:
        await connection.send_text(json.dumps(message))
      return True
    return False  # El usuario no está conectado (mensaje diferido / push)

  async def broadcast_presence(self, user_id: str, status: str):
    """Notifica el estado de presencia a los sockets activos."""
    presence_event = {
        "type": "presence_status",
        "user_id": user_id,
        "status": status,
    }
    for active_user, sockets in self.active_connections.items():
      if active_user != user_id:
        for socket in sockets:
          await socket.send_text(json.dumps(presence_event))
          
