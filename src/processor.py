"""
Módulo encargado del procesamiento del documento.

Responsabilidades:
1. Dividir el documento en fragmentos (chunks).
2. Generar embeddings utilizando Gemini.
3. Crear una base vectorial Chroma.
"""

from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

def crear_vector_store(
    texto_crudo,
    chunk_size=1000,
    chunk_overlap=200
):
    """
    Convierte un documento de texto en una base vectorial.

    Parameters
    ----------
    texto_crudo : str
        Texto completo extraído del documento.

    chunk_size : int
        Tamaño de cada fragmento.

    chunk_overlap : int
        Superposición entre fragmentos.

    Returns
    -------
    tuple
        (vectorstore, documentos)
    """

    # Dividir el texto en fragmentos
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    documentos = text_splitter.create_documents(
        [texto_crudo]
    )

    # Crear embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    # Crear base vectorial
    vectorstore = Chroma.from_documents(
        documents=documentos,
        embedding=embeddings
    )

    return vectorstore, documentos