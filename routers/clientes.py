from fastapi import APIRouter, HTTPException, Header
from db import get_connection
import jwt, os
from pydantic import BaseModel

router = APIRouter(prefix="/clientes", tags=["Clientes"])
SECRET_KEY = os.getenv("SUPER_SECRET_KEY", "supersecret")

def validar_token(authorization: str):
    try:
        scheme, token = authorization.split()
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

class ClienteRegistro(BaseModel):
    nombre: str
    email: str
    telefono: str

@router.post("/registrar")
def registrar_cliente(cliente: ClienteRegistro, authorization: str = Header(...)):
    payload = validar_token(authorization)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO clientes (nombre, email, telefono)
            VALUES (?, ?, ?)
        """, (cliente.nombre, cliente.email, cliente.telefono))
        conn.commit()
        id_cliente = cursor.lastrowid
        return {"message": "Cliente registrado correctamente", "id_cliente": id_cliente, "nombre": cliente.nombre}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.get("/listar")
def listar_clientes(authorization: str = Header(...)):
    payload = validar_token(authorization)

    if payload["rol"] not in ["dueño", "gerente"]:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"clientes": clientes}

@router.put("/editar/{id_cliente}")
def editar_cliente(id_cliente: int, cliente: ClienteRegistro, authorization: str = Header(...)):
    payload = validar_token(authorization)

    if payload["rol"] not in ["dueño", "gerente"]:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE clientes
            SET nombre = ?, email = ?, telefono = ?
            WHERE id_cliente = ?
        """, (cliente.nombre, cliente.email, cliente.telefono, id_cliente))
        conn.commit()
        return {"message": "Cliente actualizado correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.delete("/eliminar/{id_cliente}")
def eliminar_cliente(id_cliente: int, authorization: str = Header(...)):
    payload = validar_token(authorization)

    if payload["rol"] != "dueño":
        raise HTTPException(status_code=403, detail="Acceso denegado: solo el dueño puede eliminar clientes")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Eliminar pagos asociados
        cursor.execute("DELETE FROM pagos WHERE id_membresia IN (SELECT id_membresia FROM membresias WHERE id_cliente = ?)", (id_cliente,))
        # Eliminar membresías asociadas
        cursor.execute("DELETE FROM membresias WHERE id_cliente = ?", (id_cliente,))
        # Eliminar cliente
        cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
        conn.commit()

        return {"message": "Cliente, membresías y pagos eliminados correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


@router.put("/activar/{id_cliente}")
def activar_cliente(id_cliente: int, authorization: str = Header(...)):
    payload = validar_token(authorization)

    if payload["rol"] != "dueño":
        raise HTTPException(status_code=403, detail="Acceso denegado: solo el dueño puede activar clientes")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE clientes SET activo = 1 WHERE id_cliente = ?", (id_cliente,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        return {"message": "Cliente activado correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()