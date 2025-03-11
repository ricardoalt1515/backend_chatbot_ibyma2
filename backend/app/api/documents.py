# app/api/documents.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import os
import shutil
from datetime import datetime
import uuid
from app.core.config import settings

router = APIRouter()

# Asegurar que exista el directorio para almacenar archivos
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: str = Form(...),
    message: str = Form(""),
):
    try:
        # Validar tamaño del archivo (máximo 10MB)
        MAX_SIZE = 10 * 1024 * 1024  # 10MB
        file_size = 0
        file_content = b""

        # Leer archivo por partes para validar tamaño
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            file_size += len(chunk)
            file_content += chunk
            if file_size > MAX_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="El archivo excede el tamaño máximo permitido (10MB)",
                )

        # Regresar al inicio del archivo
        await file.seek(0)

        # Crear nombre único para el archivo
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

        # Guardar archivo
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Procesar mensaje asociado con el archivo
        from app.services.chat_service import chat_service

        # Añadir mensaje del usuario mencionando el archivo
        file_message = f"He subido un archivo: {file.filename}"
        if message:
            file_message = f"{message}\n\nAdjunto el archivo: {file.filename}"

        # Obtener respuesta del asistente
        ai_response = await chat_service.process_message(
            conversation_id=conversation_id,
            message_text=file_message,
            file_info={
                "filename": file.filename,
                "path": file_path,
                "size": file_size,
                "content_type": file.content_type,
            },
        )

        return {
            "message": ai_response,
            "file_info": {
                "filename": file.filename,
                "stored_as": unique_filename,
                "size": file_size,
                "content_type": file.content_type,
            },
        }

    except Exception as e:
        # Asegurar que cualquier error no deje archivos incompletos
        if "file_path" in locals() and os.path.exists(file_path):
            os.remove(file_path)

        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=500, detail=f"Error al procesar el archivo: {str(e)}"
        )
