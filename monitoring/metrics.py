import time
import csv
from pathlib import Path

METRICS_FILE = Path("monitoring/metrics.csv")

def inicializar_metrics():
    """Crea el archivo CSV de métricas si no existe."""
    if not METRICS_FILE.exists():
        with open(METRICS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "pregunta", "respuesta", "sin_respuesta", "feedback_negativo", "tiempo_respuesta"])

def registrar_metricas(pregunta, respuesta, inicio, feedback_negativo=False):
    """
    Registra métricas de una interacción:
    - Pregunta y respuesta
    - Si la respuesta fue vacía (sin_respuesta)
    - Si hubo feedback negativo
    - Tiempo de respuesta en segundos
    """
    tiempo_respuesta = round(time.time() - inicio, 2)
    sin_respuesta = 1 if not respuesta or respuesta.strip() == "" else 0

    with open(METRICS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            pregunta,
            respuesta,
            sin_respuesta,
            1 if feedback_negativo else 0,
            tiempo_respuesta
        ])

def calcular_estadisticas():
    """
    Calcula métricas agregadas:
    - % preguntas sin respuesta
    - % feedback negativo
    - Tiempo promedio de respuesta
    """
    total = 0
    sin_respuesta = 0
    feedback_neg = 0
    tiempos = []

    if not METRICS_FILE.exists():
        return {"total": 0, "sin_respuesta_pct": 0, "feedback_neg_pct": 0, "tiempo_promedio": 0}

    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            sin_respuesta += int(row["sin_respuesta"])
            feedback_neg += int(row["feedback_negativo"])
            tiempos.append(float(row["tiempo_respuesta"]))

    return {
        "total": total,
        "sin_respuesta_pct": round((sin_respuesta / total) * 100, 2) if total > 0 else 0,
        "feedback_neg_pct": round((feedback_neg / total) * 100, 2) if total > 0 else 0,
        "tiempo_promedio": round(sum(tiempos) / len(tiempos), 2) if tiempos else 0
    }
