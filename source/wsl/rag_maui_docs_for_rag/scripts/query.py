# =============================================================
# Proyecto:
# Arquitectura RAG local con supervisión térmica
#
# Archivo:
# query.py
#
# Versión:
# 1.4
#
# Fecha:
# 24 de Julio de 2026
#
# Descripción:
# ------------
# Módulo principal del pipeline RAG.
#
# Coordina el flujo completo de una consulta desde que el
# usuario introduce una pregunta hasta que la respuesta es
# generada por el backend de inferencia seleccionado.
#
# Este módulo constituye el núcleo del sistema y mantiene
# desacopladas las etapas de recuperación de conocimiento,
# generación de respuestas y registro de métricas.
#
# Responsabilidades:
# ------------------
# - Recibir las consultas del usuario.
# - Gestionar la sesión de trabajo.
# - Detectar errores de compilación C# cuando existan.
# - Generar embeddings mediante Ollama.
# - Recuperar contexto desde la base vectorial.
# - Recuperar información arquitectónica mediante symbols.jsonl.
# - Construir el contexto enviado al LLM.
# - Delegar la inferencia a llm_backend.py.
# - Registrar la ejecución mediante logger.py.
#
# Componentes utilizados:
# -----------------------
# Embeddings:
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
#                  Usuario
#                     │
#                     ▼
#              Recepción pregunta
#                     │
#                     ▼
#          Detección de errores C#
#                     │
#                     ▼
#           Embedding de consulta
#                     │
#                     ▼
#        Recuperación semántica (RAG)
#                     │
#                     ▼
#      Recuperación de contexto simbólico
#                     │
#                     ▼
#             Construcción del prompt
#                     │
#                     ▼
#             llm_backend.py
#          ┌──────────┴──────────┐
#          │                     │
#          ▼                     ▼
#      Ollama               OpenRouter
#          │                     │
#          └──────────┬──────────┘
#                     ▼
#              Respuesta LLM
#                     │
#                     ▼
#             Registro en logger.py
#
# Gestión de sesión:
# ------------------
# Cada consulta del usuario crea una nueva sesión lógica de
# ejecución. La sesión conserva:
#
# - modo operativo;
# - backend de inferencia;
# - modelo seleccionado;
# - métricas de ejecución.
#
# El registro asociado a la sesión se inicializa para cada
# consulta mediante logger.py.
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
# Cambios versión 1.4:
# --------------------
# - Se consolida el funcionamiento del backend híbrido
#   LOCAL / CLOUD.
# - La sesión de trabajo pasa a inicializarse para cada
#   consulta realizada por el usuario.
# - logger.py registra una sesión independiente por consulta,
#   incorporando métricas de rendimiento del pipeline.
# - Se mantiene completamente local la recuperación RAG,
#   delegando únicamente la inferencia al backend seleccionado.
# - Se mejora la separación de responsabilidades entre
#   query.py, llm_backend.py, logger.py y
#   thermal_watchdog.py.
#
# Objetivo de la versión:
# -----------------------
# Consolidar una arquitectura híbrida desacoplada en la que
# la recuperación del conocimiento permanezca local mientras
# la generación de respuestas pueda ejecutarse mediante
# distintos proveedores de inferencia sin modificar el
# núcleo del pipeline RAG.
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

TOP_K = 1
SIM_THRESHOLD = 0.25


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

    with open(EMBEDDINGS_FILE, "r", encoding="utf-8") as f:
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
            print("❌ Error embedding:", response.text)
            return None

        return response.json().get("embedding", None)

    except Exception as e:
        print("❌ Error embedding request:", str(e))
        return None


# =========================
# SEARCH
# =========================

def cosine(a, b):
    if a is None or b is None:
        return -1

    a = np.array(a)
    b = np.array(b)

    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return -1

    return np.dot(a, b) / denom


