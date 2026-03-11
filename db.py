import sqlite3, os, sys

DB_DIR = os.path.join(os.path.expanduser("~"), "GymGest")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "gym_management.db")

def get_connection():
    # Conecta al archivo .db en la carpeta del proyecto
    conn = sqlite3.connect(DB_PATH)
    # Permite acceder a las columnas por nombre en lugar de índices
    conn.row_factory = sqlite3.Row
    return conn