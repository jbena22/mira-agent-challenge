from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

def crear_vector_store(texto_crudo):
    # 1. Dividir el texto en trozos pequeños para que la IA los entienda mejor
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.create_documents([texto_crudo])
    
    # 2. Crear los embeddings (convertir texto a números)
    # Nota: Necesitas configurar GOOGLE_API_KEY o GEMINI_API_KEY
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # 3. Guardar en una base de datos vectorial en memoria
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings
    )
    return vectorstore