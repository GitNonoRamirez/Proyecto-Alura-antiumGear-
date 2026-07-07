# consulta_embedding.py
# Transformación de una pregunta en embedding relacionada al proyecto AntiumGear

from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Inicializa el modelo de embeddings (el mismo que usaste en la indexación)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

def generar_embedding(pregunta: str):
    vector = embeddings.embed_query(pregunta)
    return vector

if __name__ == "__main__":
    # Pregunta relacionada con el proyecto AntiumGear
    pregunta = "¿Cuál es el plazo máximo para solicitar un reembolso según la política de AntiumGear?"
    embedding = generar_embedding(pregunta)
    print("Pregunta:", pregunta)
    print("Embedding generado (primeros 10 valores):", embedding[:10])

