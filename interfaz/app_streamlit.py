import streamlit as st
import time
import pandas as pd
from components.fuentes import mostrar_fuentes
from components.feedback import mostrar_botones_feedback
from session_manager import inicializar_historial, agregar_interaccion, obtener_historial
from monitoring.metrics import inicializar_metrics, registrar_metricas, calcular_estadisticas, METRICS_FILE

# Configuración básica de la página
st.set_page_config(page_title="Agente AntiumGear", layout="wide")

# Aviso destacado de agente IA
st.warning("⚠️ Estás conversando con un **Agente de IA**. No es una persona real.")

# Inicializar historial y métricas
inicializar_historial()
inicializar_metrics()

# Campo de entrada de la pregunta
user_input = st.text_input("Escribe tu pregunta:")

# Simulación de respuesta del agente (por ahora)
def get_agent_response(query):
    return {
        "respuesta": f"Respuesta simulada para: {query}",
        "fuentes": ["Politica_Privacidad.txt", "Terminos_Condiciones.txt"]
    }

# Procesar la pregunta
if user_input:
    inicio = time.time()
    result = get_agent_response(user_input)
    agregar_interaccion(user_input, result["respuesta"], result["fuentes"])

    # Registrar métricas de esta interacción
    registrar_metricas(user_input, result["respuesta"], inicio, feedback_negativo=False)

# Mostrar historial de conversación
st.markdown("### Historial de conversación")
for i, item in enumerate(obtener_historial()):
    st.markdown(f"**Tú:** {item['pregunta']}")
    st.markdown(f"**Agente:** {item['respuesta']}")

    # Visualización clara de fuentes
    mostrar_fuentes(item['fuentes'])

    # Botones de feedback con registro en CSV
    mostrar_botones_feedback(item['pregunta'], item['respuesta'], item['fuentes'], i)

    st.markdown("---")

# Mostrar métricas de calidad agregadas
stats = calcular_estadisticas()
st.markdown("### 📊 Métricas de calidad")
st.write(stats)

# Mostrar gráficos si existe metrics.csv
if METRICS_FILE.exists():
    df = pd.read_csv(METRICS_FILE)

    # Gráfico 1: % preguntas sin respuesta vs con respuesta
    sin_res = df["sin_respuesta"].sum()
    con_res = len(df) - sin_res
    st.markdown("#### 📈 Distribución de respuestas")
    st.bar_chart(pd.DataFrame({"Respuestas": [con_res, sin_res]}, index=["Con respuesta", "Sin respuesta"]))

    # Gráfico 2: Feedback negativo vs positivo
    neg = df["feedback_negativo"].sum()
    pos = len(df) - neg
    st.markdown("#### 💬 Feedback de usuarios")
    st.bar_chart(pd.DataFrame({"Feedback": [pos, neg]}, index=["Positivo", "Negativo"]))

    # Gráfico 3: Tiempo de respuesta histórico
    st.markdown("#### ⏱️ Tiempo de respuesta por interacción")
    st.line_chart(df["tiempo_respuesta"])
