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
  
# ==========================================
# FUNCIONES DE AUTENTICACIÓN (MÓDULO 1)
# ==========================================

def save_user(full_name: str, dob: str, email: str, password: str):
    """Guarda un nuevo usuario en la base de datos de Supabase."""
    try:
        data = {
            "full_name": full_name,
            "dob": dob,
            "email": email,
            "password": password  # Luego le agregamos encriptación
        }
        response = supabase.table("users").insert(data).execute()
        return response.data
    except Exception as e:
        print(f"⚠️ Error guardando usuario en Supabase: {e}")
        return None

def verify_user_credentials(username: str, password: str):
    """Verifica si el correo o nombre de usuario y contraseña coinciden en Supabase."""
    try:
        # Limpiamos cualquier espacio accidental al inicio o final del texto ingresado
        clean_username = username.strip() if username else ""
        print(f"🔍 Buscando credenciales para: '{clean_username}'")
        
        # 1. Buscar por correo electrónico (email)
        response = supabase.table("users").select("*").eq("email", clean_username).eq("password", password).execute()
        if response.data and len(response.data) > 0:
            print("✅ ¡Usuario encontrado por email!")
            return response.data[0]
        
        # 2. Buscar por nombre de usuario (full_name)
        response = supabase.table("users").select("*").eq("full_name", clean_username).eq("password", password).execute()
        if response.data and len(response.data) > 0:
            print("✅ ¡Usuario encontrado por full_name!")
            return response.data[0]
            
        print("❌ Supabase no devolvió ningún registro con estos datos.")
        return None
    except Exception as e:
        print(f"⚠️ Error verificando usuario en Supabase: {e}")
        return None
        
