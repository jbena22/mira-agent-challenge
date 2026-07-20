"""
Configuración del modelo de lenguaje.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

def obtener_llm(modelo):
    """
    Retorna una instancia del modelo Gemini.
    """

    return ChatGoogleGenerativeAI(
        model=modelo
    )