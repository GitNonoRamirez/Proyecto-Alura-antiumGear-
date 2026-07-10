import streamlit as st
import csv
import os

FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "feedback.csv")

def guardar_feedback(pregunta, respuesta, fuentes, tipo):
    """
    Guarda el feedback en un archivo CSV.
    """
    existe = os.path.isfile(FEEDBACK_FILE)
    with open(FEEDBACK_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        if not existe:
            writer.writerow(["pregunta", "respuesta", "fuentes", "feedback"])
        writer.writerow([pregunta, respuesta, ";".join(fuentes), tipo])

def mostrar_botones_feedback(pregunta, respuesta, fuentes, idx):
    """
    Muestra los botones de feedback y los bloquea apenas se vota.
    """
    key_feedback = f"feedback_{idx}"
    ya_voto = st.session_state.get(key_feedback)

    if ya_voto is not None:
        # Mostrar un caption opcional para indicar que ya se votó
        st.caption("👍 Voto registrado" if ya_voto == "positivo" else "👎 Voto registrado")
        return

    fb1, fb2 = st.columns([0.1, 0.1])
    with fb1:
        if st.button("👍", key=f"like_{idx}"):
            st.session_state[key_feedback] = "positivo"
            guardar_feedback(pregunta, respuesta, fuentes, "positivo")
            st.rerun()
    with fb2:
        if st.button("👎", key=f"dislike_{idx}"):
            st.session_state[key_feedback] = "negativo"
            guardar_feedback(pregunta, respuesta, fuentes, "negativo")
            st.rerun()
