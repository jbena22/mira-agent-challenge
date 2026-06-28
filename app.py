import streamlit as st
from src.ingestion import procesar_documento

st.title("🤖 Agente Inteligente Funcional")

uploaded_file = st.file_uploader("Sube tu documento (PDF o CSV)", type=["pdf", "csv"])

if uploaded_file is not None:
    # Procesamiento
    texto = procesar_documento(uploaded_file)
    
    if texto:
        st.success("¡Documento procesado exitosamente!")
        with st.expander("Ver contenido extraído"):
            st.text(texto[:1000] + "...") # Muestra solo un preview
        
        pregunta = st.text_input("¿Qué deseas saber sobre este documento?")
        if st.button("Consultar"):
            st.info("Aquí conectaremos la lógica de la IA (RAG) próximamente.")