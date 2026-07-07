import os
import faiss
import numpy as np

# Carpeta donde guardaste los embeddings
embedding_folder = "documentos/documentos_embeddings"

# Lista para almacenar vectores y metadatos
vectors = []
metadatos = []

# Leer cada archivo de embeddings
for file in os.listdir(embedding_folder):
    if file.endswith(".txt.txt"):  # tus archivos tienen esta extensión
        path = os.path.join(embedding_folder, file)
        with open(path, "r", encoding="utf-8") as f:
            # Cada embedding está guardado como una lista de números separados por comas
            vector = np.array(eval(f.read()), dtype="float32")
            vectors.append(vector)
            metadatos.append({"archivo": file})

# Convertir lista a matriz numpy
matrix = np.vstack(vectors)

# Crear índice FAISS (L2 = distancia euclidiana)
index = faiss.IndexFlatL2(matrix.shape[1])
index.add(matrix)

# Guardar índice en carpeta vector_db
os.makedirs("vector_db", exist_ok=True)
faiss.write_index(index, "vector_db/antiumgear.index")

print("✅ Base vectorial creada con FAISS y guardada en vector_db/antiumgear.index")
