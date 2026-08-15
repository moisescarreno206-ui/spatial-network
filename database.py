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
            "password": password
        }
        # Intentamos guardar
        response = supabase.table("users").insert(data).execute()
        print(f"✅ Usuario guardado con éxito: {response.data}")
        return response.data
    except Exception as e:
        # AQUÍ ESTÁ EL CAMBIO: Imprimimos el error técnico completo
        print(f"⚠️ ERROR DETALLADO DE SUPABASE: {e}")
        return None

def verify_user_credentials(username: str, password: str):
    """Verifica si el correo o nombre de usuario y contraseña coinciden en Supabase."""
    try:
        clean_username = username.strip() if username else ""
        clean_password = password.strip() if password else ""
        print(f"🔍 Buscando credenciales para: '{clean_username}' con contraseña: '{clean_password}'")
        
        # 1. Buscar por correo electrónico (ignorando mayúsculas/minúsculas)
        res_email = supabase.table("users").select("*").ilike("email", clean_username).eq("password", clean_password).execute()
        print(f"📦 Resultado búsqueda por email: {res_email.data}")
        if res_email.data and len(res_email.data) > 0:
            print("✅ ¡Usuario encontrado por email!")
            return res_email.data[0]
        
        # 2. Buscar por nombre de usuario / full_name (ignorando mayúsculas/minúsculas)
        res_name = supabase.table("users").select("*").ilike("full_name", clean_username).eq("password", clean_password).execute()
        print(f"📦 Resultado búsqueda por full_name: {res_name.data}")
        if res_name.data and len(res_name.data) > 0:
            print("✅ ¡Usuario encontrado por full_name!")
            return res_name.data[0]
            
        print("❌ Supabase no devolvió ningún registro con estos datos.")
        return None
    except Exception as e:
        print(f"⚠️ Error crítico en verify_user_credentials: {e}")
        return None
