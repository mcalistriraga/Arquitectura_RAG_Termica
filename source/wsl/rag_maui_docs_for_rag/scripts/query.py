# =============================================================
# Proyecto:
# Arquitectura RAG local con supervisión térmica
#
# Archivo:
# query.py
#
# Versión:
# 1.6
#
# Fecha:
# Agosto de 2026
#
# Descripción:
# ------------
# Módulo principal del pipeline RAG.
#
# Coordina la ejecución completa del pipeline, desde la
# recepción de la consulta del usuario hasta la generación de
# la respuesta y el registro de observabilidad del proceso.
#
# Actúa como orquestador de las distintas etapas del sistema,
# manteniendo desacopladas la recuperación del conocimiento,
# la construcción del contexto, la inferencia mediante el LLM
# y el registro de métricas y depuración.
#
# Responsabilidades:
# ------------------
# - Recibir las consultas del usuario.
# - Gestionar la sesión de trabajo.
# - Detectar errores de compilación C# cuando existan.
# - Generar embeddings de la consulta mediante Ollama.
# - Recuperar conocimiento desde la base vectorial.
# - Recuperar información arquitectónica desde symbols.jsonl.
# - Construir el contexto RAG a partir de múltiples chunks.
# - Integrar el contexto simbólico al contexto recuperado.
# - Construir el contexto enviado al backend de inferencia.
# - Delegar la inferencia a llm_backend.py.
# - Registrar métricas y eventos mediante logger.py.
# - Facilitar mecanismos opcionales de observabilidad y
#   depuración del pipeline.
#
# Componentes utilizados:
# -----------------------
# Modelo de embeddings:
#     nomic-embed-text
#
# Backends disponibles:
#     LOCAL  -> Ollama
#     CLOUD  -> OpenRouter
#
# Modelos configurados:
#     DEBUG -> qwen2.5-coder:1.5b
#     ARCH  -> llama3.2:3b
#     DOCS  -> llama3.2:3b
#
# Modos de operación:
# -------------------
# 1. Depuración de código C# / .NET MAUI.
# 2. Consultas de arquitectura del sistema.
# 3. Generación de documentación técnica.
#
# Arquitectura general:
# ---------------------
#
#                 Usuario
#                    │
#                    ▼
#           Recepción de consulta
#                    │
#                    ▼
#          Detección de errores C#
#                    │
#                    ▼
#         Generación del embedding
#                    │
#                    ▼
#        Recuperación semántica (RAG)
#                    │
#                    ▼
#      Construcción del contexto RAG
#          ┌─────────┴─────────┐
#          ▼                   ▼
# Contexto recuperado   Contexto simbólico
#          └─────────┬─────────┘
#                    ▼
#      Construcción del prompt
#                    │
#                    ▼
#             llm_backend.py
#          ┌─────────┴─────────┐
#          ▼                   ▼
#      Ollama             OpenRouter
#          └─────────┬─────────┘
#                    ▼
#             Respuesta LLM
#                    │
#                    ▼
#     logger.py / Observabilidad
#
# Gestión de sesión:
# ------------------
# Cada consulta crea una nueva sesión lógica de ejecución.
#
# La sesión conserva:
#
# - modo operativo;
# - backend de inferencia;
# - modelo seleccionado;
# - métricas del pipeline.
#
# logger.py inicializa un nuevo registro para cada consulta y
# calcula automáticamente las métricas de rendimiento.
#
# Supervisión térmica:
# --------------------
# La protección térmica permanece completamente desacoplada
# del pipeline RAG.
#
# Es responsabilidad exclusiva de:
#
#     thermal_watchdog.py
#
# Dicho módulo supervisa continuamente el hardware y puede
# interrumpir la ejecución de query.py cuando se alcanzan
# condiciones térmicas críticas.
#
# Observabilidad y depuración:
# ----------------------------
# El módulo incorpora mecanismos opcionales de observabilidad
# controlados mediante banderas de configuración.
#
# DEBUG_RETRIEVAL
#     Registra score y origen de los chunks recuperados.
#
# DEBUG_CHUNKS
#     Visualiza y registra el contenido de los chunks
#     recuperados durante la búsqueda semántica.
#
# DEBUG_CONTEXT
#     Registra información del contexto construido y una
#     vista previa del contenido enviado al backend LLM.
#
# Estas capacidades permiten validar el funcionamiento del
# pipeline sin modificar su lógica principal.
#
# Cambios versión 1.6:
# --------------------
# - Se consolida la construcción explícita del contexto RAG.
# - El contexto enviado al LLM se construye a partir de los
#   chunks recuperados mediante búsqueda semántica.
# - Se incorpora recuperación de múltiples chunks mediante
#   TOP_K configurable.
# - Se amplían los mecanismos de observabilidad del pipeline:
#       * recuperación semántica;
#       * chunks recuperados;
#       * contexto construido.
# - Se mantienen desacopladas las responsabilidades entre
#   recuperación, construcción de contexto, inferencia,
#   observabilidad y supervisión térmica.
# - Se conserva la arquitectura híbrida LOCAL / CLOUD,
#   independiente del backend utilizado en cada sesión.
#
# Objetivo de la versión:
# -----------------------
# Consolidar la utilización efectiva del conocimiento
# recuperado por el pipeline RAG, mejorando la construcción
# del contexto enviado al modelo de lenguaje e incorporando
# capacidades de observabilidad que faciliten el análisis,
# validación y futura evolución de la arquitectura sin
# aumentar el acoplamiento entre sus componentes.
#
# =============================================================

