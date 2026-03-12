import datetime
from fastapi import APIRouter, HTTPException, Header
from db import get_connection
import jwt, os
import sqlite3

router = APIRouter(prefix="/pagos", tags=["Pagos"])
SECRET_KEY = os.getenv("SUPER_SECRET_KEY", "supersecret")

@router.post("/registrar/{id_membresia}")
def registrar_pago(id_membresia: int, monto: float, authorization: str = Header(...)):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        fecha_pago = datetime.date.today()

        cursor.execute("""
            SELECT id_pago FROM pagos
            WHERE id_membresia = ? AND estado = 'pendiente'
            ORDER BY id_pago DESC LIMIT 1
        """, (id_membresia,))
        pendiente = cursor.fetchone()

        if not pendiente:
            raise HTTPException(status_code=400, detail="No hay un pago pendiente para esta membresía")

        id_pago = pendiente["id_pago"]

        cursor.execute("""
            UPDATE pagos
            SET estado = 'pagado', fecha_pago = ?, monto = ?
            WHERE id_pago = ?
        """, (fecha_pago, monto, id_pago))
        conn.commit()

        cursor.execute("""
            SELECT c.nombre, c.telefono, m.tipo
            FROM membresias m
            JOIN clientes c ON m.id_cliente = c.id_cliente
            WHERE m.id_membresia = ?
        """, (id_membresia,))
        cliente = cursor.fetchone()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        nombre_cliente = cliente["nombre"]
        telefono = cliente["telefono"]
        tipo_membresia = cliente["tipo"]

        factura_texto = (
            f"*** GYM MANAGEMENT ***\n"
            f"Factura N° {id_pago}\n"
            f"Cliente: {nombre_cliente}\n"
            f"Membresía: {tipo_membresia}\n"
            f"Monto: ${monto}\n"
            f"Fecha: {fecha_pago}\n"
            f"Estado: PAGADO\n"
            f"--------------------------\n"
            f"Gracias por su pago!"
        )

        os.makedirs("facturas", exist_ok=True)
        ruta = f"facturas/factura_{id_pago}_{nombre_cliente}.txt"
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(factura_texto)

        return {
            "message": "Pago registrado y factura generada",
            "id_pago": id_pago,
            "factura": ruta,
            "factura_texto": factura_texto,
            "telefono": telefono
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.get("/listar")
def listar_pagos(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

    if payload["rol"] != "dueño":
        raise HTTPException(status_code=403, detail="Acceso denegado: solo el dueño puede ver movimientos de dinero")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id_pago, p.id_membresia, p.fecha_pago, p.monto, p.estado,
               c.nombre AS nombre_cliente, c.telefono, m.tipo AS tipo_membresia
        FROM pagos p
        JOIN membresias m ON p.id_membresia = m.id_membresia
        JOIN clientes c ON m.id_cliente = c.id_cliente
        WHERE p.id_pago = (
            SELECT MAX(p2.id_pago)
            FROM pagos p2
            WHERE p2.id_membresia = p.id_membresia
        )
    """)
    pagos = [dict(row) for row in cursor.fetchall()]

    for pago in pagos:
        pago["factura_texto"] = (
            f"🏋️ GYM MANAGEMENT\n\n"
            f"Factura N° {pago['id_pago']}\n"
            f"Cliente: {pago['nombre_cliente']}\n"
            f"Membresía: {pago['tipo_membresia']}\n"
            f"Monto: ${pago['monto']}\n"
            f"Fecha: {pago['fecha_pago']}\n"
            f"Estado: {pago['estado'].upper()}\n"
            f"--------------------------\n"
            f"Gracias por tu pago 💪"
        )

    hoy = datetime.date.today()
    cursor.execute("""
        SELECT COALESCE(SUM(monto), 0) AS total_mes
        FROM pagos
        WHERE estado = 'pagado'
          AND strftime('%Y', fecha_pago) = ?
          AND strftime('%m', fecha_pago) = ?
    """, (str(hoy.year), f"{hoy.month:02d}"))
    total_mes = cursor.fetchone()["total_mes"]

    conn.close()
    return {"pagos": pagos, "total_mes": total_mes}

@router.delete("/eliminar/{id_pago}")
def eliminar_pago(id_pago: int, authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

    if payload["rol"] not in ["dueño", "gerente"]:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM pagos WHERE id_pago = ?", (id_pago,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pago no encontrado")

        return {"message": f"Pago {id_pago} eliminado correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.get("/mensaje/clientes/{id_cliente}")
def generar_mensaje_cliente(id_cliente: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT nombre, telefono FROM clientes WHERE id_cliente = ?", (id_cliente,))
    cliente = cursor.fetchone()
    conn.close()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Mensaje fijo y sencillo
    mensaje = f"Hola {cliente['nombre']}, tu pago fue registrado correctamente."

    return {"texto": mensaje, "telefono": cliente["telefono"]}
