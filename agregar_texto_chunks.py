import pandas as pd
import os

# Ruta al CSV
csv_path = r"C:\Users\ramir\Proyecto-Alura-antiumGear-\documentos\documentos_metadatos\metadatos_completo.csv"

# Carpeta donde están los chunks de texto
chunks_folder = r"C:\Users\ramir\Proyecto-Alura-antiumGear-\documentos\documentos_chunks"

# Leer el CSV
df = pd.read_csv(csv_path, encoding="utf-8")

# Función para leer el texto del archivo_chunk con coincidencia parcial
def leer_chunk(nombre_archivo):
    ruta = os.path.join(chunks_folder, nombre_archivo)
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    else:
        # Buscar coincidencia parcial en la carpeta
        for file in os.listdir(chunks_folder):
            if nombre_archivo in file:
                with open(os.path.join(chunks_folder, file), "r", encoding="utf-8", errors="ignore") as f:
                    return f.read().strip()
        return "N/A"

# Crear nueva columna con el texto
df["texto_chunk"] = df["archivo_chunk"].apply(leer_chunk)

# Guardar CSV enriquecido
df.to_csv(csv_path, index=False, encoding="utf-8")

print("✅ CSV actualizado con columna texto_chunk usando coincidencia parcial")

