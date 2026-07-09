import os
import hashlib
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

DOCUMENTS_DIR = Path("documentos/documentos_txt")
STATE_FILE = Path("pipeline/state.json")
VECTOR_DB_DIR = Path("vector_db")

MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def calcular_hash(archivo):
    with open(archivo, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def cargar_estado():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_estado(estado):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2)

def generar_embeddings(texto):
    return MODEL.encode(texto).astype("float32")

def actualizar_faiss(embeddings, vector_db_dir):
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, f"{vector_db_dir}/antiumgear.index")
    print("[INFO] Índice FAISS actualizado.")

def actualizar_indice():
    estado_previo = cargar_estado()
    estado_actual = {}
    cambios_detectados = False
    embeddings_list = []

    for archivo in DOCUMENTS_DIR.glob("*.txt"):
        hash_actual = calcular_hash(archivo)
        estado_actual[str(archivo)] = hash_actual

        if str(archivo) not in estado_previo or estado_previo[str(archivo)] != hash_actual:
            print(f"[INFO] Cambio detectado en: {archivo}")
            cambios_detectados = True
            with open(archivo, "r", encoding="utf-8") as f:
                texto = f.read()
            embeddings_list.append(generar_embeddings(texto))

    if cambios_detectados:
        print("[INFO] Actualizando índice vectorial...")
        embeddings_array = np.vstack(embeddings_list)
        actualizar_faiss(embeddings_array, VECTOR_DB_DIR)
        guardar_estado(estado_actual)
        print("[INFO] Índice actualizado correctamente.")
    else:
        print("[INFO] No se detectaron cambios en los documentos.")

if __name__ == "__main__":
    actualizar_indice()

