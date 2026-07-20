"""
===============================================================================
MIRA AI - Asistente Inteligente para Consulta de Documentos
===============================================================================

Aplicación principal desarrollada con Streamlit que implementa un flujo
Retrieval-Augmented Generation (RAG) para responder preguntas basadas
únicamente en el contenido de documentos PDF y CSV.

Flujo general de la aplicación:

1. El usuario carga un documento PDF o CSV.
2. El documento es procesado para extraer su contenido.
3. El contenido se divide en fragmentos (chunks).
4. Se generan embeddings mediante Google Gemini.
5. Se almacena la información en una base vectorial Chroma.
6. Ante una consulta:
    - Se recuperan los fragmentos más relevantes.
    - Se construye el contexto.
    - Gemini genera una respuesta utilizando únicamente dicho contexto.
7. La conversación se almacena en memoria para mejorar la experiencia
   del usuario durante la sesión.

Autor:
Jhonattan Benavides

Proyecto:
Challenge Alura - Agentes Inteligentes
"""

import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from src.ingestion import procesar_documento
from src.processor import crear_vector_store
from src.prompts import PROMPT_RAG
from src.llm import obtener_llm

# ============================================================
# CONFIGURACIÓN
# ============================================================

# Cargar las variables de entorno (.env)
# Aquí se obtiene la GOOGLE_API_KEY utilizada por Gemini.
load_dotenv()

# Configuración general de la aplicación Streamlit.
# Define el título de la pestaña, el icono y el diseño de la página.
st.set_page_config(
    page_title="Agente Inteligente para Documentos",
    page_icon="🤖",
    layout="wide"
)

# ============================================================
# SIDEBAR
# ============================================================
#
# Permite al usuario configurar algunos parámetros del sistema RAG
# sin necesidad de modificar el código.
#
# Parámetros configurables:
#
# • Modelo Gemini utilizado.
# • Tamaño de los fragmentos (Chunk Size).
# • Solapamiento entre fragmentos (Chunk Overlap).
# • Número de fragmentos recuperados (Top-K).
#
# También incluye una breve descripción del proyecto.

with st.sidebar:

    st.header("⚙️ Configuración")

    modelo = st.selectbox(
        "Modelo Gemini",
        [
            "gemini-2.5-flash"
        ]
    )

    chunk_size = st.slider(
        "Chunk Size",
        min_value=500,
        max_value=2000,
        value=1000,
        step=100
    )

    chunk_overlap = st.slider(
        "Chunk Overlap",
        min_value=0,
        max_value=500,
        value=200,
        step=50
    )

    k_chunks = st.slider(
        "Cantidad de fragmentos recuperados",
        min_value=1,
        max_value=10,
        value=3
    )

    st.divider()

    st.markdown("## ℹ️ Acerca del proyecto")

    st.write(
        """
        Este proyecto implementa un sistema **RAG
        (Retrieval-Augmented Generation)** utilizando:

        - Streamlit
        - LangChain
        - Google Gemini
        - ChromaDB
        """
    )

# ============================================================
# TÍTULO
# ============================================================

st.title("🤖 Asistente de Conocimiento, MIRA")

st.markdown(
    """
    ### Tu asistente inteligente para consultar documentos PDF y CSV

    Carga un documento, realiza preguntas en lenguaje natural y obtén
    respuestas basadas únicamente en la información contenida en el archivo
    mediante **Retrieval-Augmented Generation (RAG)**.
    """
)

# ============================================================
# VARIABLES DE SESIÓN
# ============================================================
#
# Streamlit vuelve a ejecutar el script completo cada vez que el usuario
# interactúa con la aplicación.
#
# session_state permite conservar información entre ejecuciones,
# evitando reprocesar documentos o perder el historial de conversación.

if "documentos_subidos" not in st.session_state:
    st.session_state.documentos_subidos = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ============================================================
# SUBIR DOCUMENTO
# ============================================================
#
# El usuario puede cargar únicamente archivos PDF o CSV.
# Una vez seleccionado el archivo comienza el flujo de procesamiento.

uploaded_file = st.file_uploader(
    "Sube tu documento",
    type=["pdf", "csv"]
)

