from fastapi import APIRouter, Header, HTTPException
from datetime import datetime, timedelta
from db import get_connection

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

@router.get("/membresias-proximas")
def membresias_proximas(authorization: str = Header(...)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        fecha_limite = datetime.now().date() + timedelta(days=3)
        cursor.execute(
            "SELECT * FROM membresias WHERE fecha_fin <= ?",
            (fecha_limite,)
        )
        data = [dict(row) for row in cursor.fetchall()]
        return {"membresias_proximas": data}
    finally:
        conn.close()