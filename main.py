import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import usuarios, clientes, membresias, pagos, reportes, notificaciones

app = FastAPI(title="Gym Management Backend")

# Configuración de CORS para permitir llamadas desde el frontend en modo dev
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers de tu aplicación
app.include_router(usuarios.router)
app.include_router(pagos.router)
app.include_router(clientes.router)
app.include_router(membresias.router)
app.include_router(notificaciones.router)
app.include_router(reportes.router)




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)