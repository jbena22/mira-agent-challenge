"""
Aplicación principal del Agente Inteligente.

Esta aplicación permite:
1. Cargar un documento PDF o CSV.
2. Procesar el documento y convertirlo en embeddings.
3. Almacenar los embeddings en una base vectorial (Chroma).
4. Recuperar el contexto más relevante según la pregunta del usuario.
5. Enviar el contexto a Gemini para generar una respuesta.
"""

import streamlit as st
from dotenv import load_dotenv

# Funciones propias del proyecto
from src.ingestion import procesar_documento
from src.processor import crear_vector_store

# Componentes de LangChain y Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Cargar variables de entorno (.env)
load_dotenv()

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Agente Inteligente para Documentos",
    page_icon="🤖",
    layout="wide"
)

# Título e introducción
st.title("🤖 Agente Inteligente para Documentos")

st.write(
    """
    Carga un documento en formato PDF o CSV y realiza preguntas
    sobre su contenido utilizando Inteligencia Artificial.
    """
)

# Permitir al usuario subir un archivo
uploaded_file = st.file_uploader(
    "Sube tu documento",
    type=["pdf", "csv"]
)

# Solo continuar cuando exista un archivo
if uploaded_file is not None:

    # Verificar si el usuario cambió el documento.
    # Esto evita volver a generar embeddings innecesariamente.
    if (
        "archivo_actual" not in st.session_state
        or st.session_state.archivo_actual != uploaded_file.name
    ):

        with st.spinner("Procesando documento..."):

            # Extraer el texto del archivo
            texto = procesar_documento(uploaded_file)

            # Validar que se haya obtenido contenido
            if not texto:
                st.error("No fue posible procesar el documento.")
                st.stop()

            # Guardar información en memoria durante la sesión
            st.session_state.archivo_actual = uploaded_file.name
            st.session_state.texto = texto

            # Crear la base vectorial a partir del texto
            st.session_state.vectorstore = crear_vector_store(texto)

        st.success("Documento procesado correctamente.")

    # Mostrar una vista previa del documento
    with st.expander("Vista previa del documento"):

        st.text_area(
            label="Contenido extraído",
            value=st.session_state.texto[:1500],
            height=250,
            disabled=True
        )

    # Caja de texto para ingresar preguntas
    pregunta = st.text_input(
        "¿Qué deseas saber sobre este documento?"
    )

    # Ejecutar únicamente cuando el usuario presione el botón
    if st.button("Consultar"):

        # Validar que exista una pregunta
        if not pregunta.strip():
            st.warning("Por favor escribe una pregunta.")
            st.stop()

        with st.spinner("Consultando el documento..."):

            # Crear un recuperador de información
            retriever = st.session_state.vectorstore.as_retriever(
                search_kwargs={"k": 3}
            )

            # Obtener los fragmentos más relevantes
            documentos = retriever.invoke(pregunta)

            # Unir los fragmentos recuperados
            contexto = "\n\n".join(
                doc.page_content
                for doc in documentos
            )

            # Inicializar el modelo Gemini
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash"
            )

            # Prompt que controla el comportamiento del modelo
            prompt = ChatPromptTemplate.from_template(
                """
                Eres un asistente especializado en responder preguntas
                utilizando únicamente la información proporcionada
                en el contexto.

                Si la respuesta no aparece en el contexto responde:

                "No encontré esa información en el documento."

                Contexto:
                {contexto}

                Pregunta:
                {pregunta}
                """
            )

            # Construir la cadena Prompt -> Modelo
            cadena = prompt | llm

            # Obtener la respuesta del modelo
            respuesta = cadena.invoke(
                {
                    "contexto": contexto,
                    "pregunta": pregunta
                }
            )

        # Mostrar la respuesta
        st.subheader("Respuesta")

        st.write(respuesta.content)