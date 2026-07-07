# unir_metadatos.py
import pandas as pd

# Leer metadatos_chunks con separador ;
chunks = pd.read_csv(
    r"C:\Users\ramir\Proyecto-Alura-antiumGear-\documentos\documentos_metadatos\metadatos_chunks.csv",
    sep=";", encoding="latin-1"
)

# Leer metadatos_embeddings limpio (solo fecha y embedding_vector)
embeddings = pd.read_csv(
    r"C:\Users\ramir\Proyecto-Alura-antiumGear-\documentos\documentos_metadatos\metadatos_embeddings.csv",
    sep=";", encoding="utf-8"
)

# Unir por posición (fila 1 con fila 1, etc.)
df = pd.concat([chunks.reset_index(drop=True), embeddings.reset_index(drop=True)], axis=1)

# Guardar el resultado limpio
df.to_csv(
    r"C:\Users\ramir\Proyecto-Alura-antiumGear-\documentos\documentos_metadatos\metadatos_completo.csv",
    index=False, encoding="utf-8"
)

print("Columnas finales:", df.columns.tolist())
print("Primeras filas:\n", df.head().to_string())

