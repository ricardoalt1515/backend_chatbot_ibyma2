from fastapi import APIRouter, Body
from typing import Dict, Any

router = APIRouter()


@router.post("/event")
async def log_event(event_data: Dict[str, Any] = Body(...)):
    """
    Endpoint simple para recibir eventos de analytics.
    En una implementacion real, aqui guardariamos los eventos en una base de datos.
    """
    # Por ahora solo registrara el evento en los logs
    print(f"Evento recibido: {event_data}")
    return {"status": "ok"}
