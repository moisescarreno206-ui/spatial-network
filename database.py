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
    """Verifica credenciales mostrando un diagnóstico detallado en los logs de Render."""
    try:
        clean_username = username.strip() if username else ""
        clean_password = password.strip() if password else ""
        print(f"\n🔍 [LOGIN] Buscando -> Usuario/Email: '{clean_username}' | Contraseña: '{clean_password}'")
        
        # Traemos TODOS los usuarios de la tabla para inspeccionarlos
        all_users = supabase.table("users").select("*").execute()
        print(f"📋 [DEBUG] Registros totales en la tabla 'users': {all_users.data}")
        
        if not all_users.data:
            print("❌ [DEBUG] La tabla 'users' está vacía. Nadie se ha registrado correctamente.")
            return None

        # Revisamos registro por registro para ver dónde falla la coincidencia
        for user in all_users.data:
            db_email = str(user.get("email", "")).strip()
            db_name = str(user.get("full_name", "")).strip()
            db_pass = str(user.get("password", "")).strip()
            
            print(f"-> Comparando con DB -> email: '{db_email}', name: '{db_name}', pass: '{db_pass}'")
            
            email_match = db_email.lower() == clean_username.lower()
            name_match = db_name.lower() == clean_username.lower()
            pass_match = db_pass == clean_password
            
            if (email_match or name_match) and pass_match:
                print(f"✅ ¡Coincidencia exacta encontrada para el usuario ID {user.get('id')}!")
                return user
        
        print("❌ [DEBUG] Ningún usuario coincide con los datos ingresados.")
        return None
    except Exception as e:
        print(f"⚠️ Error crítico en verify_user_credentials: {e}")
        return None
