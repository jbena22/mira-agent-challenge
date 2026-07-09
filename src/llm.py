"""
Configuración del modelo de lenguaje.

Este módulo centraliza la creación del modelo Gemini para
facilitar futuros cambios de proveedor o versión.
"""

from langchain_google_genai import ChatGoogleGenerativeAI


def obtener_llm():
    """
    Retorna una instancia del modelo Gemini utilizado por la aplicación.
    """

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash"
    )