import streamlit as st
import csv
import os

FEEDBACK_FILE = "interfaz/feedback.csv"

def guardar_feedback(pregunta, respuesta, fuentes, tipo):
    """
    Guarda el feedback en un archivo CSV.
    :param pregunta: Texto de la pregunta del usuario
    :param respuesta: Texto de la respuesta del agente
    :param fuentes: Lista de fuentes utilizadas
    :param tipo: 'positivo' o 'negativo'
    """
    existe = os.path.isfile(FEEDBACK_FILE)
    with open(FEEDBACK_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not existe:
            writer.writerow(["pregunta", "respuesta", "fuentes", "feedback"])
        writer.writerow([pregunta, respuesta, ", ".join(fuentes), tipo])

def mostrar_botones_feedback(pregunta, respuesta, fuentes, idx):
    """
    Muestra botones de feedback y guarda la selección.
    """
    col1, col2 = st.columns([0.1, 0.1])
    with col1:
        if st.button("👍", key=f"pos_{idx}"):
            guardar_feedback(pregunta, respuesta, fuentes, "positivo")
            st.success("Feedback positivo registrado.")
    with col2:
        if st.button("👎", key=f"neg_{idx}"):
            guardar_feedback(pregunta, respuesta, fuentes, "negativo")
            st.error("Feedback negativo registrado.")
