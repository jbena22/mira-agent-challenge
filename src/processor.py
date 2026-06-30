"""
Módulo encargado del procesamiento del documento.

Responsabilidades:

1. Dividir el documento en fragmentos (chunks).
2. Generar embeddings utilizando Gemini.
3. Crear una base vectorial Chroma.
"""

from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


def crear_vector_store(texto_crudo):
    """
    Convierte un documento de texto en una base vectorial.

    Parameters
    ----------
    texto_crudo : str
        Texto completo extraído del documento.

    Returns
    -------
    Chroma
        Base vectorial lista para realizar búsquedas semánticas.
    """

    # Dividir el texto en fragmentos más pequeños
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    documentos = text_splitter.create_documents(
        [texto_crudo]
    )

    # Inicializar el modelo de embeddings de Gemini
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    # Crear la base vectorial
    vectorstore = Chroma.from_documents(
        documents=documentos,
        embedding=embeddings
    )

    return vectorstore