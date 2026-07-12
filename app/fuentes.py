import streamlit as st

def mostrar_fuentes(fuentes):
    """
    Muestra las fuentes utilizadas en una respuesta dentro de la interfaz Streamlit.
    :param fuentes: Lista de nombres de documentos utilizados como fuente.
    """
    if fuentes:
        st.markdown("**📂 Fuentes utilizadas:**")
        for fuente in fuentes:
            st.markdown(f"- {fuente}")
    else:
        st.markdown("📂 No se identificaron fuentes para esta respuesta.")
