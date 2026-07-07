from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

# Definir el modelo correcto (puedes usar gemini-embedding-001, gemini-embedding-2, etc.)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# Carpeta donde están tus chunks
carpeta_chunks = "documentos/documentos_chunks"
carpeta_salida = "documentos/documentos_embeddings"
os.makedirs(carpeta_salida, exist_ok=True)

# Recorrer todos los archivos de texto en la carpeta de chunks
for archivo in os.listdir(carpeta_chunks):
    if archivo.endswith(".txt"):
        ruta = os.path.join(carpeta_chunks, archivo)
        with open(ruta, "r", encoding="utf-8") as f:
            texto = f.read()

        # Generar embedding
        vector = embeddings.embed_query(texto)

        # Guardar embedding con el mismo nombre del chunk
        salida = os.path.join(carpeta_salida, f"embedding_{archivo}")
        with open(salida, "w", encoding="utf-8") as f:
            f.write(str(vector))

        print(f"Embedding generado: {salida}")



