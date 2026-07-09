"""
Prompts utilizados por el Agente Inteligente.

Separar los prompts del resto del código facilita su
mantenimiento y permite reutilizarlos si la aplicación crece.
"""

from langchain_core.prompts import ChatPromptTemplate


PROMPT_RAG = ChatPromptTemplate.from_template(
    """
    Eres un asistente especializado en responder preguntas
    utilizando únicamente la información proporcionada
    en el contexto.

    Si la respuesta no aparece en el contexto responde exactamente:

    "No encontré esa información en el documento."

    Contexto:
    {contexto}

    Pregunta:
    {pregunta}
    """
)