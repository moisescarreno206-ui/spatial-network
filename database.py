import os
from supabase import Client, create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "TU_SUPABASE_URL_AQUI")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "TU_SUPABASE_ANON_KEY_AQUI")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_message(
    sender_id: int,
    recipient_id: int,
    content: str,
    msg_type: str = "texto",
    read: bool = False,
):
  """Guarda el mensaje en la tabla 'mensajes' de Supabase."""
  data = {
      "remitente_id": sender_id,
      "destinatario_id": recipient_id,
      "contenido": content,
      "tipo_mensaje": msg_type,
      "leido": read,
  }
  supabase.table("mensajes").insert(data).execute()


def get_pending_messages(recipient_id: int):
  """Obtiene los mensajes no leídos (no entregados/leídos) para el usuario."""
  response = (
      supabase.table("mensajes")
      .select("id, remitente_id, contenido, tipo_mensaje, created_at")
      .eq("destinatario_id", recipient_id)
      .eq("leido", False)
      .order("created_at", desc=False)
      .execute()
  )

  messages = []
  for row in response.data:
    messages.append({
        "type": "new_message",
        "message_id": row["id"],
        "sender_id": row["remitente_id"],
        "content": row["contenido"],
        "msg_type": row["tipo_mensaje"],
        "timestamp": row["created_at"],
    })
  return messages


def mark_pending_as_delivered(recipient_id: int):
  """Marca los mensajes como leídos/entregados."""
  supabase.table("mensajes").update({"leido": True}).eq(
      "destinatario_id", recipient_id
  ).eq("leido", False).execute()
  
