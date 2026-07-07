# buscar_reranking.py
import numpy as np
import pandas as pd
import faiss
import re

# 1. Cargar CSV
df = pd.read_csv(
    r"C:\Users\ramir\Proyecto-Alura-antiumGear-\documentos\documentos_metadatos\metadatos_completo.csv",
    encoding="utf-8"
)

# 2. Función para limpiar y convertir embeddings
def parse_embedding(emb_str):
    if isinstance(emb_str, str):
        emb_str = emb_str.strip("[]").replace(",", " ")
        tokens = re.findall(r"-?\d+\.\d+", emb_str)
        return np.array([float(x) for x in tokens])
    else:
        return np.array([])

# 3. Normalizar todos los embeddings a la misma longitud
parsed = df["embedding_vector"].apply(parse_embedding).values
max_len = max(len(v) for v in parsed)
embeddings = np.vstack([np.pad(v, (0, max_len - len(v))) for v in parsed])

# Guardamos los embeddings normalizados en el DataFrame
df["embedding_array"] = [np.pad(v, (0, max_len - len(v))) for v in parsed]

# 4. Crear índice FAISS
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# 5. Función de búsqueda con reranking
def buscar_reranking(query_embedding, k=10):
    D, I = index.search(np.array([query_embedding]), k)
    candidatos = df.iloc[I[0]].copy()
    
    def cos_sim(a, b):
        if len(a) == 0 or len(b) == 0:
            return 0.0
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    # Usamos directamente la columna embedding_array ya normalizada
    candidatos["score"] = candidatos["embedding_array"].apply(
        lambda emb: cos_sim(query_embedding, emb)
    )
    
    return candidatos.sort_values(by="score", ascending=False)

# 6. Ejemplo de uso
if __name__ == "__main__":
    # Generamos un embedding de prueba con la misma dimensión que los del CSV
    query_emb = np.random.rand(max_len)
    resultados = buscar_reranking(query_emb, k=10)
    print(resultados[["documento_origen.txt", "categoria", "titulo_tema", "responsable", "score"]])