def search(query_embedding, data, k=TOP_K, file_filter=None):
    scored = []

    for item in data:
        try:
            score = cosine(query_embedding, item["embedding"])

            if score >= SIM_THRESHOLD:
                if file_filter and file_filter not in item.get("file", ""):
                    continue

                scored.append((score, item))

        except:
            pass

    scored.sort(reverse=True, key=lambda x: x[0])
    return [item for _, item in scored[:k]]


# =========================
# MAIN
# =========================

def main():

    print("🧠 RAG + DEBUGGER + ARCHITECTURE MODE")
    print("💬 Escribe 'exit' para salir\n")

    data = load_embeddings()
    symbols = load_symbols()

    print(f"📚 Embeddings: {len(data)}")
    print(f"🏗 Symbols: {len(symbols)}\n")

    if not data:
        print("❌ No embeddings")
        return

    # =========================
    # SELECCIÓN MODELO IA
    # =========================

    print("=== MODO IA LOCAL ===")
    print("1. DEPURACIÓN")
    print("2. ARQUITECTURA")
    print("3. DOCUMENTACIÓN")

    mode = input("Selecciona modo: ")

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
#
# Durante las pruebas del backend CLOUD se selecciona
# explícitamente un modelo válido de OpenRouter.
# En ejecución LOCAL se utilizará selected_model.

    session = {
        "mode": selected_mode,
#          "backend": "LOCAL",
        "backend": "cloud",  # o "CLOUD"
#          "model": selected_model
        "model": "openai/gpt-4.1-mini"  # Identificador válido en OpenRouter
    }

    print("\n==============================")
    print("Sesión actual")
    print("==============================")
    print(f"Modo IA : {session['mode']}")
    print(f"Backend : {session['backend']}")
    print(f"Modelo  : {session['model']}")
    print("==============================\n")

    # =========================
    # LOOP
    # =========================

    while True:

        user_input = input("💬 Input: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        # =========================
        # LOGGER INIT (POR PREGUNTA)
        # =========================

        init_logger(
            mode=session["mode"],
            model_chat=session["model"],
            model_embedding=MODEL_EMBED,
            backend=session["backend"],
            question=user_input
        )

        log_step("SESSION_START")
        log_step("MODE_SELECTED", session["mode"])
        log_step("INPUT_RECEIVED", session["mode"])

        error_info = None
        file_filter = None

        if is_compiler_error(user_input):
            error_info = extract_error_info(user_input)
            file_filter = error_info.get("file")
            query_text = user_input + " " + (file_filter or "")
            log_step("COMPILER_ERROR", session["mode"])
        else:
            query_text = user_input

        # =========================
        # EMBEDDING
        # =========================

        log_step("EMBEDDING_START", session["mode"])

        q_emb = get_embedding(query_text)

        if q_emb is None:
            log_step("EMBEDDING_FAIL", session["mode"])
            continue

        log_step("EMBEDDING_OK", session["mode"])

        # =========================
        # SEARCH
        # =========================

        log_step("SEARCH_START", session["mode"])

        results = search(q_emb, data, TOP_K, file_filter)

        log_step("SEARCH_DONE", session["mode"])

        # =========================
        # CONTEXT
        # =========================

        context = ""
        if file_filter:
            context = f"[FILE FILTER ACTIVE: {file_filter}]"

        symbol = find_symbol_context(user_input, symbols)
        symbol_context = build_symbol_context(symbol)

        # =========================
        # LLM
        # =========================

        log_step("LLM_START", session["mode"])

        answer = ask_llm_backend(
            context,
            user_input,
            session["model"],
            error_info,
            symbol_context,
            backend=session["backend"].lower()
        )

        log_step("LLM_DONE", session["mode"])

        print("\n🤖 Respuesta:\n")
        print(answer)
        print("\n" + "=" * 60 + "\n")

        log_step("ANSWER_PRINTED", session["mode"])


if __name__ == "__main__":
    main()
