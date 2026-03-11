import os
import sys

from fastapi import FastAPI, staticfiles
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import usuarios, clientes, membresias, pagos, reportes, notificaciones
from fastapi.middleware.cors import CORSMiddleware




BUNDLE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

print(f"BUNDLE_DIR: {BUNDLE_DIR}")
assets_path = os.path.join(BUNDLE_DIR, "frontend_dist", "assets")
print(f"Assets path: {assets_path}")
print(f"Assets exists: {os.path.exists(assets_path)}")

app = FastAPI(title="Gym Management Backend")

# No mount, use custom route for SPA
origins = [
    "http://localhost:5173",  # tu frontend en Vite
    "http://127.0.0.1:5173",  # por si usas esta variante
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # permite todos los métodos: GET, POST, PUT, DELETE
    allow_headers=["*"],  # permite todas las cabeceras
)

app.include_router(usuarios.router)
app.include_router(pagos.router)
app.include_router(clientes.router)
app.include_router(membresias.router)
app.include_router(notificaciones.router)
app.include_router(reportes.router)
    
@app.get("/{path:path}")
async def serve_spa(path: str):
    if not path or path == "/":
        file_path = os.path.join(BUNDLE_DIR, "frontend_dist", "index.html")
    else:
        file_path = os.path.join(BUNDLE_DIR, "frontend_dist", path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        return FileResponse(os.path.join(BUNDLE_DIR, "frontend_dist", "index.html"))

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import time
    webbrowser.open("http://127.0.0.1:8000")
    time.sleep(1)  # Give time for browser to open
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)

@app.get("/")
def serve_frontend():
    return FileResponse("frontend_dist/index.html")


