import os
import csv

# Carpeta de embeddings
embedding_folder = "documentos/documentos_embeddings"

# Carpeta de metadatos
metadatos_folder = "documentos/documentos_metadatos"
os.makedirs(metadatos_folder, exist_ok=True)

# Archivo de entrada (metadatos de etapa 2)
csv_metadatos_path = os.path.join(metadatos_folder, "metadatos_chunks.csv")

# Archivo de salida (nuevo CSV extendido)
csv_output_path = os.path.join(metadatos_folder, "metadatos_embeddings.csv")

# Leer metadatos originales (usando latin-1 y separador ;)
metadatos = {}
with open(csv_metadatos_path, "r", encoding="latin-1") as f:
    reader = csv.DictReader(f, delimiter=";")
    columnas = reader.fieldnames
    print("Columnas detectadas en CSV:", columnas)

    if "archivo_chunk" not in columnas:
        raise ValueError(f"No se encontró columna 'archivo_chunk'. Columnas disponibles: {columnas}")

    for row in reader:
        metadatos[row["archivo_chunk"]] = row

# Crear nueva lista con embeddings + metadatos
rows = []
for file in os.listdir(embedding_folder):
    if file.endswith(".txt"):
        file_path = os.path.join(embedding_folder, file)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            embedding = f.read().strip()

        print("Procesando embedding:", file)

        meta = metadatos.get(file, {})
        # Copiamos todas las columnas originales
        new_row = dict(meta)
        # Añadimos las nuevas
        new_row["fecha"] = "2026-07-04"
        new_row["embedding_vector"] = embedding
        rows.append(new_row)

# Guardar en nuevo CSV con todas las columnas originales + nuevas
fieldnames = columnas + ["fecha", "embedding_vector"]
with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ CSV extendido generado en {csv_output_path}")
