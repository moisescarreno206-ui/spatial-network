from fastapi import APIRouter, Form, HTTPException
from database import save_user, verify_user_credentials

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = verify_user_credentials(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"message": "Login exitoso", "user": user}

@router.post("/register")
async def register(
    full_name: str = Form(...),
    dob: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    user = save_user(full_name, dob, email, password)
    if not user:
        raise HTTPException(status_code=400, detail="Error al registrar el usuario o ya existe")
    return {"message": "Usuario creado con éxito", "user": user}
    
