import os

PORT = int(os.environ.get("PORT", 5000))
SECRET_KEY = os.environ.get("SECRET_KEY", "spatial-network-2026-key")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xyzcompany.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "public-anon-key")

# Base de datos en memoria para respaldo rápido en ejecución
LOCAL_DB = {
    "users": {},
    "chats": {},
    "messages": {},
    "contacts": {},
    "blocked": {},
    "statuses": [],
    "groups": [],
    "reports": []
}

