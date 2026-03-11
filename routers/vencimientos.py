from fastapi import APIRouter, HTTPException, Header
from db import get_connection
import jwt, os

router = APIRouter(prefix="/vencimientos", tags=["Vencimientos"])
SECRET_KEY = os.getenv("SUPER_SECRET_KEY", "supersecret")

def validar_token(authorization: str):
    try:
        scheme, token = authorization.split()
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.get("/proximos")
def vencimientos_proximos(authorization: str = Header(...)):
    payload = validar_token(authorization)

    # Dueño y gerentes pueden ver vencimientos
    if payload["rol"] not in ["dueño", "gerente"]:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT c.nombre, c.apellido, m.tipo, m.fecha_fin
            FROM membresias m
            JOIN clientes c ON m.id_cliente = c.id_cliente
            WHERE m.fecha_fin BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
        """)
        proximos = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return {"proximos_vencimientos": proximos}

@router.get("/vencidos")
def vencimientos_vencidos(authorization: str = Header(...)):
    payload = validar_token(authorization)

    if payload["rol"] not in ["dueño", "gerente"]:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT c.nombre, c.apellido, m.tipo, m.fecha_fin
            FROM membresias m
            JOIN clientes c ON m.id_cliente = c.id_cliente
            WHERE m.fecha_fin < CURDATE()
        """)
        vencidos = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return {"membresias_vencidas": vencidos}