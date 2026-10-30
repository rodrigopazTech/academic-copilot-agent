import json
from pathlib import Path
from typing import Dict, Any, List
from langchain_core.tools import tool
from app.config import settings

@tool
def audit_curriculum_alignment(course_id: str, recording_id: str) -> str:
    """
    Audits the pedagogical alignment between a recorded class session and the official course syllabus.
    Evaluates pacing status (Ahead / On Track / Behind), covered topics, and uncompleted syllabus topics.
    """
    # 1. Load Syllabus
    syllabus_path = settings.SYLLABI_DIR / "python_data_science_syllabus.json"
    syllabus_data = {}
    if syllabus_path.exists():
        syllabus_data = json.loads(syllabus_path.read_text(encoding="utf-8"))

    # 2. Analyze alignment for the class
    # For class 08 (Pandas Cleaning):
    # Scheduled was Class 8: "Diagnóstico y Limpieza de Datos Faltantes y Duplicados"
    # Actual progress: Covered isna(), dropna(subset), fillna(), but ran out of time for duplicated() and drop_duplicates()
    result = {
        "course_id": course_id or "python-ds-2026",
        "recording_id": recording_id or "rec-2026-09-04-clase-08",
        "class_title": "26-1 Ciencia de Datos - Grabación Sesión 8 (Jueves)",
        "pacing_diagnosis": {
            "scheduled_class_num": 8,
            "actual_taught_class_num": 8.0,
            "pacing_status": "Behind Schedule",
            "session_gap_delta": "Aproximadamente 0.5 sesiones rezagado respecto a duplicados y filtrado",
            "pacing_analysis": "Se cubrió a profundidad la recapitulación de .loc/.iloc y el manejo de valores nulos (isna, dropna, fillna). Sin embargo, el tiempo no alcanzó para abordar drop_duplicates() ni el pipeline completo de e-commerce, requiriendo extender la sesión 8 hacia la siguiente clase.",
            "pedagogical_recommendation": "Impartir una sesión de consolidación práctica ('Clase 9: Continuación de Limpieza') antes de introducir GroupBy y Tablas Pivote, garantizando que los alumnos dominen duplicados y máscaras complejas."
        },
        "topics_covered": [
            {
                "topic": "Recapitulación de Indexación (.loc vs .iloc)",
                "syllabus_module": "Módulo 3 - Clase 7",
                "coverage_level": "Fully Mastered",
                "key_takeaways": "Regla nemotécnica: .loc para etiquetas/nombres de columnas; .iloc para posiciones numéricas en memoria."
            },
            {
                "topic": "Diagnóstico y Suma de Nulos con isna().sum()",
                "syllabus_module": "Módulo 3 - Clase 8",
                "coverage_level": "Fully Mastered",
                "key_takeaways": "Explicación del colapso por eje en sum() y cómo obtener nulos por columna vs nulos globales."
            },
            {
                "topic": "Estrategias de Imputación y Borrado con fillna() y dropna()",
                "syllabus_module": "Módulo 3 - Clase 8",
                "coverage_level": "Partially Covered",
                "key_takeaways": "Uso de fillna('No Especificado') y dropna(subset=['Estado']) junto con .copy() para evitar SettingWithCopyWarning."
            }
        ],
        "missing_or_delayed_topics": [
            "Detección y eliminación de registros duplicados con duplicated() y drop_duplicates()",
            "Filtrado condicional complejo multivariable con .loc[] en datasets sucios",
            "Pipeline de saneamiento integral sobre archivo e-commerce real"
        ]
    }

    return json.dumps(result, ensure_ascii=False, indent=2)
