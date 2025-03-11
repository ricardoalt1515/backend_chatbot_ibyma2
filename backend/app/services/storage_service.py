import motor.motor_asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import settings
from app.models.chat import Conversation, Message


class StorageService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.db = None
        self.conversations = None
        self.is_connected = False

    async def connect(self):
        """
        Establece conexión con MongoDB y verifica que funcione.
        """
        try:
            # Configurar cliente con timeout para evitar bloqueos largos
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,  # 5 segundos de timeout
            )

            # Verificar conexión
            await self.client.admin.command("ping")

            self.db = self.client[settings.MONGODB_DB]
            self.conversations = self.db.conversations
            self.is_connected = True
            self.logger.info("Conectado a MongoDB exitosamente")

            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.logger.error(f"No se pudo conectar a MongoDB: {str(e)}")
            self.is_connected = False

            # Usar almacenamiento en memoria como fallback
            self.logger.warning("Usando almacenamiento en memoria como alternativa")
            return False
        except Exception as e:
            self.logger.error(f"Error desconocido al conectar a MongoDB: {str(e)}")
            self.is_connected = False
            return False

    async def save_conversation(self, conversation: Conversation) -> Conversation:
        """
        Guarda una nueva conversación en la base de datos.
        """
        if not self.is_connected:
            self.logger.warning(
                "No hay conexión a MongoDB, usando almacenamiento en memoria"
            )
            # Aquí podrías implementar un almacenamiento en memoria alternativo
            return conversation

        conversation_dict = conversation.model_dump()
        result = await self.conversations.insert_one(conversation_dict)
        conversation.id = str(result.inserted_id)
        return conversation

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Recupera una conversación por su ID.
        """
        if not self.is_connected:
            self.logger.warning(
                "No hay conexión a MongoDB, usando almacenamiento en memoria"
            )
            return None

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

    async def add_message(self, conversation_id: str, message: Message) -> Message:
        """
        Añade un mensaje a una conversación existente.
        """
        if not self.is_connected:
            self.logger.warning(
                "No hay conexión a MongoDB, usando almacenamiento en memoria"
            )
            return message

        message_dict = message.model_dump()

        # Actualizar la conversación con el nuevo mensaje
        result = await self.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$push": {"messages": message_dict},
                "$set": {"updated_at": datetime.now()},
            },
        )

        if result.modified_count == 0:
            self.logger.warning(
                f"No se pudo añadir mensaje a la conversación: {conversation_id}"
            )

        return message

    async def update_conversation_step(
        self, conversation_id: str, step: str
    ) -> Conversation:
        """
        Actualiza el paso actual de una conversación.
        """
        if not self.is_connected:
            self.logger.warning(
                "No hay conexión a MongoDB, usando almacenamiento en memoria"
            )
            return None

        result = await self.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"current_step": step, "updated_at": datetime.now()}},
        )

        if result.modified_count == 0:
            self.logger.warning(
                f"No se pudo actualizar el paso de la conversación: {conversation_id}"
            )

        return await self.get_conversation(conversation_id)

    async def update_conversation(self, conversation: Conversation) -> Conversation:
        """
        Actualiza toda la conversación en la base de datos.
        """
        if not self.is_connected:
            self.logger.warning(
                "No hay conexión a MongoDB, usando almacenamiento en memoria"
            )
            return conversation

        conversation_dict = conversation.model_dump()

        # Eliminar el ID para no sobreescribirlo
        if "id" in conversation_dict:
            conversation_id = conversation_dict.pop("id")
        else:
            return None

        # Actualizar
        result = await self.conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {**conversation_dict, "updated_at": datetime.now()}},
        )

        if result.modified_count == 0:
            self.logger.warning(
                f"No se pudo actualizar la conversación: {conversation_id}"
            )

        return await self.get_conversation(conversation_id)


storage_service = StorageService()
