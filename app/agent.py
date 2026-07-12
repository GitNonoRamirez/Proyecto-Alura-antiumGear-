from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

DB_DIR = "chroma_db"

def get_agent():
    # Embeddings locales con HuggingFace
    embedder = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # Base vectorial Chroma
    vectordb = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embedder
    )

    # LLM de Google Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",   # puedes usar "gemini-1.5-pro"
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # Prompt base
    prompt = ChatPromptTemplate.from_template(
        "Usa el siguiente contexto para responder la pregunta.\n\nContexto:\n{context}\n\nPregunta:\n{question}"
    )

    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    # Definimos el agente manualmente
    def agent_fn(question: str):
        docs = retriever.get_relevant_documents(question)
        context = "\n\n".join([d.page_content for d in docs])
        formatted_prompt = prompt.format(context=context, question=question)
        return llm.invoke(formatted_prompt)

    return agent_fn

if __name__ == "__main__":
    agent = get_agent()
    while True:
        query = input("❓ Pregunta sobre tus documentos: ")
        if query.lower() in ["salir", "exit", "quit"]:
            break
        result = agent(query)
        print(f"💡 Respuesta: {result.content}\n")
