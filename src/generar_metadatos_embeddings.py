import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDINGS_DIR = os.path.join(BASE_DIR, "..", "documentos", "documentos_embeddings")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "documentos", "documentos_metadatos")

rows = []
for archivo in os.listdir(EMBEDDINGS_DIR):
    if archivo.endswith(".txt"):
        ruta = os.path.join(EMBEDDINGS_DIR, archivo)
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            vector = f.read()
        # ejemplo: embedding_Politica_Reembolsos_chunk3.txt → Politica_Reembolsos_chunk3.txt
        nombre_chunk = archivo.replace("embedding_", "")
        rows.append({
            "archivo_chunk": nombre_chunk,
            "embedding_vector": vector.strip()
        })

df = pd.DataFrame(rows)

# Exportar con separador ;
os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(os.path.join(OUTPUT_DIR, "metadatos_embeddings.csv"),
          sep=";", index=False, encoding="utf-8")

print("✅ Archivo metadatos_embeddings.csv generado correctamente en documentos_metadatos/")