import os
import json
import numpy as np
import requests
import re
import time
from datetime import datetime

from logger import (
    init_logger,
    log_step,
    log_debug,
)

from llm_backend import ask_llm_backend



# =========================
# CONFIGURACIÓN
# =========================

SLEEP_TIME = 0.0  # throttle opcional

EMBEDDINGS_FILE = "embeddings.jsonl"
SYMBOLS_FILE = "symbols.jsonl"

OLLAMA_CHAT_URL = "http://localhost:11434/api/generate"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

MODEL_DEBUG = "qwen2.5-coder:1.5b"
MODEL_ARCH = "llama3.2:3b"
MODEL_DOCS = "llama3.2:3b"

MODEL_EMBED = "nomic-embed-text"

TOP_K = 3  #prueba: se cambió de 1 a 3 el 31/7/2026
SIM_THRESHOLD = 0.25

# =========================
# DEPURACIÓN Y PRUEBAS
# =========================

DEBUG_CHUNKS = True

DEBUG_RETRIEVAL = True

DEBUG_CONTEXT = True



# =========================
# THROTTLE
# =========================

def throttle():			

     if SLEEP_TIME > 0:		
         time.sleep(SLEEP_TIME)	


# =========================
# LOAD SYMBOLS
# =========================

def load_symbols():

    symbols = []

    if not os.path.exists(SYMBOLS_FILE):
        return symbols

    with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:

        for line in f:

            try:
                symbols.append(json.loads(line))

            except:
                pass

    return symbols


def find_symbol_context(question, symbols):

    for s in symbols:

        for c in s.get("classes", []):

            if c.lower() in question.lower():
                return s

    return None


def build_symbol_context(symbol):

    if not symbol:
        return ""

    return f"""
ARCHITECTURE CONTEXT

FILE: {symbol.get('file')}
CLASSES: {symbol.get('classes')}
PROPERTIES: {symbol.get('properties')}
METHODS: {symbol.get('methods')}
IS_VIEWMODEL: {symbol.get('is_viewmodel')}
"""

# =========================
# ERROR DETECTION
# =========================

def is_compiler_error(text):

    return bool(re.search(r"\bCS\d+\b", text))


def extract_error_info(text):

    file_match = re.search(r"([\w\.-]+\.cs)", text)
    code_match = re.search(r"(CS\d+)", text)

    return {
        "file": file_match.group(1) if file_match else None,
        "code": code_match.group(1) if code_match else None,
        "raw": text
    }


# =========================
# CARGA DE EMBEDDINGS
# =========================

