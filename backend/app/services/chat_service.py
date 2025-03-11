# app/services/chat_service.py (modificado)

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
from bson import ObjectId

from app.models.chat import Conversation, Message
from app.services.ai_service import ai_service
from app.core.config import settings
import motor.motor_asyncio


class ChatService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Conexión a MongoDB
        self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB]
        self.conversations = self.db.conversations

        # Pasos del cuestionario (simplificado)
        self.question_steps = [
            "welcome",
            "water_source",
            "daily_water_usage",
            "wastewater_volume",
            "main_contaminants",
            "current_treatment",
            "water_quality_data",
            "reuse_goals",
            "budget_range",
            "summary",
        ]

    async def start_conversation(self) -> Conversation:
        """
        Inicia una nueva conversación.
        """
        # Crear nueva conversación
        conversation = Conversation(messages=[], current_step="welcome")

        # Guardar en MongoDB
        conversation_dict = conversation.model_dump()
        result = await self.conversations.insert_one(conversation_dict)
        conversation.id = str(result.inserted_id)

        # Devolver solo el ID y estructura basica
        return conversation

    async def process_message(self, conversation_id: str, message_text: str) -> str:
        """
        Procesa un mensaje del usuario y devuelve la respuesta.
        Opcionalmente procesa informacion de un archivo adjunto
        """
        # Obtener conversación
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversación no encontrada: {conversation_id}")

        # Añadir mensaje del usuario
        await self.add_message(conversation_id, "user", message_text)

        # Si hay archivo, añadir informacion al contexto
        file_context = ""
        if file_info:
            # Guardar referencia al archivo en la conversacion
            await self.add_file_reference(conversation_id, file_info)

            # Extraer informacion basica del archivo segun su tipo
            file_context = await self.extract_file_info(file_info)

        # Recuperar historial de mensajes
        messages = [msg.model_dump() for msg in conversation.messages]

        # Añadir contexto del archivo si existe
        if file_context:
            messages.append(
                {
                    "role": "system",
                    "content": f"El usuario ha subido un archivo. informacion del archivo: {file_context}",
                }
            )

        # Obtener paso actual
        current_step = conversation.current_step

        # Determinar el siguiente paso
        next_step = self._get_next_step(current_step)

        # Actualizar paso
        if next_step:
            await self._update_conversation_step(conversation_id, next_step)

        # Obtener respuesta de la IA
        ai_response = await ai_service.get_chat_response(messages, next_step)

        # Añadir respuesta del asistente
        await self.add_message(conversation_id, "assistant", ai_response)

        return ai_response

    # Metodo para manejar archivos
    async def add_file_reference(self, conversation_id: str, file_info: dict):
        """
        Añade referencia a un archivo en la conversacion.
        """
        await self.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$push": {"files": file_info}, "$set": {"updated_at": datetime.now()}},
        )

    async def extract_file_info(self, file_info: dict) -> str:
        """
        Extrae informacion basica de un archivo segun su tipo.
        En una implementacion mas avanzada que despues haremos se procesaria el contenido.
        """
        filename = file_info.get("filename", "")
        file_path = file_info.get("path", "")
        content_type = file_info.get("content_type", "")

        # Informacion basica
        info = f"Nombre: {filename}, Tipo: {content_type}"

        return info

    async def add_message(
        self, conversation_id: str, role: str, content: str
    ) -> Message:
        """
        Añade un mensaje a la conversación.
        """
        message = Message(role=role, content=content)
        message_dict = message.model_dump()

        # Actualizar en MongoDB
        await self.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$push": {"messages": message_dict},
                "$set": {"updated_at": datetime.now()},
            },
        )

        return message

    async def _update_conversation_step(self, conversation_id: str, step: str) -> None:
        """
        Actualiza el paso actual de la conversación.
        """
        await self.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"current_step": step, "updated_at": datetime.now()}},
        )

    def _get_next_step(self, current_step: str) -> str:
        """
        Determina el siguiente paso en el cuestionario.
        """
        if current_step not in self.question_steps:
            return "water_source"  # Default a la primera pregunta real

        current_index = self.question_steps.index(current_step)
        next_index = current_index + 1

        if next_index >= len(self.question_steps):
            return "summary"  # Volver al paso final si ya se completó

        return self.question_steps[next_index]

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Recupera una conversación por su ID.
        """
        try:
            conversation_data = await self.conversations.find_one(
                {"_id": ObjectId(conversation_id)}
            )

            if not conversation_data:
                return None

            # Convertir _id de ObjectId a string
            conversation_data["id"] = str(conversation_data.pop("_id"))

            return Conversation(**conversation_data)
        except Exception as e:
            self.logger.error(f"Error al recuperar conversación: {str(e)}")
            return None


chat_service = ChatService()
