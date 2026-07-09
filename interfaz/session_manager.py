import streamlit as st

def inicializar_historial():
    """
    Inicializa el historial de conversación en la sesión de Streamlit.
    """
    if "history" not in st.session_state:
        st.session_state["history"] = []

def agregar_interaccion(pregunta, respuesta, fuentes):
    """
    Agrega una interacción al historial de conversación.
    """
    st.session_state["history"].append({
        "pregunta": pregunta,
        "respuesta": respuesta,
        "fuentes": fuentes
    })

def obtener_historial():
    """
    Devuelve el historial completo de la sesión.
    """
    return st.session_state.get("history", [])
