# buscar_faiss_filtrado.py
# Búsqueda semántica con filtrado por metadatos en AntiumGear

import faiss
import numpy as np
import pandas as pd
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Ruta absoluta al archivo de metadatos
# ⚠️ Ajusta la extensión si tu archivo se llama .csv o .txt
df = pd.read_csv(
    r"C:\Users\ramir\Proyecto-Alura-antiumGear-\documentos\documentos_metadatos\metadatos_embeddings.csv",
    sep=",",           # aseguramos que use coma como separador
    encoding="utf-8",  # para acentos y caracteres especiales
    engine="python"    # más tolerante con CSV grandes
)

# Mostrar columnas y categorías disponibles
print("Columnas disponibles en el CSV:", df.columns.tolist())
if "categoria" in df.columns:
    print("Categorías disponibles en el CSV:", df["categoria"].unique())

# Inicializar embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

def buscar_con_filtro(pregunta, palabra_filtro="reembolso"):
    # Generar embedding de la pregunta
    query_vector = np.array([embeddings.embed_query(pregunta)], dtype="float32")

    # Cargar índice FAISS
    index = faiss.read_index(
        r"C:\Users\ramir\Proyecto-Alura-antiumGear-\vector_db\antiumgear.index"
    )

    # Buscar los k más cercanos
    distancias, indices = index.search(query_vector, k=10)

    resultados = []
    for idx, dist in zip(indices[0], distancias[0]):
        fila = df.iloc[idx]
        # Filtro flexible: busca la palabra dentro de la categoría
        if "categoria" in df.columns and palabra_filtro.lower() in str(fila["categoria"]).lower():
            resultados.append({
                "texto": fila.get("archivo_chunk", ""),
                "documento": fila.get("documento_origen.txt", ""),
                "categoria": fila.get("categoria", ""),
                "distancia": dist
            })
    return resultados

if __name__ == "__main__":
    pregunta = "¿Cuál es el plazo máximo para solicitar un reembolso según la política de AntiumGear?"
    resultados = buscar_con_filtro(pregunta, palabra_filtro="reembolso")
    if resultados:
        for r in resultados:
            print(f"[{r['documento']} - {r['categoria']}] {r['texto']} (distancia: {r['distancia']})")
    else:
        print("No se encontraron resultados con el filtro aplicado.")

