import streamlit as st

def get_session():
    if "historial" not in st.session_state:
        st.session_state["historial"] = []
    return st.session_state["historial"]

def update_session(pregunta, respuesta, fuentes):
    if "historial" not in st.session_state:
        st.session_state["historial"] = []
    st.session_state["historial"].append({
        "pregunta": pregunta,
        "respuesta": respuesta,
        "fuentes": fuentes
    })

