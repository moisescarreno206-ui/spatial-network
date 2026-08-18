import json
from pathlib import Path

from connection_manager import ConnectionManager
from database import (
    get_pending_messages,
    mark_pending_as_delivered,
    save_message,
)
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from virals import router as virals_router

# 1. Importación de Módulos (Autenticación y Chats)
from modules.auth import router as auth_router
from modules.chats import chats_bp as chats_router  # <-- Nuevo router integrado

app = FastAPI(title="Spatial Network - Engine Core")

# 2. Registrar rutas adicionales (Virales, Autenticación y Chats)
app.include_router(virals_router)
app.include_router(auth_router)
app.include_router(chats_router)  # <-- Registro de la nueva interfaz de chats

# 3. Gestor de conexiones WebSocket activa
manager = ConnectionManager()

# 4. Ubicación exacta de las plantillas gráficas
BASE_DIR = Path(__file__).resolve().parent
AUTH_FILE = BASE_DIR / "templates" / "auth.html"
INDEX_FILE = BASE_DIR / "templates" / "index.html"


# ⚠️ NOTA: El endpoint antiguo de /chats fue desactivado aquí para que 
# el nuevo módulo en modules/chats.py maneje correctamente la vista con pestañas.
# @app.get("/chats")
# async def get_chats_view():
#   if INDEX_FILE.exists():
#     return FileResponse(INDEX_FILE)
#   root_index = BASE_DIR / "index.html"
#   if root_index.exists():
#     return FileResponse(root_index)
#   return HTMLResponse("<h2>Archivo index.html no encontrado en templates/</h2>")


# 🏠 Ruta Raíz: Carga la pantalla de Autenticación (Login / Registro)
@app.get("/")
async def get_home():
  if AUTH_FILE.exists():
    return FileResponse(AUTH_FILE)

  # Respaldo por si auth.html estuviera suelto en la raíz
  root_auth = BASE_DIR / "auth.html"
  if root_auth.exists():
    return FileResponse(root_auth)

  return HTMLResponse(
      "<h2>🟢 Servidor Activo. Asegúrate de tener auth.html en la carpeta"
      " templates/</h2>"
  )


# 🧪 Ruta de Pruebas: Motor de prueba de WebSocket (chat previo)
@app.get("/test-ws")
async def get_test_ws():
  if INDEX_FILE.exists():
    return FileResponse(INDEX_FILE)

  root_index = BASE_DIR / "index.html"
  if root_index.exists():
    return FileResponse(root_index)

  return HTMLResponse("<h2>Motor de pruebas no encontrado.</h2>")


# ⚡ Endpoint WebSocket principal (/ws/chat)
@app.websocket("/ws/chat")
async def websocket_endpoint(
    websocket: WebSocket, user_id: str = Query(...), token: str = Query(...)
):
  await manager.connect(user_id, websocket)
  await manager.broadcast_presence(user_id, "online")

  # Entregar mensajes offline acumulados en Supabase
  try:
    pending_messages = get_pending_messages(user_id)
    if pending_messages:
      for msg in pending_messages:
        await manager.send_personal_message(msg, websocket)
      mark_pending_as_delivered(user_id)
  except Exception as e:
    print(f"⚠️ Error procesando mensajes pendientes: {e}")

  # Escucha continua de eventos
  try:
    while True:
      raw_data = await websocket.receive_text()
      data = json.loads(raw_data)
      event_type = data.get("type")

      # Evento: Enviar mensaje
      if event_type == "send_message":
        recipient_id = str(data.get("recipient_id"))
        msg_id = data.get("message_id")
        content = data.get("content")
        media_url = data.get("media_url")
        timestamp = data.get("timestamp")

        payload = {
            "type": "new_message",
            "message_id": msg_id,
            "sender_id": user_id,
            "content": content,
            "media_url": media_url,
            "timestamp": timestamp,
        }

        # Envío en tiempo real si el receptor está en línea
        delivered = await manager.send_to_user(recipient_id, payload)

        # Guardar registro en Supabase
        try:
          save_message(
              sender_id=user_id,
              recipient_id=recipient_id,
              content=content,
              msg_type="texto" if not media_url else "media",
              read=delivered,
          )
        except Exception as e:
          print(f"⚠️ Error guardando mensaje en Supabase: {e}")

        # Confirmación (ACK) al emisor
        await manager.send_personal_message(
            {
                "type": "server_ack",
                "message_id": msg_id,
                "status": "delivered" if delivered else "stored_offline",
            },
            websocket,
        )

      # Evento: Notificación de "Escribiendo..."
      elif event_type == "typing_status":
        recipient_id = str(data.get("recipient_id"))
        await manager.send_to_user(
            recipient_id,
            {
                "type": "user_typing",
                "sender_id": user_id,
                "is_typing": data.get("is_typing"),
                "mode": data.get("mode", "text"),
            },
        )

      # Evento: Confirmación de lectura
      elif event_type == "read_ack":
        sender_id = str(data.get("sender_id"))
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
    