def load_embeddings():

    data = []

    if not os.path.exists(EMBEDDINGS_FILE):

        print("❌ No existe embeddings.jsonl")
        return data


    with open(
        EMBEDDINGS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            try:

                item = json.loads(line)

                if "embedding" in item and item["embedding"]:
                    data.append(item)

            except:

                pass


    return data



# =========================
# EMBEDDING
# =========================

def get_embedding(text):

    try:

        response = requests.post(

            OLLAMA_EMBED_URL,

            json={
                "model": MODEL_EMBED,
                "prompt": text
            },

            timeout=30
        )


        if response.status_code != 200:

            print(
                "❌ Error embedding:",
                response.text
            )

            return None


        return response.json().get(
            "embedding",
            None
        )


    except Exception as e:

        print(
            "❌ Error embedding request:",
            str(e)
        )

        return None



# =========================
# SEARCH
# =========================

def cosine(a, b):

    if a is None or b is None:

        return -1


    a = np.array(a)
    b = np.array(b)


    denom = (
        np.linalg.norm(a)
        *
        np.linalg.norm(b)
    )


    if denom == 0:

        return -1


    return np.dot(a, b) / denom



def search(
    query_embedding,
    data,
    k=TOP_K,
    file_filter=None
):

    scored = []


    for item in data:

        try:

            score = cosine(
                query_embedding,
                item["embedding"]
            )


            if score >= SIM_THRESHOLD:


                if (
                    file_filter
                    and file_filter not in item.get("file", "")
                ):

                    continue


                scored.append(
                    (
                        score,
                        item
                    )
                )


        except:

            pass


    scored.sort(
        reverse=True,
        key=lambda x: x[0]
    )


    return [
        {
            "score": score,
            "data": item
        }
        for score, item in scored[:k]
    ]



# =========================
# MAIN
# =========================

def main():

    print(
        "🧠 RAG + DEBUGGER + ARCHITECTURE MODE"
    )

    print(
        "💬 Escribe 'exit' para salir\n"
    )


    data = load_embeddings()

    symbols = load_symbols()


    print(
        f"📚 Embeddings: {len(data)}"
    )

    print(
        f"🏗 Symbols: {len(symbols)}\n"
    )


    if not data:

        print("❌ No embeddings")
        return



    # =========================
    # SELECCIÓN MODELO IA
    # =========================

    print(
        "=== MODO IA LOCAL ==="
    )

    print(
        "1. DEPURACIÓN"
    )

    print(
        "2. ARQUITECTURA"
    )

    print(
        "3. DOCUMENTACIÓN"
    )


    mode = input(
        "Selecciona modo: "
    )


    if mode == "1":

        selected_model = MODEL_DEBUG
        selected_mode = "DEBUG"


    elif mode == "2":

        selected_model = MODEL_ARCH
        selected_mode = "ARCH"


    else:

        selected_model = MODEL_DOCS
        selected_mode = "DOCS"



    # =========================
    # SESIÓN ACTUAL
    # =========================

    session = {

        "mode": selected_mode,

        "backend": "cloud",

        "model":
            "openai/gpt-4.1-mini"
    }



    print(
        "\n=============================="
    )

    print(
        "Sesión actual"
    )

    print(
        "=============================="
    )

    print(
        f"Modo IA : {session['mode']}"
    )

    print(
        f"Backend : {session['backend']}"
    )

    print(
        f"Modelo  : {session['model']}"
    )

    print(
        "==============================\n"
    )



    # =========================
    # LOOP
    # =========================

    while True:


        user_input = input(
            "💬 Input: "
        )


        if user_input.lower() in [
            "exit",
            "quit"
        ]:

            break



        # =========================
        # LOGGER INIT
        # =========================

        init_logger(

            mode=session["mode"],

            model_chat=session["model"],

            model_embedding=MODEL_EMBED,

            backend=session["backend"],

            question=user_input
        )


        log_step(
            "SESSION_START"
        )


        log_step(
            "MODE_SELECTED",
            session["mode"]
        )


        log_step(
            "INPUT_RECEIVED",
            session["mode"]
        )



        error_info = None

        file_filter = None



        if is_compiler_error(user_input):


            error_info = extract_error_info(
                user_input
            )


            file_filter = error_info.get(
                "file"
            )


            query_text = (
                user_input
                +
                " "
                +
                (file_filter or "")
            )


            log_step(
                "COMPILER_ERROR",
                session["mode"]
            )


        else:

            query_text = user_input




        # =========================
        # EMBEDDING
        # =========================

        log_step(
            "EMBEDDING_START",
            session["mode"]
        )


        q_emb = get_embedding(
            query_text
        )


        if q_emb is None:

            log_step(
                "EMBEDDING_FAIL",
                session["mode"]
            )

            continue



        log_step(
            "EMBEDDING_OK",
            session["mode"]
        )



        # =========================
        # SEARCH
        # =========================

        log_step(
            "SEARCH_START",
            session["mode"]
        )

        results = search(
            q_emb,
            data,
            TOP_K,
            file_filter
        )


        if DEBUG_RETRIEVAL:

            retrieval_info = ""

            for i, result in enumerate(results, 1):

                item = result["data"]

                retrieval_info += (
                    f"""
Chunk:
{i}

Score:
{result['score']:.4f}

File:
{item.get('file')}

"""
                )


            log_debug(
                "RETRIEVAL METADATA",
                retrieval_info
            )



        log_step(
            "SEARCH_DONE",
            session["mode"]
        )


        if DEBUG_CHUNKS:

            print("\n===== CHUNKS RECUPERADOS =====")

            debug_text = ""

            for i, result in enumerate(results, 1):

                item = result["data"]

                chunk = (
                    f"\nChunk {i}\n"
                    f"Score : {result['score']:.4f}\n"
                    f"Archivo : {item.get('file')}\n"
                    f"Contenido:\n{item.get('content')}\n"
                )

                print(chunk)

                debug_text += chunk


            log_debug(
                "CHUNKS RECUPERADOS",
                debug_text
            )



        # =========================
        # BUILD CONTEXT FROM RAG
        # =========================        
        #
        # Los resultados obtenidos mediante búsqueda
        # semántica contienen los chunks relevantes
        # del proyecto.
        #
        # En esta versión se incorpora nuevamente
        # este contenido al contexto enviado al LLM.
        #
        # El contexto construido representa la
        # información recuperada que será utilizada
        # posteriormente por el backend LLM.
        #
        # =========================


        context = ""

        for result in results:

            item = result["data"]

            context += (
                "\n\n"
                +
                item.get(
                    "content",
                    ""
                )
            )


        if DEBUG_CONTEXT:

            log_debug(
                "RAG CONTEXT METADATA",
                f"""
CHUNKS_USED:
{len(results)}

CONTEXT_CHARACTERS:
{len(context)}

TOP_K:
{TOP_K}

SIM_THRESHOLD:
{SIM_THRESHOLD}
"""
            )


            log_debug(
                "RAG CONTEXT PREVIEW",
                context[:2000]
            )



        if file_filter:

            context = (

                f"[FILE FILTER ACTIVE: {file_filter}]\n"

                +

                context

            )



        # =========================
        # SYMBOL CONTEXT
        # =========================

        symbol = find_symbol_context(
            user_input,
            symbols
        )


        symbol_context = build_symbol_context(
            symbol
        )



        # =========================
        # LLM
        # =========================

        log_step(
            "LLM_START",
            session["mode"]
        )


        answer = ask_llm_backend(

            context,

            user_input,

            session["model"],

            error_info,

            symbol_context,

            backend=session["backend"].lower()

        )


        log_step(
            "LLM_DONE",
            session["mode"]
        )



        print(
            "\n🤖 Respuesta:\n"
        )


        print(answer)


        print(
            "\n"
            +
            "=" * 60
            +
            "\n"
        )


        log_step(
            "ANSWER_PRINTED",
            session["mode"]
        )



if __name__ == "__main__":

    main()
