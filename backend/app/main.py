# app/main.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import time

from app.api import chat, documents
from app.core.config import settings

app = FastAPI(
    title="Hydrous AI API",
    description="Backend para el chatbot de soluciones de reciclaje de agua",
    version="0.1.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ricardoalt1515.github.io/chatbot-widget/",  # dominio de github
        "http://localhost:3000",  # Para pruebas locales
        "*",  # Para desarrollo (quitar en produccion)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Añadir middleware para límite de tasa
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Aquí implementarías un limitador de tasa real
    # Para el MVP usamos un simple retraso
    client_ip = request.client.host
    # Simular verificación de límite
    time.sleep(0.05)  # Pequeño retraso
    response = await call_next(request)
    return response


# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Incluir routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(documents.router, prefix="/api", tags=["documents"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}
