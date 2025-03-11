# app/services/ai_service.py (extracto)
async def _get_groq_response(self, formatted_messages: List[Dict[str, str]]) -> str:
    """
    Obtiene respuesta de Groq.
    """
    try:
        response = self.groq_client.chat.completions.create(
            model=self.groq_model,
            messages=formatted_messages,
            temperature=0.7,
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as e:
        self.logger.error(f"Error al comunicarse con Groq: {str(e)}")
        # Mensaje de error detallado para ayudar a depurar
        import traceback

        self.logger.error(f"Traceback: {traceback.format_exc()}")

        # Devolver un mensaje genérico
        return "Lo siento, ha ocurrido un error al procesar tu solicitud. El equipo técnico ha sido notificado."
