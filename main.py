import json
from connection_manager import ConnectionManager
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect

app = FastAPI(title="Spatial Network - Engine Core")
manager = ConnectionManager()


@app.websocket("/ws/chat")
async def websocket_endpoint(
    websocket: WebSocket, user_id: str = Query(...), token: str = Query(...)
):
  # TODO: Validar firma del token JWT de sesión aquí
  await manager.connect(user_id, websocket)

  # Notificar a la red que el usuario está "En línea"
  await manager.broadcast_presence(user_id, "online")

  try:
    while True:
      # Escuchar mensajes entrantes
      raw_data = await websocket.receive_text()
      data = json.loads(raw_data)
      event_type = data.get("type")

      # 1. Procesar envío de mensaje
      if event_type == "send_message":
        recipient_id = data.get("recipient_id")
        payload = {
            "type": "new_message",
            "message_id": data.get("message_id"),
            "sender_id": user_id,
            "content": data.get("content"),
            "media_url": data.get("media_url"),
            "timestamp": data.get("timestamp"),
        }

        # Intentar entrega directa en tiempo real
        delivered = await manager.send_to_user(recipient_id, payload)

        # Responder al emisor con acuse de recibo de servidor
        await manager.send_personal_message(
            {
                "type": "server_ack",
                "message_id": data.get("message_id"),
                "status": "delivered_to_server" if delivered else "stored",
            },
            websocket,
        )

      # 2. Indicadores de "Escribiendo..." o "Grabando audio..."
      elif event_type == "typing_status":
        recipient_id = data.get("recipient_id")
        await manager.send_to_user(
            recipient_id,
            {
                "type": "user_typing",
                "sender_id": user_id,
                "is_typing": data.get("is_typing"),
                "mode": data.get("mode", "text"),  # 'text' o 'audio'
            },
        )

      # 3. Confirmación de Lectura (Doble Check)
      elif event_type == "read_ack":
        sender_id = data.get("sender_id")
        await manager.send_to_user(
            sender_id,
            {
                "type": "message_read",
                "message_id": data.get("message_id"),
                "read_by": user_id,
            },
        )

  except WebSocketDisconnect:
    manager.disconnect(user_id, websocket)
    await manager.broadcast_presence(user_id, "offline")


if __name__ == "__main__":
  import uvicorn

  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
  
