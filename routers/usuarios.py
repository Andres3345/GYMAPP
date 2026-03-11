from fastapi import APIRouter, HTTPException
from db import get_connection
from pydantic import BaseModel
import bcrypt
import os
import jwt

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

SECRET_KEY = os.getenv("SUPER_SECRET_KEY", "supersecret")

class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    contraseña: str
    rol: str  # 'dueño' o 'gerente'

class UsuarioLogin(BaseModel):
    email: str
    contraseña: str

@router.post("/login")
def login_usuario(usuario: UsuarioLogin):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (usuario.email,))
    user = cursor.fetchone()

    conn.close()

    if not user or not bcrypt.checkpw(usuario.contraseña.encode("utf-8"), user["contraseña"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = jwt.encode(
        {"id_usuario": user["id_usuario"], "rol": user["rol"]},
        SECRET_KEY,
        algorithm="HS256"
    )

    return {"access_token": token, "token_type": "bearer"}

@router.post("/registro")
def registrar_usuario(usuario: UsuarioRegistro):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_pw = bcrypt.hashpw(usuario.contraseña.encode("utf-8"), bcrypt.gensalt())

    try:
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, contraseña, rol)
            VALUES (?, ?, ?, ?)
        """, (usuario.nombre, usuario.email, hashed_pw.decode("utf-8"), usuario.rol))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

    return {"message": "Usuario registrado correctamente"}