# app/services/ai_service.py (modificado)

import logging
import openai
from groq import Groq
from typing import List, Dict, Any, Optional
from app.core.config import settings


class AIService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai_provider = settings.AI_PROVIDER

        # Setup OpenAI
        if self.ai_provider == "openai" or settings.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            self.openai_model = settings.OPENAI_MODEL

        # Setup Groq
        if self.ai_provider == "groq" or settings.GROQ_API_KEY:
            self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
            self.groq_model = settings.GROQ_MODEL

        # Prompt del sistema para Hydrous AI - Más específico
        self.system_prompt = """
        Eres el Hydrous AI Water Solution Designer, tu asistente experto en el diseño 
        de soluciones personalizadas para el tratamiento y reciclaje de aguas residuales.
        
        PROCESO DE RECOPILACIÓN DE INFORMACIÓN:
        - Dividirás el proceso en pasos pequeños y sencillos.
        - REALIZARÁS UNA SOLA PREGUNTA A LA VEZ, siguiendo estrictamente el orden del cuestionario.
        - Cada pregunta irá acompañada de una breve explicación de su importancia.
        - Para preguntas de opción múltiple, las respuestas estarán NUMERADAS.
        - NUNCA harás múltiples preguntas en un mismo mensaje.
        
        REGLAS IMPORTANTES:
        1. Mantén tus respuestas BREVES y CLARAS.
        2. Haz SOLO UNA PREGUNTA a la vez.
        3. NO avances a la siguiente pregunta hasta recibir respuesta a la actual.
        4. Si el usuario se desvía del tema, guíalo amablemente de vuelta al cuestionario.
        5. Si el usuario sube un archivo, analiza su contenido y menciona información relevante.
        
        PASOS DEL CUESTIONARIO:
        1. Preguntar sobre la fuente principal de agua para procesos industriales.
        2. Consultar sobre el consumo diario promedio de agua en metros cúbicos.
        3. Preguntar qué porcentaje del agua se convierte en agua residual.
        4. Consultar sobre los principales contaminantes en las aguas residuales.
        5. Preguntar si ya cuenta con algún sistema de tratamiento.
        6. Verificar si dispone de análisis de laboratorio recientes.
        7. Consultar el objetivo principal para el agua tratada.
        8. Preguntar sobre el rango presupuestario aproximado.
        9. Resumir la información recopilada.
        """

    async def get_first_question(self) -> str:
        """
        Obtiene la primera pregunta del cuestionario.
        """
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "system",
                    "content": """
                Genera la primera pregunta del cuestionario sobre soluciones de reciclaje de agua.
                Debe ser sobre la fuente principal de agua para procesos industriales.
                Incluye opciones numeradas y una breve explicación de su importancia.
                NO uses formato Markdown. Mantén la respuesta concisa.
                """,
                },
            ]

            if self.ai_provider == "groq" and settings.GROQ_API_KEY:
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=250,
                )
                return response.choices[0].message.content
            else:
                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=250,
                )
                return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Error al obtener primera pregunta: {str(e)}")
            return "¿Cuál es la fuente principal de agua para sus procesos industriales?\n\nImportancia: Conocer su fuente de agua nos ayuda a entender la calidad del agua entrante y posibles limitaciones.\n\n1. Agua municipal/potable\n2. Pozo/agua subterránea\n3. Agua superficial (río, lago)\n4. Agua de lluvia\n5. Otra fuente"

    async def get_chat_response(
        self, messages: List[Dict[str, str]], current_step: Optional[str] = None
    ) -> str:
        """
        Obtiene una respuesta de la IA basada en el historial de mensajes y el paso actual.
        """
        try:
            # Preparar mensajes para la API
            formatted_messages = self._format_messages(messages)

            # Añadir instrucción específica para garantizar formato adecuado
            format_instruction = """
            RECUERDA: 
            - Mantén tu respuesta BREVE y CLARA
            - Haz UNA SOLA pregunta
            - NO uses formato Markdown
            - Si es una pregunta de opción múltiple, NUMERA las opciones (1., 2., etc.)
            - Incluye una breve explicación de la importancia de la pregunta
            """

            formatted_messages.append({"role": "system", "content": format_instruction})

            # Si tenemos un paso actual, añadimos instrucción específica
            if current_step:
                step_instruction = f"Estás en el paso '{current_step}' del cuestionario. Responde al mensaje del usuario y luego haz solo UNA pregunta relacionada con este paso."
                formatted_messages.append(
                    {"role": "system", "content": step_instruction}
                )

            # Usar el proveedor configurado
            if self.ai_provider == "groq" and settings.GROQ_API_KEY:
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=formatted_messages,
                    temperature=0.7,
                    max_tokens=400,  # Limitamos tokens para respuestas más concisas
                )
                return response.choices[0].message.content
            else:
                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=formatted_messages,
                    temperature=0.7,
                    max_tokens=400,
                )
                return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Error al comunicarse con el servicio de IA: {str(e)}")
            return "Lo siento, ha ocurrido un error al procesar tu solicitud. Por favor, intenta nuevamente."

    def _format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Formatea los mensajes para la API de IA.
        """
        formatted_messages = [{"role": "system", "content": self.system_prompt}]

        # Limitar el contexto a los últimos 5 mensajes para mayor eficiencia
        recent_messages = messages[-10:] if len(messages) > 10 else messages

        # Añadir mensajes de la conversación
        for message in recent_messages:
            if message.get("role") in ["user", "assistant", "system"]:
                formatted_messages.append(
                    {"role": message["role"], "content": message["content"]}
                )

        return formatted_messages


ai_service = AIService()
