import os
import hashlib
import json
from pathlib import Path

DOCUMENTS_DIR = Path("documentos/documentos_txt")
STATE_FILE = Path("pipeline/state.json")
CURADURIA_FILE = Path("docs/curaduria/responsables.json")

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

def cargar_curaduria():
    if CURADURIA_FILE.exists():
        with open(CURADURIA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def obtener_area_responsable(documento, curaduria):
    for area, datos in curaduria.items():
        if documento in datos.get("documentos", []):
            return area, datos["responsable"], datos["correo"]
    return None, None, None

def actualizar_indice():
    estado_previo = cargar_estado()
    estado_actual = {}
    cambios_detectados = False
    curaduria = cargar_curaduria()

    for archivo in DOCUMENTS_DIR.glob("*.txt"):
        hash_actual = calcular_hash(archivo)
        estado_actual[str(archivo)] = hash_actual

        if str(archivo) not in estado_previo or estado_previo[str(archivo)] != hash_actual:
            print(f"[INFO] Cambio detectado en: {archivo.name}")
            cambios_detectados = True

            area, responsable, correo = obtener_area_responsable(archivo.name, curaduria)
            if area:
                print(f"   → Responsable: {responsable} ({area}) - Contacto: {correo}")
            else:
                print("   → No se encontró responsable asignado en curaduría.")

    if cambios_detectados:
        print("[INFO] Actualizando índice vectorial...")
        guardar_estado(estado_actual)
        print("[INFO] Índice actualizado correctamente.")
    else:
        print("[INFO] No se detectaron cambios en los documentos.")

if __name__ == "__main__":
    actualizar_indice()
