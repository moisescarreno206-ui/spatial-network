from fastapi import APIRouter, Form, HTTPException
from database import save_user, verify_user_credentials

router = APIRouter()

@router.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = verify_user_credentials(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"message": "Login exitoso", "user": user}

@router.post("/auth/register")
async def register(
    full_name: str = Form(...),
    dob: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    # Aquí llamarías a tu función de base de datos para guardar el usuario
    success = save_user(full_name, dob, email, password)
    if not success:
        raise HTTPException(status_code=400, detail="Error al registrar")
    return {"message": "Usuario creado con éxito"}
