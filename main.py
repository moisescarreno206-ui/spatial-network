from pathlib import Path

# Obtiene la ruta exacta del directorio donde está main.py
BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"


@app.get("/")
async def get_home():
  if INDEX_FILE.exists():
    return FileResponse(INDEX_FILE)

  # Si no lo encuentra en la raíz, busca si está en carpetas comunes
  alt_paths = [
      BASE_DIR / "templates" / "index.html",
      BASE_DIR / "static" / "index.html",
      BASE_DIR / "modules" / "index.html",
  ]

  for path in alt_paths:
    if path.exists():
      return FileResponse(path)

  return HTMLResponse(
      f"<h2>🟢 Servidor Activo. Buscando index.html en: {INDEX_FILE}</h2>"
  )
    
