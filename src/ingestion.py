"""
Módulo encargado de la ingesta de documentos.

Actualmente soporta:

- PDF
- CSV

Su función principal es extraer el contenido textual para
que posteriormente pueda convertirse en embeddings.
"""

import pandas as pd
from pypdf import PdfReader
import streamlit as st


def procesar_documento(archivo):
    """
    Procesa un archivo PDF o CSV.

    Parameters
    ----------
    archivo : UploadedFile
        Archivo cargado desde Streamlit.

    Returns
    -------
    str
        Texto extraído del documento.
    """

    texto = ""

    # Obtener la extensión del archivo
    extension = archivo.name.split(".")[-1].lower()

    try:

        # Lectura de PDF
        if extension == "pdf":

            reader = PdfReader(archivo)

            for page in reader.pages:

                contenido = page.extract_text()

                # Algunos PDF contienen páginas vacías
                if contenido:
                    texto += contenido + "\n"

        # Lectura de CSV
        elif extension == "csv":

            df = pd.read_csv(archivo)

            # Convertir el DataFrame a texto
            texto = df.to_csv(index=False)

        else:

            st.error("Formato no soportado.")

            return None

        return texto

    except Exception as e:

        st.error(f"Error al procesar el documento: {e}")

        return None