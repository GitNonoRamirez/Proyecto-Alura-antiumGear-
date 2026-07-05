import os
import faiss
import numpy as np

# Carpeta donde guardaste los embeddings
embedding_folder = "documentos/documentos_embeddings"

vectors = []
metadatos = []

for file in os.listdir(embedding_folder):
    if file.endswith(".txt.txt"):
        path = os.path.join(embedding_folder, file)
        with open(path, "r", encoding="utf-8") as f:
            vector = np.array(eval(f.read()), dtype="float32")
            vectors.append(vector)
            metadatos.append({"archivo": file})

matrix = np.vstack(vectors)

# Crear índice HNSW (más eficiente que IndexFlatL2)
dim = matrix.shape[1]
index = faiss.IndexHNSWFlat(dim, 32)  # 32 = número de conexiones por nodo
index.hnsw.efConstruction = 200       # parámetro de construcción (más alto = más precisión)
index.add(matrix)

# Guardar índice optimizado
os.makedirs("vector_db", exist_ok=True)
faiss.write_index(index, "vector_db/antiumgear_hnsw.index")

print("✅ Índice HNSW creado y guardado en vector_db/antiumgear_hnsw.index")
