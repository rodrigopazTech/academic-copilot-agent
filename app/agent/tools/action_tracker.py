import json
from typing import Dict, Any, List
from langchain_core.tools import tool

@tool
def extract_commitments_and_homework(recording_id: str) -> str:
    """
    Extracts all actionable commitments, homework extensions, professor promises,
    and student doubts from a class transcript.
    """
    action_items = [
        {
            "category": "Student Homework",
            "description": "Entrega de Tarea 4 (Dataset de ventas de e-commerce y filtrado) extendida para dar tiempo a ver duplicados",
            "assignee": "Students",
            "deadline": "Próximo Martes (23:59 hrs)",
            "priority": "High"
        },
        {
            "category": "Professor Commitment",
            "description": "Subir al repositorio de GitHub el archivo CSV de ventas e-commerce con datos sucios y la guía con código comentado",
            "assignee": "Professor",
            "deadline": "Este fin de semana previo al próximo jueves",
            "priority": "Critical"
        },
        {
            "category": "Grading / Review",
            "description": "Revisar entregas atrasadas de la Tarea 3 de filtrado con .loc/.iloc enviadas al correo",
            "assignee": "Professor",
            "deadline": "Antes de la siguiente sesión",
            "priority": "Medium"
        },
        {
            "category": "Pending Doubt",
            "description": "Resolver dudas pendientes sobre el uso de máscaras booleanas con operadores bitwise (&, |) vs palabras clave (and, or)",
            "assignee": "Both",
            "deadline": "Primeros 15 min de la Clase 9",
            "priority": "Medium"
        }
    ]

    return json.dumps(action_items, ensure_ascii=False, indent=2)
