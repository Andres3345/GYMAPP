from fastapi import APIRouter, HTTPException, Header
from db import get_connection
import jwt, os

router = APIRouter(prefix="/reportes", tags=["Reportes"])
SECRET_KEY = os.getenv("SUPER_SECRET_KEY", "supersecret")

def validar_token(authorization: str):
    try:
        scheme, token = authorization.split()
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.get("/ganancias-mensuales")
def ganancias_mensuales(anio: int, mes: int, authorization: str = Header(...)):
    payload = validar_token(authorization)

    if payload["rol"] != "dueño":
        raise HTTPException(status_code=403, detail="Acceso denegado: solo el dueño puede ver ganancias")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) AS total_ganancias
            FROM pagos
            WHERE estado = 'pagado'
              AND strftime('%Y', fecha_pago) = ?
              AND strftime('%m', fecha_pago) = ?
        """, (str(anio), f"{mes:02d}"))
        result = cursor.fetchone()
        return {"anio": anio, "mes": mes, "ganancias": result["total_ganancias"]}
    finally:
        conn.close()

@router.get("/ganancias-anuales")
def ganancias_anuales(anio: int, authorization: str = Header(...)):
    payload = validar_token(authorization)

    if payload["rol"] != "dueño":
        raise HTTPException(status_code=403, detail="Acceso denegado: solo el dueño puede ver ganancias")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT strftime('%m', fecha_pago) AS mes,
                   COALESCE(SUM(monto), 0) AS total_ganancias
            FROM pagos
            WHERE estado = 'pagado'
              AND strftime('%Y', fecha_pago) = ?
            GROUP BY mes
            ORDER BY mes
        """, (str(anio),))
        result = [dict(row) for row in cursor.fetchall()]
        return {"anio": anio, "ganancias": result}
    finally:
        conn.close()