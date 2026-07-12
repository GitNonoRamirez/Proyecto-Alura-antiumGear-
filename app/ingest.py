import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Ruta absoluta a tu carpeta de PDFs
PDF_DIR = "C:/Users/ramir/Proyecto-Alura-antiumGear-/documentos"
DB_DIR = "chroma_db"

# Inicialización explícita del modelo de embeddings
embedder = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

def ingest_pdf(path):
    """Carga un PDF y lo divide en fragmentos"""
    loader = PyPDFLoader(path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    return chunks

def main():
    print("📂 Archivos encontrados en la carpeta:")
    print(os.listdir(PDF_DIR))  # Depuración: muestra los PDFs detectados

    all_chunks = []
    for file in os.listdir(PDF_DIR):
        if file.lower().endswith(".pdf"):  # acepta .pdf y .PDF
            path = os.path.join(PDF_DIR, file)
            print(f"📄 Procesando: {file}")
            chunks = ingest_pdf(path)
            print(f"   → {len(chunks)} fragmentos generados")
            all_chunks.extend(chunks)

    if not all_chunks:
        print("⚠️ No se encontraron fragmentos. Revisa que haya PDFs válidos en la carpeta.")
        return

    # Guardar en ChromaDB
    Chroma.from_documents(all_chunks, embedder, persist_directory=DB_DIR)
    print("✅ PDFs indexados en ChromaDB")

if __name__ == "__main__":
    main()
