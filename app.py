import streamlit as st
from src.ingestion import procesar_documento
from src.processor import crear_vector_store
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

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
            with st.spinner("Buscando en el documento..."):
                
                vectorstore = crear_vector_store(texto)

                retriever = vectorstore.as_retriever(
                    search_kwargs={"k": 3}
                )

                documentos = retriever.invoke(pregunta)

                contexto = "\n\n".join(
                    doc.page_content
                    for doc in documentos
                )
                
                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

                prompt = ChatPromptTemplate.from_template("""
                Eres un asistente especializado en responder preguntas únicamente utilizando la información del contexto.

                Si la respuesta no está en el documento responde:

                "No encontré esa información en el documento."

                Contexto:
                {contexto}

                Pregunta:
                {pregunta}
                """)

                cadena = prompt | llm

                respuesta = cadena.invoke(
                    {
                        "contexto": contexto,
                        "pregunta": pregunta
                    }
                )

                st.write("### Respuesta:")
                st.write(respuesta.content)