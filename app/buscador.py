import os
import re
import json
import hashlib
import unicodedata
import logging
import traceback
from typing import List, Dict, Tuple, Optional
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Configuración de Logging para producción y diagnóstico en consola
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger("BuscadorDocumentos")
MENSAJE_SIN_RESPUESTA = "Lo siento, no tengo la respuesta a tu consulta. Nuestro equipo puede ayudarte si nos contactas en contacto@antiumgear.cl."
FRASE_CLAVE_SIN_RESPUESTA = "no tengo la respuesta a tu consulta"

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

print("\n" + "="*80)
print(" DIAGNÓSTICO DE INICIALIZACIÓN ")
print("="*80)

if not GOOGLE_API_KEY:
    print("❌ ERROR: No se encontró la variable de entorno GOOGLE_API_KEY.")
    print("   Por favor, verifica que tu archivo .env exista en la raíz con: GOOGLE_API_KEY=tu_api_key")
else:
    print("✅ Variable GOOGLE_API_KEY detectada correctamente.")
    genai.configure(api_key=GOOGLE_API_KEY)

# Configuración de rutas relativas basadas en la ubicación de buscador.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "documentos"))
PROMPT_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", "prompts", "prompt_base.md"))
CACHE_PATH = os.path.normpath(os.path.join(BASE_DIR, "embeddings_cache.json"))

print(f"📁 Directorio de Documentos: {DOCS_DIR}")
print(f"📄 Ruta del Prompt Base: {PROMPT_PATH}")
print(f"💾 Ruta del Caché: {CACHE_PATH}")
print("="*80 + "\n")

if os.path.exists(CACHE_PATH):
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            embeddings_cache = json.load(f)
        print(f"ℹ️ Caché de embeddings cargada exitosamente ({len(embeddings_cache)} vectores persistidos).")
    except Exception as e:
        print(f"⚠️ No se pudo cargar la caché de embeddings: {e}")
        embeddings_cache = {}
else:
    embeddings_cache = {}

