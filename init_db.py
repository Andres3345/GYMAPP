import sqlite3, os

DB_DIR = os.path.join(os.path.expanduser("~"), "GymGest")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "gym_management.db")

schema = """
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    contraseña TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('dueño','gerente')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS membresias (
    id_membresia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('dia','mensual','trimestral','anual')),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    precio REAL NOT NULL,
    activa BOOLEAN DEFAULT 1,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pagos (
    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_membresia INTEGER,
    fecha_pago DATE NOT NULL,
    monto REAL NOT NULL,
    estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente','pagado')),
    FOREIGN KEY (id_membresia) REFERENCES membresias(id_membresia) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS vencimientos (
    id_vencimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_membresia INTEGER NOT NULL,
    tipo_vencimiento TEXT NOT NULL CHECK(tipo_vencimiento IN ('pago','membresia')),
    fecha_vencimiento DATE NOT NULL,
    estado TEXT DEFAULT 'vigente' CHECK(estado IN ('vigente','vencido')),
    FOREIGN KEY (id_membresia) REFERENCES membresias(id_membresia) ON DELETE CASCADE
);
"""

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print(f"Base de datos creada con éxito: {DB_PATH}")

if __name__ == "__main__":
    init_db()