# app/services/storage_service.py
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from app.models.chat import Conversation, Message


class StorageService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Almacenamiento en memoria
        self.conversations = {}

    async def save_conversation(self, conversation: Conversation) -> Conversation:
        """
        Guarda una conversación en memoria.
        """
        # Generar ID si no existe
        if not conversation.id:
            conversation_id = str(uuid.uuid4())
        else:
            conversation_id = conversation.id

        # Convertir a diccionario
        conversation_dict = conversation.model_dump()

        # Guardar en memoria
        self.conversations[conversation_id] = conversation_dict

        # Actualizar el ID en el objeto
        conversation.id = conversation_id

        return conversation

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Recupera una conversación por su ID.
        """
        try:
            conversation_data = self.conversations.get(conversation_id)
            if not conversation_data:
                return None

            # Crear objeto Conversation
            return Conversation(**conversation_data)
        except Exception as e:
            self.logger.error(f"Error al recuperar conversación: {str(e)}")
            return None

    async def add_message(
        self, conversation_id: str, role: str, content: str
    ) -> Message:
        """
        Añade un mensaje a una conversación.
        """
        message = Message(role=role, content=content)
        message_dict = message.model_dump()

        # Obtener conversación
        conversation_data = self.conversations.get(conversation_id)
        if not conversation_data:
            raise ValueError(f"Conversación no encontrada: {conversation_id}")

        # Añadir mensaje
        if "messages" not in conversation_data:
            conversation_data["messages"] = []

        conversation_data["messages"].append(message_dict)
        conversation_data["updated_at"] = datetime.now()

        # Actualizar en memoria
        self.conversations[conversation_id] = conversation_data

        return message

    async def update_conversation_step(
        self, conversation_id: str, step: str
    ) -> Conversation:
        """
        Actualiza el paso actual de una conversación.
        """
        conversation_data = self.conversations.get(conversation_id)
        if not conversation_data:
            raise ValueError(f"Conversación no encontrada: {conversation_id}")

        # Actualizar paso
        conversation_data["current_step"] = step
        conversation_data["updated_at"] = datetime.now()

        # Actualizar en memoria
        self.conversations[conversation_id] = conversation_data

        # Devolver conversación actualizada
        return Conversation(**conversation_data)

    async def update_conversation(self, conversation: Conversation) -> Conversation:
        """
        Actualiza toda la conversación.
        """
        if not conversation.id:
            raise ValueError("La conversación no tiene ID")

        # Convertir a diccionario
        conversation_dict = conversation.model_dump()

        # Actualizar en memoria
        self.conversations[conversation.id] = conversation_dict

        return conversation


# Instancia singleton
storage_service = StorageService()
