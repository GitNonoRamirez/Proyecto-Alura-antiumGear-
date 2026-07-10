import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHUNKS_DIR = os.path.join(BASE_DIR, "..", "documentos", "documentos_chunks")
EMBEDDINGS_DIR = os.path.join(BASE_DIR, "..", "documentos", "documentos_embeddings")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "documentos", "documentos_metadatos")

# --- Cargar metadatos de los chunks ---
rows_chunks = []
for archivo in os.listdir(CHUNKS_DIR):
    if archivo.endswith(".txt"):
        ruta = os.path.join(CHUNKS_DIR, archivo)
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            texto = f.read()
        rows_chunks.append({
            "archivo_chunk": archivo,
            "texto_chunk": texto.strip(),
            "documento_origen": archivo.split("_")[0] + ".txt"
        })

df_chunks = pd.DataFrame(rows_chunks)

# --- Cargar embeddings ---
rows_emb = []
for archivo in os.listdir(EMBEDDINGS_DIR):
    if archivo.endswith(".txt"):
        ruta = os.path.join(EMBEDDINGS_DIR, archivo)
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            vector = f.read()
        nombre_chunk = archivo.replace("embedding_", "")
        rows_emb.append({
            "archivo_chunk": nombre_chunk,
            "embedding_vector": vector.strip()
        })

df_emb = pd.DataFrame(rows_emb)

# --- Unir ambos DataFrames ---
df_final = pd.merge(df_chunks, df_emb, on="archivo_chunk", how="inner")

# --- Guardar CSV maestro con separador ; ---
os.makedirs(OUTPUT_DIR, exist_ok=True)
df_final.to_csv(os.path.join(OUTPUT_DIR, "metadatos_completo.csv"),
                sep=";", index=False, encoding="utf-8")

print("✅ Archivo metadatos_completo.csv generado correctamente en documentos_metadatos/")
