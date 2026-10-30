import json
from typing import Dict, Any, List
from langchain_core.tools import tool

@tool
def generate_next_class_package(course_name: str = "Ciencia de Datos", target_class_num: int = 9) -> str:
    """
    Generates a complete instructional pedagogical continuity package for the next class,
    including lesson timeline breakdown, fully documented executable demonstration Python code,
    and student hands-on exercises.
    """
    demo_code = '''"""
CLASE 9: CONTINUACIÓN PRÁCTICA - LIMPIEZA DE DUPLICADOS Y FILTRADO CON PANDAS
Instructor: Rodrigo Paz
"""
import pandas as pd

# 1. Carga de datos de e-commerce con valores sucios
data = {
    "ID_Pedido": [101, 102, 103, 103, 104, 105, 106],
    "Producto": ["Laptop Pro", "Mouse Gamer", "Teclado RGB", "Teclado RGB", "Monitor 4K", None, "Auriculares"],
    "Categoria": ["Electrónica", "Accesorios", "Accesorios", "Accesorios", "Electrónica", "Audio", "Audio"],
    "Precio_Unitario": [25000, 450, 1200, 1200, 8500, None, 1800],
    "Estado": ["Entregado", "Cancelado", "En Tránsito", "En Tránsito", None, "Entregado", "Entregado"]
}
df = pd.DataFrame(data)

print("--- 1. DIAGNÓSTICO DE NULOS ---")
# .isna().sum() identifica el recuento de valores NaN por columna
print(df.isna().sum())

print("\\n--- 2. LIMPIEZA DE FILAS CORRUPTAS ---")
# dropna(subset=['Estado']) elimina pedidos sin estado definido
df_limpio = df.dropna(subset=["Estado"]).copy()

print("\\n--- 3. DETECCIÓN Y ELIMINACIÓN DE DUPLICADOS ---")
# duplicated() retorna máscara booleana de registros repetidos
print(f"Duplicados encontrados: {df_limpio.duplicated().sum()}")
df_sin_duplicados = df_limpio.drop_duplicates(subset=["ID_Pedido"]).copy()

print("\\n--- 4. FILTRADO MULTIVARIABLE CON .loc ---")
# Filtro por categoría 'Accesorios' con precio mayor a 500
filtro = df_sin_duplicados.loc[
    (df_sin_duplicados["Categoria"] == "Accesorios") & (df_sin_duplicados["Precio_Unitario"] >= 500),
    ["ID_Pedido", "Producto", "Precio_Unitario"]
]
print(filtro)
'''

    package = {
        "target_class_number": target_class_num,
        "title": f"Clase {target_class_num}: Cierre de Limpieza Avanzada y Filtrado Condicional en Pandas",
        "focus_objective": "Consolidar el dominio de duplicados, imputación selectiva y filtros booleanos multivariables antes de abordar GroupBy.",
        "time_allocation_minutes": {
            "Recapitulación y resolución de dudas de Tarea 4": 15,
            "Demostración guiada de drop_duplicates() y subset": 35,
            "Filtrado condicional complejo con .loc y operadores & / |": 35,
            "Laboratorio práctico en vivo de alumnos": 30,
            "Cierre y asignación de Tarea Integradora": 5
        },
        "demonstration_code": demo_code,
        "student_exercises": [
            "Detectar cuántos pedidos duplicados existen en el CSV de ventas sin alterar el DataFrame original.",
            "Eliminar duplicados manteniendo la última ocurrencia (keep='last') y comparar resultados.",
            "Crear un filtro con .loc que seleccione clientes con compras mayores a $15,000 en la categoría 'Electrónica'."
        ],
        "homework_assignment": "Completar el script de saneamiento de datos para el archivo ventas_ecommerce.csv y subirlo a la rama personal de GitHub."
    }

    return json.dumps(package, ensure_ascii=False, indent=2)
