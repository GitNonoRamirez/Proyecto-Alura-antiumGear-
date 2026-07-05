import faiss
import numpy as np

# Cargar el índice guardado
index = faiss.read_index("vector_db/antiumgear.index")

# Ejemplo de consulta: un vector aleatorio (en la práctica será el embedding de una pregunta)
query = np.random.rand(index.d).astype("float32").reshape(1, -1)

# Buscar los 5 más cercanos
distancias, indices = index.search(query, 5)

print("🔎 Resultados de la búsqueda:")
print("Indices encontrados:", indices)
print("Distancias:", distancias)
