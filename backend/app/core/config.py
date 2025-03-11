import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Añadir configuracion para archivos
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    ALLOWED_EXTENSIONS: List[str] = [
        ".pdf",
        ".docx",
        ".txt",
        ".csv",
        ".xlsx",
        ".jpg",
        ".jpeg",
        ".png",
    ]

    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Hydrous AI"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # AI Services
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")  # "openai" o "groq"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")

    # Groq
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "hydrous")

    class Config:
        env_file = ".env"


settings = Settings()
