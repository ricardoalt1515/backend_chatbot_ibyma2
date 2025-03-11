import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, documents, analytics
from app.core.config import settings

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hydrous AI API",
    description="Backend para el chatbot de soluciones de reciclaje de agua",
    version="0.1.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Evento de startup
@app.on_event("startup")
async def startup_db_client():
    try:
        # Aquí va tu código de inicialización
        logger.info("Aplicación iniciada correctamente")
    except Exception as e:
        # Forma correcta de usar logger.error
        logger.error("Error en startup: %s", str(e))


# Incluir routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/")
async def root():
    return {
        "message": "Hydrous AI Backend API",
        "version": "0.1.0",
        "status": "running",
        "docs_url": "/docs",
    }
