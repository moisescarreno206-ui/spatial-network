from typing import Optional
from fastapi import APIRouter, Query

# Creamos el enrutador compatible con FastAPI
router = APIRouter(prefix="/api/settings", tags=["settings"])

virals_database = [
    {
        "creator": "amiti_official",
        "type": "video",
        "title": "Actualización Spatial V2",
        "url": "https://www.w3schools.com/html/mov_bbb.mp4",
    },
    {
        "creator": "tech_master",
        "type": "image",
        "title": "Setup de desarrollo 2026",
        "url": "https://picsum.photos/400/300",
    },
    {
        "creator": "amiti_official",
        "type": "image",
        "title": "Próximos servidores globales",
        "url": "https://picsum.photos/401/300",
    },
]


@router.get("/virals")
async def get_virals(creator: Optional[str] = Query("", description="Filtrar por creador")):
  creator_clean = creator.strip().lower() if creator else ""

  if creator_clean:
    results = [
        v for v in virals_database if creator_clean in v["creator"].lower()
    ]
  else:
    results = virals_database

  return {"status": "success", "items": results}
  
