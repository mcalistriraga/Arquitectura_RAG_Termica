# =============================================================
# Proyecto: Arquitectura RAG local con supervisión térmica
# Archivo: query.py
#
# Versión: 1.1
# Fecha: Julio 2026
# Hora: 14:00
#
# Descripción:
# ------------
# Módulo principal de consulta del sistema RAG local.
#
# Implementa:
# - Carga de embeddings generados previamente.
# - Generación del embedding de la consulta mediante Ollama.
# - Búsqueda semántica mediante similitud coseno.
# - Recuperación de contexto arquitectónico mediante symbols.jsonl.
# - Consulta a modelos LLM locales utilizando Ollama.
#
# Modos de operación:
# 1. Debugging C# / MAUI
# 2. Arquitectura del sistema
# 3. Documentación técnica
#
# Correcciones versión 1.1:
# -------------------------
# - Se elimina el manejo directo de supervisión térmica dentro de query.py.
# - La protección térmica queda delegada exclusivamente a thermal_watchdog.py.
# - Se eliminan dependencias obsoletas con logger.py relacionadas con temperatura.
# - Se mantiene la responsabilidad de query.py enfocada en el pipeline RAG.
#
# Arquitectura actual:
# --------------------
# query.py
#     |
#     +-- Gestión de consultas RAG
#     +-- Embeddings
#     +-- Búsqueda semántica
#     +-- Inferencia LLM
#     +-- Registro de eventos
#
# thermal_watchdog.py
#     |
#     +-- Supervisión térmica del hardware
#     +-- Protección ante temperaturas críticas
#
# Modelos configurados:
# - Embeddings : nomic-embed-text
# - Debug      : qwen2.5-coder:1.5b
# - Arquitectura/Docs : llama3.2:3b
#
# Objetivo versión 1.1:
# ---------------------
# Recuperar una versión funcional y coherente del módulo de consulta,
# compatible con la arquitectura desacoplada de supervisión térmica.
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
    is_aborted,
)

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
# LLM
# =========================

def ask_llm(context, question, model, error_info=None, symbol_context=""):

    # =========================
    # MODEL SAFETY
    # =========================

    allowed_models = {
        "qwen2.5-coder:1.5b",
        "llama3.2:3b",
        "llama3:latest",
        "nomic-embed-text:latest"
    }

    if model not in allowed_models:
        print(f"❌ MODELO INVALIDO: {model}")
        model = "qwen2.5-coder:1.5b"

    full_context = f"""
{symbol_context}

{context}
"""[:1500]

    if error_info:
        prompt = f"""
Eres un experto en debugging C# y MAUI.

ERROR:
{error_info['raw']}

ARCHIVO:
{error_info['file']}

CONTEXTO:
{full_context}

INSTRUCCIONES:
- Explica la causa exacta
- Identifica clase o propiedad
- Propón fix exacto
- Impacto en UI/ViewModel

RESPUESTA:
"""
    else:
        prompt = f"""
Eres un asistente técnico MAUI.

CONTEXTO:
{full_context}

PREGUNTA:
{question}

RESPUESTA:
"""

    try:
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        print("🔍 LLM STATUS:", response.status_code)

        try:
            print("🔍 LLM RAW:", response.text[:300])
        except:
            pass

        if response.status_code == 200:
            return response.json().get("response", "")

        return "❌ Error LLM"

    except Exception as e:
        print("❌ LLM EXCEPTION:", str(e))
        return "❌ Error LLM"


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
    # LOGGER INIT
    # =========================

    init_logger()
    log_step("SESSION_START")

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

    log_step("MODE_SELECTED", selected_mode)

    # =========================
    # LOOP
    # =========================

    while True:

        # 🔥 CONTROL TÉRMICO GLOBAL (único punto de control)
        if is_aborted():
            print("🛑 SISTEMA ABORTADO POR TEMPERATURA")
            log_step("ABORT_GLOBAL", selected_mode)
            break

        user_input = input("💬 Input: ")

        if user_input.lower() in ["exit", "quit"]:
            log_step("EXIT")
            break

        log_step("INPUT_RECEIVED", selected_mode)

        error_info = None
        file_filter = None

        if is_compiler_error(user_input):
            error_info = extract_error_info(user_input)
            file_filter = error_info.get("file")
            query_text = user_input + " " + (file_filter or "")
            log_step("COMPILER_ERROR", selected_mode)
        else:
            query_text = user_input

        # =========================
        # EMBEDDING
        # =========================

        log_step("EMBEDDING_START", selected_mode)

        q_emb = get_embedding(query_text)

        if q_emb is None:
            log_step("EMBEDDING_FAIL", selected_mode)
            continue

        log_step("EMBEDDING_OK", selected_mode)

        # =========================
        # SEARCH
        # =========================

        log_step("SEARCH_START", selected_mode)

        results = search(q_emb, data, TOP_K, file_filter)

        log_step("SEARCH_DONE", selected_mode)

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

        log_step("LLM_START", selected_mode)

        answer = ask_llm(
            context,
            user_input,
            selected_model,
            error_info,
            symbol_context
        )

        log_step("LLM_DONE", selected_mode)

        print("\n🤖 Respuesta:\n")
        print(answer)
        print("\n" + "=" * 60 + "\n")

        log_step("ANSWER_PRINTED", selected_mode)


if __name__ == "__main__":
    main()
