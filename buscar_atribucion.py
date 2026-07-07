import pandas as pd

# Ruta al CSV con embeddings y metadatos
csv_path = r"C:\Users\ramir\Proyecto-Alura-antiumGear-\documentos\documentos_metadatos\metadatos_completo.csv"
df = pd.read_csv(csv_path, encoding="utf-8")

# Función segura para obtener fragmento
def obtener_fragmento(df, documento):
    fila = df.loc[df["documento_origen.txt"] == documento, "texto_chunk"]
    if not fila.empty:
        valor = fila.values[0]
        if pd.isna(valor) or valor == "N/A":
            return "N/A"
        return str(valor)
    return "N/A"

# Simulación de resultados (ejemplo, normalmente vendrían de FAISS + reranking)
resultados = [
    {
        "documento": "Terminos_Condiciones_AntiumGear.txt",
        "categoria": "Términos y Condiciones",
        "responsable": "Área Legal",
        "score": -0.0096,
        "texto_chunk": obtener_fragmento(df, "Terminos_Condiciones_AntiumGear.txt")
    },
    {
        "documento": "Politica_Reembolsos_Devoluciones_AntiumGear.txt",
        "categoria": "Reembolsos y Devoluciones",
        "responsable": "Área Finanzas",
        "score": -0.0208,
        "texto_chunk": obtener_fragmento(df, "Politica_Reembolsos_Devoluciones_AntiumGear.txt")
    },
    {
        "documento": "Guia_Envios_Entregas_AntiumGear.txt",
        "categoria": "Envíos y Entregas",
        "responsable": "Área Operaciones",
        "score": 0.0007,
        "texto_chunk": obtener_fragmento(df, "Guia_Envios_Entregas_AntiumGear.txt")
    }
]

# Mostrar resultados
for r in resultados:
    print(f"\n📄 Documento: {r['documento']}")
    print(f"📂 Categoría: {r['categoria']}")
    print(f"👤 Responsable: {r['responsable']}")
    print(f"⭐ Score: {r['score']:.4f}")
    
    fragmento = str(r.get("texto_chunk", "N/A"))
    print(f"📝 Fragmento: {fragmento[:200]}...")
