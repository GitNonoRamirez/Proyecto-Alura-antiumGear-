import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import google.genai as genai

# 📌 Cargar variables desde .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Configurar la API con la key
genai.configure(api_key=API_KEY)

CSV_PATH = "embeddings.csv"  # Ajusta al nombre de tu archivo de embeddings

def embed_text(texto: str):
    """
    Genera embeddings reales usando la API de Google Generative AI.
    """
    response = genai.embed_content(
        model="models/gemini-embedding-001",
        content=texto
    )
    return response['embedding']

def buscar_en_csv(pregunta: str):
    try:
        texto = pregunta.lower()

        # 🔎 Reembolsos / devoluciones
        if any(p in texto for p in [
            "devolver", "reembolso", "garantía", "cambio", "cambiar",
            "producto", "artículo", "audífonos", "teclado", "hardware"
        ]):
            return (
                "Puedes devolver o cambiar un producto dentro de 10 días corridos desde la recepción si está sin uso y en su empaque original. "
                "Además, cuentas con 6 meses de garantía legal en caso de fallas de fábrica.",
                ["Política de Reembolsos y Devoluciones – AntiumGear Ltda."]
            )

        # 🔎 Privacidad
        if any(p in texto for p in [
            "privacidad", "datos personales", "información", "tratamiento", "confidencialidad", "usuarios"
        ]):
            return (
                "Tus datos personales se tratan bajo principios de licitud, finalidad y seguridad. "
                "AntiumGear solo los usa para gestión de compras, soporte y cumplimiento legal, "
                "y nunca se comparten sin tu consentimiento.",
                ["Política de Privacidad – AntiumGear Ltda."]
            )

        # 🔎 Envíos
        if any(p in texto for p in [
            "envío", "despacho", "entrega", "courier", "tiempo de entrega", "transporte"
        ]):
            return (
                "Los envíos se procesan en 24 a 48 horas hábiles. "
                "El despacho estándar tarda de 1 a 3 días en la Región Metropolitana, "
                "2 a 5 días en regiones y hasta 10 días en zonas extremas.",
                ["Guía de Envíos y Entregas – AntiumGear Ltda."]
            )

        # 🔎 Términos y condiciones
        if any(p in texto for p in [
            "compra", "usuario", "contrato", "condiciones", "pago", "uso"
        ]):
            return (
                "El uso de la plataforma implica aceptar los términos y condiciones, "
                "que regulan la capacidad legal del usuario, el proceso de compra, "
                "los medios de pago y la resolución de controversias.",
                ["Términos y Condiciones – AntiumGear Ltda."]
            )

        # 🔎 Si no entra en ningún filtro → búsqueda normal con embeddings
        df = pd.read_csv(CSV_PATH, sep=";")
        pregunta_vec = embed_text(pregunta)
        embeddings = df["embedding_vector"].apply(lambda x: np.fromstring(x.strip("[]"), sep=" "))
        matriz = np.vstack(embeddings.values)

        num = np.dot(matriz, pregunta_vec)
        den = np.linalg.norm(matriz, axis=1) * np.linalg.norm(pregunta_vec)
        similitudes = num / den

        if similitudes.max() < 0.3:  
            # 📌 Fallback corporativo
            return (
                "Lo siento, no encontré una respuesta exacta en las políticas de AntiumGear. "
                "Puedes contactar a nuestro equipo en contacto@antiumgear.cl.",
                []
            )

        idx = np.argmax(similitudes)
        fragmento = df.iloc[idx]["texto_chunk"]
        fuente = df.iloc[idx]["documento_origen"]

        return fragmento, [fuente]

    except Exception:
        # 📌 Fallback genérico para preguntas fuera de contexto
        return (
            "Esa consulta no está relacionada con las políticas de AntiumGear. "
            "Si necesitas información sobre nuestros productos o servicios, puedes escribirnos a contacto@antiumgear.cl.",
            []
        )

# 🔎 Verificación rápida de la API
if __name__ == "__main__":
    try:
        prueba = embed_text("texto de prueba")
        print("✅ API key activa. Embedding generado:", prueba[:5])  # muestra los primeros 5 valores
    except Exception as e:
        print("❌ Error con la API key:", e)
