import pandas as pd
from pypdf import PdfReader
import streamlit as st

def procesar_documento(archivo):
    """
    Lee archivos PDF o CSV y extrae su contenido de forma organizada.
    """
    texto = ""
    
    # Obtener la extensión del archivo
    extension = archivo.name.split('.')[-1].lower()
    
    try:
        if extension == 'pdf':
            reader = PdfReader(archivo)
            for page in reader.pages:
                texto += page.extract_text()
        
        elif extension == 'csv':
            df = pd.read_csv(archivo)
            texto = df.to_string()
            
        else:
            st.error("Formato no soportado. Por favor, sube un PDF o CSV.")
            return None
            
        return texto
    
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        return None