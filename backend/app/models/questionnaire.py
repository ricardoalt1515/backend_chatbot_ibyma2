from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field


class QuestionOption(BaseModel):
    value: str
    label: str


class Question(BaseModel):
    id: str
    question: str
    description: Optional[str] = None
    type: str = "text"  # "text", "number", "multiple_choice", "document", "date"
    options: Optional[List[QuestionOption]] = None
    required: bool = True
    unit: Optional[str] = None  # Para valores numéricos (m³/día, mg/L)
    next: Optional[str] = None  # ID de la siguiente pregunta
    conditional_next: Optional[List[Dict[str, Any]]] = None  # Flujo condicional


class Questionnaire(BaseModel):
    industry_type: str
    questions: Dict[str, Question]  # Mapa de ID a pregunta
    start_step: str  # ID de la primera pregunta
    version: str = "1.0"
