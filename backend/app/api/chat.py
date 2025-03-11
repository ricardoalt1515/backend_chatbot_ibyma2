from fastapi import APIRouter, HTTPException, Body
from typing import Dict

from app.models.chat import ChatRequest, ChatResponse, Conversation
from app.services.chat_service import chat_service

router = APIRouter()


@router.post("/chat/start", response_model=Conversation)
async def start_conversation():
    """
    Inicia una nueva conversación.
    """
    try:
        conversation = await chat_service.start_conversation()
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/{conversation_id}/messages")
async def get_messages(conversation_id: str):
    """
    Recupera solo los mensajes de una conversacion.
    Util para mostrar en el frontend
    """
    conversation = await chat_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversacion no encontrada")

    # Filitrar solo los mensajes de usuario y asistente (no sistema)
    visible_messages = [
        msg.model_dump()
        for msg in conversation.messages
        if msg.role in ["user", "assistant"]
    ]

    return {"conversation_id": conversation_id, "messages": visible_messages}


@router.post("/chat/message", response_model=ChatResponse)
async def send_message(request: ChatRequest = Body(...)):
    """
    Procesa un mensaje del usuario y devuelve la respuesta.
    """
    if not request.conversation_id:
        raise HTTPException(status_code=400, detail="Se requiere ID de conversación")

    try:
        response = await chat_service.process_message(
            request.conversation_id, request.message
        )

        return ChatResponse(conversation_id=request.conversation_id, message=response)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """
    Recupera una conversación por su ID.
    """
    conversation = await chat_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    return conversation
