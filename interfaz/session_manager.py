import streamlit as st

def get_session():
    """Obtiene el historial de conversación desde el estado de sesión."""
    if "historial" not in st.session_state:
        st.session_state["historial"] = []
    return st.session_state["historial"]

def update_session(pregunta, respuesta, fuentes):
    """Agrega una nueva interacción al historial de conversación."""
    if "historial" not in st.session_state:
        st.session_state["historial"] = []
    st.session_state["historial"].append({
        "pregunta": pregunta,
        "respuesta": respuesta,
        "fuentes": fuentes
    })

