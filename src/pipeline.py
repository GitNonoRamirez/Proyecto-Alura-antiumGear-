# pipeline.py
# Flujo principal del agente: búsqueda → generación → validación → fallback con área responsable + formato final

import os

UMBRAL_CONFIANZA = 0.75

FALLBACK = "Lo siento, no tengo la respuesta a tu consulta. Nuestro equipo puede ayudarte si nos contactas en contacto@antiumgear.cl."

# Mapeo de documentos a áreas responsables
AREAS_RESPONSABLES = {
    "Política de Privacidad": "Área Legal",
    "Términos y Condiciones": "Área Legal",
    "Reembolsos y Devoluciones": "Área Finanzas",
    "Guía de Envíos": "Área Operaciones",
    "Preguntas Frecuentes (FAQ)": "Atención al Cliente"
}

def filtrar_fragmentos(resultados):
    """
    Filtra los fragmentos recuperados según el umbral de confianza.
    Cada resultado debe tener un campo 'score' y 'texto'.
    """
    relevantes = [r for r in resultados if r['score'] >= UMBRAL_CONFIANZA]
    return relevantes

def validar_consistencia(respuesta, fragmentos):
    """
    Verifica que la respuesta esté respaldada por al menos uno de los fragmentos recuperados.
    """
    for frag in fragmentos:
        if frag['texto'].lower() in respuesta.lower():
            return True
    return False

def obtener_area_responsable(fragmentos):
    """
    Determina el área responsable según la fuente del fragmento.
    """
    for frag in fragmentos:
        doc = frag.get("documento")
        if doc in AREAS_RESPONSABLES:
            return AREAS_RESPONSABLES[doc]
    return None

def aplicar_formato_salida(respuesta, referencias):
    """
    Carga la plantilla formato_base.md y reemplaza los campos.
    """
    ruta_template = os.path.join("prompts", "templates_salida", "formato_base.md")
    with open(ruta_template, "r", encoding="utf-8") as f:
        template = f.read()

    salida = template.replace("{respuesta_resumen}", respuesta)
    salida = salida.replace("{referencias_documentos}", ", ".join(referencias) if referencias else "Ninguna referencia disponible")

    return salida

def flujo_agente(pregunta):
    """
    Orquesta el flujo completo:
    1. Recupera fragmentos con FAISS (busqueda_vectorial).
    2. Filtra por umbral de confianza.
    3. Genera la respuesta con el prompt.
    4. Valida consistencia.
    5. Devuelve respuesta final o fallback con área responsable en formato estructurado.
    """
    # Paso 1: búsqueda vectorial
    resultados = busqueda_vectorial(pregunta)  # <-- tu función en buscar_faiss.py

    # Paso 2: aplicar umbral de confianza
    fragmentos = filtrar_fragmentos(resultados)

    if not fragmentos:
        return aplicar_formato_salida(FALLBACK, [])

    # Paso 3: generar respuesta con el modelo
    prompt = construir_prompt(pregunta, fragmentos)  # <-- usa prompt_base.md
    respuesta = generar_respuesta(prompt, fragmentos)

    # Paso 4: validar consistencia
    if not validar_consistencia(respuesta, fragmentos):
        area = obtener_area_responsable(fragmentos)
        if area:
            respuesta_final = f"Lo siento, no tengo la respuesta a tu consulta. Este tema corresponde al {area}. Nuestro equipo puede ayudarte si nos contactas en contacto@antiumgear.cl."
        else:
            respuesta_final = FALLBACK
        referencias = [frag["documento"] for frag in fragmentos]
        return aplicar_formato_salida(respuesta_final, referencias)

    # Si la respuesta es válida
    referencias = [frag["documento"] for frag in fragmentos]
    return aplicar_formato_salida(respuesta, referencias)