if uploaded_file is not None:

    if (
        "archivo_actual" not in st.session_state
        or st.session_state.archivo_actual != uploaded_file.name
    ):

        with st.spinner("Procesando documento..."):

            # Extraer el contenido del documento.
            #
            # Dependiendo del tipo de archivo:
            #
            # • PDF → se extrae el texto página por página.
            # • CSV → se convierte la información tabular en texto.

            texto = procesar_documento(uploaded_file)

            if not texto:
                st.error("No fue posible procesar el documento.")
                st.stop()

            # Crear la base vectorial.
            #
            # Este proceso realiza:
            #
            # 1. División del documento en fragmentos.
            # 2. Generación de embeddings.
            # 3. Almacenamiento en ChromaDB.            

            (
                vectorstore,
                documentos
            ) = crear_vector_store(
                texto,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )

            st.session_state.archivo_actual = uploaded_file.name
            st.session_state.texto = texto
            st.session_state.vectorstore = vectorstore
            st.session_state.documentos = documentos

            if not any(
                d["nombre"] == uploaded_file.name
                for d in st.session_state.documentos_subidos
            ):
                
                # Registrar el documento cargado.
                #
                # Se almacena información básica para que el usuario pueda
                # consultar el historial durante la sesión.

                st.session_state.documentos_subidos.append(
                    {
                        "nombre": uploaded_file.name,
                        "tipo": uploaded_file.type,
                        "tamano": round(uploaded_file.size / 1024, 2),
                        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                )

        st.success("✅ Documento procesado correctamente.")

        st.info(
            f"""
            **Nombre:** {uploaded_file.name}

            **Tipo:** {uploaded_file.type}

            **Tamaño:** {round(uploaded_file.size / 1024,2)} KB
            """
        )

        st.caption(
            f"Se generaron {len(st.session_state.documentos)} fragmentos."
        )

    # ========================================================
    # VISTA PREVIA
    # ========================================================
    #
    # Mostrar una vista previa del contenido extraído.
    #
    # Esto permite verificar que el documento fue procesado correctamente
    # antes de realizar preguntas.

    with st.expander("📄 Vista previa del documento"):

        st.text_area(
            "Contenido extraído",
            st.session_state.texto[:1500],
            height=250,
            disabled=True
        )

    # ========================================================
    # CONSULTA AL DOCUMENTO
    # ========================================================
    #
    # El usuario escribe una pregunta en lenguaje natural.
    #
    # A partir de esta consulta comienza el flujo RAG:
    #
    # 1. Recuperación de fragmentos relevantes.
    # 2. Construcción del contexto.
    # 3. Generación de la respuesta con Gemini.    
    
    pregunta = st.chat_input(
        "Escribe tu pregunta sobre el documento..."
    )

    if pregunta:

        if not pregunta.strip():
            st.warning("Escribe una pregunta.")
            st.stop()

        inicio = time.time()

        with st.spinner("Consultando el documento..."):

            # Recuperar los K fragmentos más relevantes para la pregunta.
            #
            # Chroma realiza una búsqueda semántica utilizando los embeddings
            # previamente generados.
            
            retriever = st.session_state.vectorstore.as_retriever(
                search_kwargs={
                    "k": k_chunks
                }
            )
        
            documentos = retriever.invoke(pregunta)

            # Construir el contexto que será enviado al modelo.
            #
            # Los fragmentos recuperados se unen en un único texto para
            # proporcionar la información necesaria a Gemini.

            contexto = "\n\n".join(
                doc.page_content
                for doc in documentos
            )

            llm = obtener_llm(modelo)

            cadena = PROMPT_RAG | llm

            # Ejecutar el prompt RAG.
            #
            # El modelo recibe:
            #
            # • Contexto recuperado.
            # • Pregunta del usuario.
            #
            # El prompt está diseñado para responder únicamente utilizando
            # la información contenida en el documento.

            respuesta = cadena.invoke(
                {
                    "contexto": contexto,
                    "pregunta": pregunta
                }
            )

            st.session_state.chat_history.append(
                {
                    "pregunta": pregunta,
                    "respuesta": respuesta.content
                }
            )

        fin = time.time()

        # Calcular el tiempo total requerido para responder la consulta.
        
        tiempo_respuesta = fin - inicio

        st.session_state.tiempo_respuesta = tiempo_respuesta

        # ====================================================
        # CONTEXTO RECUPERADO
        # ====================================================
        #
        # Mostrar los fragmentos utilizados.
        #
        # Esta sección permite visualizar la evidencia utilizada por el modelo,
        # haciendo el proceso RAG más transparente.        

        with st.expander("🔍 Ver fragmentos utilizados"):

            for i, doc in enumerate(documentos, start=1):

                st.markdown(f"### Fragmento {i}")

                st.write(doc.page_content)

                st.divider()

# ============================================================
# HISTORIAL
# ============================================================
#
# Mostrar los documentos procesados durante la sesión actual.

if st.session_state.documentos_subidos:

    with st.expander("📚 Historial de documentos cargados"):

        for documento in st.session_state.documentos_subidos:

            st.markdown(
                f"""
                **📄 {documento["nombre"]}**

                - Tipo: {documento["tipo"]}
                - Tamaño: {documento["tamano"]} KB
                - Fecha: {documento["fecha"]}

                ---
                """
            )

# ============================================================
# HISTORIAL DE CONSULTAS
# ============================================================
#
# Mostrar la conversación mantenida con el asistente.
#
# Cada interacción contiene:
#
# • Pregunta del usuario.
# • Respuesta generada por el modelo.

if st.session_state.chat_history:

    st.subheader("💬 Conversación")

    for conversacion in st.session_state.chat_history:

        with st.chat_message("user"):
            st.write(conversacion["pregunta"])

        with st.chat_message("assistant"):
            st.write(conversacion["respuesta"])

    if "tiempo_respuesta" in st.session_state:

        st.caption(
            f"⏱ Tiempo de la última consulta: {st.session_state.tiempo_respuesta:.2f} segundos"
        )

# ============================================================
# BOTÓN PARA LIMPIAR SESIÓN
# ============================================================
#
# Reiniciar completamente la aplicación eliminando:
#
# • Documento cargado.
# • Base vectorial.
# • Historial de documentos.
# • Historial de conversación.
# • Variables de sesión.

st.divider()

if st.button("🗑 Limpiar sesión"):

    st.session_state.clear()

    st.rerun()