def guardar_cache():
    """Guarda el estado actual de la caché local de embeddings en disco"""
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(embeddings_cache, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.warning(f"No se pudo guardar la caché de embeddings: {e}")

def normalizar(texto: str) -> str:
    """Convierte texto a minúsculas, remueve acentos y normaliza espacios en blanco"""
    if not texto:
        return ""
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    # Limpiamos caracteres de control y saltos de línea molestos para una búsqueda léxica robusta
    texto = re.sub(r'[\r\n\t]+', ' ', texto)
    return re.sub(r'\s+', ' ', texto).strip()

def obtener_hash(texto: str) -> str:
    """Genera un hash MD5 único para almacenar en la caché de embeddings"""
    return hashlib.md5(texto.encode("utf-8")).hexdigest()

def dividir_en_chunks(texto: str, max_palabras: int = 1000, solapamiento: int = 200) -> List[str]:
    """Divide un bloque grande de texto en chunks manejables preservando coherencia"""
    palabras = texto.split()
    chunks = []
    i = 0
    while i < len(palabras):
        chunk = palabras[i : i + max_palabras]
        chunks.append(" ".join(chunk))
        if i + max_palabras >= len(palabras):
            break
        i += max_palabras - solapamiento
    return chunks

def embed_text(texto: str, task_type: str = "RETRIEVAL_DOCUMENT") -> np.ndarray:
    """Genera vector de embedding llamando a la API de Google con soporte de caché local y fallback de 2026"""
    key = obtener_hash(f"{task_type}:{texto}")
    
    if key in embeddings_cache:
        # IMPORTANTE: Convertimos siempre a numpy array para evitar errores de tipo en operaciones de álgebra
        return np.array(embeddings_cache[key])
        
    # Modelos de embedding en orden de preferencia para 2026
    modelos_embedding = [
        "models/gemini-embedding-2",  # Modelo multimodal de última generación (Abril 2026)
        "models/gemini-embedding-001" # Modelo clásico (Depreciación Julio 2026)
    ]
    
    for model_name in modelos_embedding:
        try:
            # Recortamos el texto por seguridad de límites de tokens de la API
            texto_seguro = texto[:4000]
            result = genai.embed_content(
                model=model_name, 
                content=texto_seguro,
                task_type=task_type
            )
            vec = result["embedding"]
            
            # Almacenamos en el diccionario global y guardamos en persistencia
            embeddings_cache[key] = vec
            guardar_cache()
            
            return np.array(vec)
        except Exception as e:
            logger.debug(f"Fallo embedding con modelo {model_name}: {e}")
            continue
            
    print("⚠️ [ERROR EN EMBED_TEXT] Falló la generación de embedding con todos los modelos disponibles.")
    return np.zeros(768)

def cargar_documentos() -> List[Dict]:
    """Carga los documentos PDF, extrae su texto, los segmenta y asocia su metadato fuente y texto completo"""
    documentos = []
    if not os.path.exists(DOCS_DIR):
        print(f"❌ ERROR: El directorio de documentos especificado no existe: {DOCS_DIR}")
        return documentos

    archivos = os.listdir(DOCS_DIR)
    pdf_count = 0
    
    for archivo in archivos:
        # Ignoramos archivos de preguntas frecuentes (FAQs) y no PDFs
        if archivo.endswith(".pdf") and "faq" not in archivo.lower():
            pdf_count += 1
            ruta = os.path.join(DOCS_DIR, archivo)
            try:
                reader = PdfReader(ruta)
                texto_total = ""
                paginas_leidas = 0
                for num_pag, page in enumerate(reader.pages):
                    texto_pag = page.extract_text()
                    if texto_pag:
                        texto_total += f"\n[Pág. {num_pag + 1}] " + texto_pag
                        paginas_leidas += 1
                
                texto_total = texto_total.strip()
                caracteres_extraidos = len(texto_total)
                
                print(f"📄 Archivo: {archivo}")
                print(f"   ├─ Páginas con texto: {paginas_leidas} de {len(reader.pages)}")
                print(f"   ├─ Caracteres extraídos: {caracteres_extraidos}")
                
                if caracteres_extraidos == 0:
                    print("   ⚠️ ADVERTENCIA: No se extrajo texto de este PDF. ¿Es un PDF escaneado (imagen)?")
                else:
                    # Mostrar vista previa de los primeros 100 caracteres extraídos
                    preview = texto_total[:120].replace('\n', ' ')
                    print(f"   ├─ Vista previa texto: \"{preview}...\"")
                
                if texto_total:
                    # Dividimos en chunks para la búsqueda semántica eficiente
                    chunks = dividir_en_chunks(texto_total)
                    print(f"   └─ Segmentado en {len(chunks)} chunks.")
                    for chunk in chunks:
                        documentos.append({
                            "texto": chunk,                  # El trozo para vectorizar/buscar
                            "texto_completo": texto_total,   # El PDF completo para que la IA lea sin restricciones
                            "fuente": archivo
                        })
            except Exception as e:
                print(f"❌ Error crítico procesando el archivo {archivo}: {e}")
                
    if pdf_count == 0:
        print("⚠️ ADVERTENCIA: No se encontraron archivos PDF elegibles en la carpeta de documentos.")
        
    return documentos

def obtener_modelo_activo() -> str:
    """Busca de manera dinámica el mejor modelo de texto soportado por la cuenta y versión del SDK en 2026"""
    modelos_preferidos = [
        "models/gemini-3.5-flash",       # GA desde Mayo 2026 - Excelente para RAG y agentes
        "models/gemini-3.1-flash-lite",  # GA desde Mayo 2026 - Alternativa ultra-rápida y económica
        "models/gemini-2.5-flash",       # Retirándose gradualmente en Julio 2026
        "models/gemini-1.5-flash",       # Retirándose gradualmente
        "models/gemini-2.5-pro",
        "models/gemini-pro"
    ]
    try:
        modelos_disponibles = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelos_disponibles.append(m.name)
        
        print(f"📋 Modelos compatibles detectados en tu SDK y API Key: {modelos_disponibles}")
        
        # 1. Buscamos el mejor de nuestra lista de preferencia
        for pref in modelos_preferidos:
            if pref in modelos_disponibles:
                print(f"🎯 Seleccionado automáticamente (Preferido): {pref}")
                return pref
            # Caso de que no use prefijo 'models/' en algunas configuraciones locales
            pref_sin = pref.replace("models/", "")
            if pref_sin in modelos_disponibles:
                print(f"🎯 Seleccionado automáticamente (Preferido): {pref_sin}")
                return pref_sin
                
        # 2. Si ninguno de nuestros preferidos está pero hay otros, usamos el primero que sea útil para chat/texto
        if modelos_disponibles:
            for m in modelos_disponibles:
                if "flash" in m or "pro" in m:
                    print(f"🔄 Seleccionado automáticamente (Fallback Inteligente): {m}")
                    return m
            print(f"🔄 Seleccionado automáticamente (Último Recurso): {modelos_disponibles[0]}")
            return modelos_disponibles[0]
            
    except Exception as e:
        print(f"⚠️ Error al listar modelos desde el servidor de Google: {e}")
        
    # Fallback definitivo en caso de error de red o de list_models (privilegios bloqueados de API key)
    # En julio de 2026, usamos gemini-3.5-flash por defecto en lugar del antiguo gemini-pro que da 404
    print("⚠️ Usando fallback forzado: models/gemini-3.5-flash")
    return "models/gemini-3.5-flash"

def generar_respuesta_con_ia(pregunta: str, fragmento: str, fuente: str) -> str:
    """Ensambla el prompt de manera segura usando reemplazos y genera la respuesta mediante un bucle de modelos autocurativo"""
    try:
        if os.path.exists(PROMPT_PATH):
            with open(PROMPT_PATH, "r", encoding="utf-8") as f:
                prompt_base = f.read()
            print("📖 Prompt base cargado con éxito desde el archivo markdown.")
        else:
            print("⚠️ Prompt base no encontrado. Usando plantilla de contingencia.")
            prompt_base = (
                "Eres el asistente de soporte técnico de Antium Gear. Responde "
                "únicamente basándote en el contexto proveído.\n\n"
                "Contexto:\n{fragmento_1}\n\nDocumento Fuente: {nombre_documento}\n\nPregunta: {pregunta}"
            )
    except Exception as e:
        print(f"❌ Error al intentar abrir prompt_base.md: {e}")
        prompt_base = "Contexto:\n{fragmento_1}\nPregunta: {pregunta}"

    # Reemplazo seguro para evitar fallos por caracteres de llaves en el Markdown
    prompt = prompt_base.replace("{pregunta}", pregunta)\
                        .replace("{fragmento_1}", fragmento)\
                        .replace("{nombre_documento}", fuente)\
                        .replace("{sección}", "N/A")\
                        .replace("{fragmento_2}", "")

    print("\n" + "="*50)
    print(" PROMPT ENVIADO A GEMINI ")
    print("="*50)
    # Mostramos los primeros 400 caracteres del prompt para depuración
    print(prompt[:400] + "\n... [Resto del prompt omitido en el log] ...")
    print("="*50)

    # Obtenemos dinámicamente el modelo que tu entorno soporta
    model_name = obtener_modelo_activo()
    
    try:
        print(f"🔄 Intentando generar contenido con el modelo: {model_name}...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        print(f"✅ Respuesta recibida exitosamente desde {model_name}!")
        return response.text.strip()
    except Exception as e:
        print(f"\n❌ [ERROR CRÍTICO: EL MODELO '{model_name}' FALLÓ EN LA API DE GEMINI]")
        print("-" * 50)
        traceback.print_exc()
        print("-" * 50)

        # Bucle de autocuración extrema en caso de fallo 404 del modelo seleccionado
        fallbacks = ["models/gemini-3.5-flash", "models/gemini-3.1-flash-lite", "models/gemini-2.5-flash", "models/gemini-1.5-flash"]
        for fallback_model in fallbacks:
            if fallback_model == model_name:
                continue
            try:
                print(f"🔄 [AUTOCURACIÓN] Probando modelo de respaldo: {fallback_model}...")
                model = genai.GenerativeModel(fallback_model)
                response = model.generate_content(prompt)
                print(f"✅ ¡ÉXITO! Respuesta recuperada usando {fallback_model}")
                return response.text.strip()
            except Exception:
                continue

    return MENSAJE_SIN_RESPUESTA

def buscar_en_docs(pregunta: str) -> Tuple[str, List[str]]:
    """Busca en los documentos utilizando una combinación inteligente de coincidencia léxica y semántica"""
    print("\n" + "#"*80)
    print(f" PROCESANDO PREGUNTA: '{pregunta}'")
    print("#"*80)
    
    documentos = cargar_documentos()
    if not documentos:
        return "⚠️ No se encontraron documentos PDF en la carpeta.", []

    pregunta_norm = normalizar(pregunta)

    # Mapeo estructurado para clasificar los documentos por palabras clave y nombres de archivo en singular
    temas = {
        "reembolsos": {
            "keywords": ["reembolso", "devoluc", "garantia", "dias", "cambio", "devolver", "plazo", "retorno"],
            "archivo": "reembolso"
        },
        "privacidad": {
            "keywords": ["privacidad", "datos", "informacion", "tratamiento", "personales", "seguridad"],
            "archivo": "privacidad"
        },
        "envios": {
            "keywords": ["envio", "entrega", "empresa", "transporte", "despacho", "starken", "chilexpress", "correos"],
            "archivo": "envio"
        },
        "terminos": {
            "keywords": ["pago", "compra", "usuario", "condiciones", "contrato", "webpay", "debito", "credito"],
            "archivo": "termino"
        }
    }

    mejor_score = 0
    mejor_texto_completo = None
    mejor_fuente = None

    print("\n🔍 CAPA 1: Búsqueda Léxica con Scoring Ponderado...")
    for doc in documentos:
        texto_norm = normalizar(doc["texto"])
        fuente_norm = normalizar(doc["fuente"])
        score = 0

        # Evaluamos la coincidencia con cada uno de los temas predefinidos
        for tema, datos in temas.items():
            nombre_archivo_clave = datos["archivo"]
            
            # Verificamos si el archivo físico corresponde legítimamente a este tema
            es_archivo_del_tema = nombre_archivo_clave in fuente_norm
            
            for kw in datos["keywords"]:
                if kw in pregunta_norm and kw in texto_norm:
                    if es_archivo_del_tema:
                        # Prioridad alta si coincide la palabra clave y el archivo destino es el correcto
                        score += 5
                    else:
                        # Puntuación muy baja para evitar falsos positivos de cruce de información entre PDFs
                        score += 0.5
        
        # Puntuación adicional de coincidencia de palabras generales no de stopwords
        palabras_pregunta = [w for w in pregunta_norm.split() if len(w) > 3]
        for w in palabras_pregunta:
            if w in texto_norm:
                score += 1

        if score > mejor_score:
            mejor_score = score
            mejor_texto_completo = doc["texto_completo"] # Parent Retrieval: Guardamos el documento completo del PDF
            mejor_fuente = doc["fuente"]

    # Si encontramos una alta coincidencia léxica coherente (Score mínimo aceptable = 5)
    if mejor_score >= 5 and mejor_texto_completo:
        print(f"🎯 Coincidencia Léxica Exitosa en: '{mejor_fuente}' (Score obtenido: {mejor_score})")
        respuesta_final = generar_respuesta_con_ia(pregunta, mejor_texto_completo, mejor_fuente)
        return respuesta_final, [] if FRASE_CLAVE_SIN_RESPUESTA in respuesta_final.lower() else [mejor_fuente]


    print(f"⚠️ Baja coincidencia léxica (Mejor score: {mejor_score}). Pasando a Búsqueda Semántica...")
    
    pregunta_vec = embed_text(pregunta, task_type="RETRIEVAL_QUERY")
    if np.linalg.norm(pregunta_vec) == 0:
        return "Lo siento, ocurrió un problema técnico al analizar tu consulta.", []

    mejor_sim = -1.0
    mejor_texto_completo = None
    mejor_fuente = None
    
    for doc in documentos:
        vec = embed_text(doc["texto"], task_type="RETRIEVAL_DOCUMENT")
        norm_vec = np.linalg.norm(vec)
        
        if norm_vec == 0:
            continue
            
        # Similitud Coseno
        sim = np.dot(pregunta_vec, vec) / (np.linalg.norm(pregunta_vec) * norm_vec)
        
        if sim > mejor_sim:
            mejor_sim = sim
            mejor_texto_completo = doc["texto_completo"] # Parent Document Retrieval
            mejor_fuente = doc["fuente"]

    # Umbral de confianza estricto para evitar alucinaciones en preguntas fuera de contexto
    UMBRAL_MINIMO = 0.55
    print(f"📊 Mejor Similitud Semántica calculada: {mejor_sim:.4f} en '{mejor_fuente}'")
    
    if mejor_texto_completo and mejor_sim >= UMBRAL_MINIMO:
        print(f"🎯 Coincidencia Semántica Exitosa en: '{mejor_fuente}'")
        respuesta_final = generar_respuesta_con_ia(pregunta, mejor_texto_completo, mejor_fuente)
        return respuesta_final, [] if FRASE_CLAVE_SIN_RESPUESTA in respuesta_final.lower() else [mejor_fuente]

    print(f"❌ Sin coincidencias fiables (Similitud {mejor_sim:.4f} inferior al umbral de {UMBRAL_MINIMO})")
    return MENSAJE_SIN_RESPUESTA, []

if __name__ == "__main__":
    print("\n" + "="*80)
    print(" INICIANDO TEST DEL BUSCADOR DE DOCUMENTOS CON PARENT RETRIEVAL ")
    print("="*80)
    
    preguntas_test = [
        "¿Cuántos días tengo para devolver un producto?"
    ]
    
    for p in preguntas_test:
        respuesta, fuentes = buscar_en_docs(p)
        print("\n" + "🏁 RESPUESTA FINAL OBTENIDA:")
        print(respuesta)
        print(f"📂 Fuentes utilizadas: {fuentes}")
        print("-" * 80)