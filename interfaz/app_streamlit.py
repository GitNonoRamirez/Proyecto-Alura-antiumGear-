import streamlit as st
import os
from session_manager import get_session, update_session
from fuentes import mostrar_fuentes
from feedback import mostrar_botones_feedback
from buscador import buscar_en_csv   # ✅ usamos nuestro buscador con CSV

st.set_page_config(page_title="Agente IA AntiumGear", layout="wide")

col1, col2 = st.columns([1, 2])

with col1:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    fondo_path = os.path.join(BASE_DIR, "..", "assets", "logo_fondo_gamer.png")
    if os.path.exists(fondo_path):
        st.image(fondo_path, use_container_width=True)
    else:
        st.warning("No se encontró la imagen del logo con fondo gamer.")

with col2:
    st.markdown("## 🤖 Chat AntiumGear")
    st.info("Estás conversando con un agente de IA que responde usando documentos oficiales de AntiumGear.")

    session = get_session()
    historial = st.container(height=480)

    for idx, item in enumerate(session):
        with historial.chat_message("user"):
            st.write(item["pregunta"])
        with historial.chat_message("assistant"):
            st.write(item["respuesta"])
            if item["fuentes"]:
                mostrar_fuentes(item["fuentes"])
            mostrar_botones_feedback(item["pregunta"], item["respuesta"], item["fuentes"], idx)

    pregunta = st.chat_input("Escribe tu mensaje aquí...")
    if pregunta:
        if pregunta.lower() in ["hola", "buenas", "hi"]:
            respuesta, fuentes = "¡Hola! ¿En qué puedo ayudarte?", []
        else:
            # ✅ Buscar en CSV maestro
            respuesta, fuentes = buscar_en_csv(pregunta)

        update_session(pregunta, respuesta, fuentes)
        st.rerun()
