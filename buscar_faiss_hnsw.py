import faiss
import numpy as np

# Cargar índice HNSW
index = faiss.read_index("vector_db/antiumgear_hnsw.index")

# Vector de prueba
query = np.random.rand(index.d).astype("float32").reshape(1, -1)

# Buscar los 5 más cercanos
distancias, indices = index.search(query, 5)

print("🔎 Resultados con HNSW:")
print("Indices encontrados:", indices)
print("Distancias:", distancias)
