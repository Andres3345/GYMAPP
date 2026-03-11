from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from db import get_connection
import jwt, os
from datetime import datetime, timedelta

router = APIRouter(prefix="/membresias", tags=["Membresías"])
SECRET_KEY = os.getenv("SUPER_SECRET_KEY", "supersecret")

def validar_token(authorization: str):
    try:
        scheme, token = authorization.split()
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

class MembresiaRegistro(BaseModel):
    id_cliente: int
    tipo: str
    fecha_inicio: str
    fecha_fin: str
    precio: float

@router.post("/registrar")
def registrar_membresia(membresia: MembresiaRegistro, authorization: str = Header(...)):
    payload = validar_token(authorization)

    if payload["rol"] not in ["dueño", "gerente"]:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO membresias (id_cliente, tipo, fecha_inicio, fecha_fin, precio)
            VALUES (?, ?, ?, ?, ?)
        """, (
            membresia.id_cliente,
            membresia.tipo,
            membresia.fecha_inicio,
            membresia.fecha_fin,
            membresia.precio
        ))
        id_membresia = cursor.lastrowid

        cursor.execute("""
            INSERT INTO pagos (id_membresia, fecha_pago, monto, estado)
            VALUES (?, ?, ?, ?)
        """, (
            id_membresia,
            membresia.fecha_fin,
            membresia.precio,
            "pendiente"
        ))
        conn.commit()

        return {
            "message": "Membresía registrada y pago pendiente generado",
            "id_membresia": id_membresia
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.get("/listar")
def listar_membresias(authorization: str = Header(...)):
    payload = validar_token(authorization)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id_membresia, m.id_cliente, c.nombre AS nombre_cliente,
               m.tipo, m.fecha_inicio, m.fecha_fin, m.precio, m.activa
        FROM membresias m
        JOIN clientes c ON m.id_cliente = c.id_cliente
    """)
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"membresias": data}

@router.put("/renovar/{id_membresia}")
def renovar_membresia(id_membresia: int, authorization: str = Header(...)):
    payload = validar_token(authorization)

    if payload["rol"] not in ["dueño", "gerente"]:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT fecha_fin, tipo, precio, activa FROM membresias WHERE id_membresia = ?", (id_membresia,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Membresía no encontrada")

        fecha_fin_actual = datetime.strptime(row["fecha_fin"], "%Y-%m-%d").date()
        tipo = row["tipo"]
        precio = row["precio"]
        activa = row["activa"]

        if not activa:
            raise HTTPException(status_code=400, detail="No se puede renovar una membresía dada de baja")

        if tipo == "dia":
            nueva_fecha_fin = fecha_fin_actual + timedelta(days=1)
        elif tipo == "mensual":
            nueva_fecha_fin = fecha_fin_actual + timedelta(days=30)
        elif tipo == "trimestral":
            nueva_fecha_fin = fecha_fin_actual + timedelta(days=90)
        elif tipo == "anual":
            nueva_fecha_fin = fecha_fin_actual + timedelta(days=365)
        else:
            nueva_fecha_fin = fecha_fin_actual + timedelta(days=30)

        nueva_fecha_inicio = datetime.now().date()

        cursor.execute("UPDATE membresias SET fecha_inicio = ?, fecha_fin = ? WHERE id_membresia = ?", (nueva_fecha_inicio, nueva_fecha_fin, id_membresia))

        cursor.execute("""
            INSERT INTO pagos (id_membresia, fecha_pago, monto, estado)
            VALUES (?, ?, ?, ?)
        """, (id_membresia, nueva_fecha_fin, precio, "pendiente"))

        conn.commit()

        return {
            "message": "Membresía renovada y pago pendiente generado",
            "id_membresia": id_membresia,
            "nueva_fecha_fin": str(nueva_fecha_fin)
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.put("/baja/{id_membresia}")
def baja_membresia(id_membresia: int, authorization: str = Header(...)):
    payload = validar_token(authorization)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE membresias SET activa = 0 WHERE id_membresia = ?", (id_membresia,))
    conn.commit()
    conn.close()
    return {"message": "Membresía dada de baja correctamente"}

@router.put("/activar/{id_membresia}")
def activar_membresia(id_membresia: int, authorization: str = Header(...)):
    payload = validar_token(authorization)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE membresias SET activa = 1 WHERE id_membresia = ?", (id_membresia,))
    conn.commit()
    conn.close()
    return {"message": "Membresía reactivada correctamente"}

@router.get("/membresias")
def membresias_proximas(authorization: str = Header(...)):
    payload = validar_token(authorization)
    conn = get_connection()
    cursor = conn.cursor()
    fecha_limite = datetime.now().date() + timedelta(days=3)
    cursor.execute("""
        SELECT m.id_membresia, m.fecha_fin, c.nombre
        FROM membresias m
        JOIN clientes c ON m.id_cliente = c.id_cliente
        WHERE m.fecha_fin <= ?
    """, (fecha_limite,))
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"membresias": data}

@router.delete("/eliminar/{id_membresia}")
def eliminar_membresia(id_membresia: int, authorization: str = Header(...)):
    payload = validar_token(authorization)

    if payload["rol"] != "dueño":
        raise HTTPException(status_code=403, detail="Acceso denegado")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM membresias WHERE id_membresia = ?", (id_membresia,))
        conn.commit()
        return {"message": "Membresía y pagos asociados eliminados correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()