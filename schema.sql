-- Crear tabla de usuarios
CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    contraseña TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('dueño','gerente')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_email ON usuarios(email);
CREATE INDEX idx_rol ON usuarios(rol);

-- Crear tabla de clientes
CREATE TABLE clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT 1
);

CREATE INDEX idx_nombre ON clientes(nombre);
CREATE INDEX idx_email_cliente ON clientes(email);

-- Crear tabla de membresías
CREATE TABLE membresias (
    id_membresia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('dia','mensual','trimestral','anual')),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    precio REAL NOT NULL,
    activa BOOLEAN DEFAULT 1,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE
);

CREATE INDEX idx_cliente ON membresias(id_cliente);
CREATE INDEX idx_tipo ON membresias(tipo);
CREATE INDEX idx_fecha_fin ON membresias(fecha_fin);

-- Crear tabla de pagos
CREATE TABLE pagos (
    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_membresia INTEGER,
    fecha_pago DATE NOT NULL,
    monto REAL NOT NULL,
    estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente','pagado')),
    FOREIGN KEY (id_membresia) REFERENCES membresias(id_membresia) ON DELETE SET NULL
);

CREATE INDEX idx_membresia ON pagos(id_membresia);
CREATE INDEX idx_estado ON pagos(estado);
CREATE INDEX idx_fecha_pago ON pagos(fecha_pago);

-- Crear tabla de vencimientos
CREATE TABLE vencimientos (
    id_vencimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_membresia INTEGER NOT NULL,
    tipo_vencimiento TEXT NOT NULL CHECK(tipo_vencimiento IN ('pago','membresia')),
    fecha_vencimiento DATE NOT NULL,
    estado TEXT DEFAULT 'vigente' CHECK(estado IN ('vigente','vencido')),
    FOREIGN KEY (id_membresia) REFERENCES membresias(id_membresia) ON DELETE CASCADE
);

CREATE INDEX idx_membresia_venc ON vencimientos(id_membresia);
CREATE INDEX idx_tipo_venc ON vencimientos(tipo_vencimiento);
CREATE INDEX idx_fecha_venc ON vencimientos(fecha_vencimiento);
CREATE INDEX idx_estado_venc ON vencimientos(estado);