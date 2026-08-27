# =============================================================
# Proyecto:
# Arquitectura RAG local con supervisión térmica
#
# Archivo:
# query.py
#
# Versión:
# 1.8
#
# Fecha:
# 27 de Agosto de 2026
#
# Descripción:
# ------------
# Módulo principal del pipeline RAG refactorizado bajo ADR-013.
#
# Coordina la ejecución completa del pipeline desde la recepción
# de la consulta hasta la generación de respuesta y observabilidad,
# consumiendo de forma unificada el Target Project activo resuelto
# por config_loader.py.
#
# Cambios versión 1.7:
# --------------------
# - Adopción estricta de resolución dinámica de workspace mediante
#   `config_loader.resolve_active_workspace()` (ADR-013).
# - Lectura de embeddings y símbolos atómicos directamente desde la
#   Knowledge Source del espacio de trabajo activo.
# - Adaptación del buscador semántico de símbolos para procesar el
#   esquema enriquecido de KS2 (`symbols_raw.jsonl`).
#
# Cambios versión 1.8:
# --------------------
# - Sustitución del matcher por coincidencia semántica y tokenizada
#   agnóstica del lenguaje (`_extract_tokens` y `find_symbol_context`).
# - Búsqueda de símbolos insensible a mayúsculas/minúsculas mediante
#   tokenización limpia (soporta PascalCase, camelCase y snake_case).
# - Soporte políglota universal (C#, Java, C++, Python) sin acoplamiento
#   a sufijos específicos de lenguaje o arquitectura.
# =============================================================

import os
import json
import numpy as np
import requests
import re
import time
from pathlib import Path
from datetime import datetime

from logger import (
    init_logger,
    log_step,
    log_debug,
)

from llm_backend import ask_llm_backend
from config_loader import resolve_active_workspace

# =========================
# CONFIGURACIÓN
# =========================

SLEEP_TIME = 0.0

OLLAMA_CHAT_URL = "http://localhost:11434/api/generate"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

MODEL_DEBUG = "qwen2.5-coder:1.5b"
MODEL_ARCH = "llama3.2:3b"
MODEL_DOCS = "llama3.2:3b"

MODEL_EMBED = "nomic-embed-text"

TOP_K = 3
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
# CARGA DE SÍMBOLOS (KS2 - Buscador Multi-Símbolo Top-N v1.9)
# =========================

TOP_K_SYMBOLS = 3  # Máximo número de símbolos relacionados a inyectar


def load_symbols(symbols_path: Path):
    symbols = []
    if not symbols_path.exists():
        print(f"⚠️ No existe el archivo de símbolos: {symbols_path}")
        return symbols

    with open(symbols_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                symbols.append(json.loads(line))
            except Exception:
                pass

    return symbols


def _extract_tokens(text: str) -> set[str]:
    """
    Tokenizador universal agnóstico del lenguaje.
    Descompone PascalCase, camelCase y snake_case a minúsculas.
    """
    cleaned = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    cleaned = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", cleaned)
    cleaned = re.sub(r"[_\W]+", " ", cleaned)
    
    return {w.lower() for w in cleaned.split() if len(w) > 2}


def find_symbol_context(question: str, symbols: list, top_k: int = TOP_K_SYMBOLS) -> list:
    """
    Recupera un ranking de hasta top_k símbolos más relevantes para la consulta.
    Combina coincidencias por subcadena compacta e intersección de tokens semánticos.
    """
    q_lower_compact = question.lower().replace(" ", "")
    q_tokens = _extract_tokens(question)
    
    log_debug("SYMBOL SEARCH INPUT", f"RAW: {question}\nTOKENS: {sorted(list(q_tokens))}")

    candidates = []

    for s in symbols:
        name = s.get("name", "")
        if not name:
            continue

        name_lower = name.lower()
        score = 0.0

        # Coincidencia 1: Match por Subcadena Compacta (Alta prioridad)
        if name_lower in q_lower_compact:
            score += 10.0 + len(name_lower)  # Da más peso a nombres más específicos/largos

        # Coincidencia 2: Intersección de Tokens Semánticos
        sym_tokens = _extract_tokens(name)
        overlap = len(q_tokens.intersection(sym_tokens))
        if overlap > 0:
            score += overlap * 2.0

        if score > 0:
            candidates.append((score, s))

    # Ordenar por mayor puntuación
    candidates.sort(key=lambda x: x[0], reverse=True)
    matched_symbols = [item[1] for item in candidates[:top_k]]

    if matched_symbols:
        matched_names = [s.get("name") for s in matched_symbols]
        log_debug("SYMBOL SEARCH SUCCESS", f"TOP {len(matched_symbols)} MATCHES: {matched_names}")
    else:
        log_debug("SYMBOL SEARCH FAILED", "No symbols matched the search criteria.")

    return matched_symbols


def build_symbol_context(symbols_list: list) -> str:
    """
    Construye el bloque de contexto concatenando los metadatos de los símbolos candidatos.
    """
    if not symbols_list:
        return ""

    blocks = ["ARCHITECTURE CONTEXT (KS2 Top Symbols Match)"]
    
    for i, symbol in enumerate(symbols_list, 1):
        props = [p.get("name") for p in symbol.get("properties", []) if isinstance(p, dict)]
        methods = [m.get("name") for m in symbol.get("methods", []) if isinstance(m, dict)]

        block = f"""
--- CANDIDATE ENTITY {i} ---
ENTITY      : {symbol.get('entity_type', 'Class')} {symbol.get('name')}
NAMESPACE   : {symbol.get('namespace')}
FILE        : {symbol.get('file')}
PROPERTIES  : {', '.join(props) if props else 'None'}
METHODS     : {', '.join(methods) if methods else 'None'}
INHERITS    : {symbol.get('inherits', 'None')}"""
        blocks.append(block)

    ctx = "\n".join(blocks)
    log_debug("SYMBOL CONTEXT BUILT", ctx)
    return ctx


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

def load_embeddings(embeddings_path: Path):
    data = []
    if not embeddings_path.exists():
        print(f"❌ No existe el índice vectorial: {embeddings_path}")
        return data

    with open(embeddings_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                if "embedding" in item and item["embedding"]:
                    data.append(item)
            except Exception:
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
        except Exception:
            pass

    scored.sort(reverse=True, key=lambda x: x[0])
    return [{"score": score, "data": item} for score, item in scored[:k]]

# =========================
# MAIN
# =========================

def main():
    print("🧠 RAG + DEBUGGER + ARCHITECTURE MODE (ADR-013)")
    print("💬 Escribe 'exit' para salir\n")

    # Resolución dinámica del Target Project
    workspace_dir = resolve_active_workspace()
    embeddings_path = workspace_dir / "knowledge" / "embeddings" / "embeddings.jsonl"
    symbols_path = workspace_dir / "knowledge" / "symbols" / "symbols_raw.jsonl"

    print(f"🎯 Target Workspace : {workspace_dir}")

    data = load_embeddings(embeddings_path)
    symbols = load_symbols(symbols_path)

    print(f"📚 Embeddings        : {len(data)}")
    print(f"🏗 Symbols           : {len(symbols)}\n")

    if not data:
        print("❌ No se encontraron embeddings en el workspace activo.")
        return

    # Selección de modelo
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

    session = {
        "mode": selected_mode,
        "backend": "cloud",
        "model": "openai/gpt-4.1-mini"
    }

    print("\n==============================")
    print("Sesión actual")
    print("==============================")
    print(f"Modo IA : {session['mode']}")
    print(f"Backend : {session['backend']}")
    print(f"Modelo  : {session['model']}")
    print("==============================\n")

    while True:
        user_input = input("💬 Input: ")

        if user_input.lower() in ["exit", "quit"]:
            break

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
            query_text = f"{user_input} {file_filter or ''}"
            log_step("COMPILER_ERROR", session["mode"])
        else:
            query_text = user_input

        log_step("EMBEDDING_START", session["mode"])
        q_emb = get_embedding(query_text)

        if q_emb is None:
            log_step("EMBEDDING_FAIL", session["mode"])
            continue

        log_step("EMBEDDING_OK", session["mode"])

        log_step("SEARCH_START", session["mode"])
        results = search(q_emb, data, TOP_K, file_filter)

        if DEBUG_RETRIEVAL:
            retrieval_info = ""
            for i, result in enumerate(results, 1):
                item = result["data"]
                retrieval_info += f"\nChunk: {i}\nScore: {result['score']:.4f}\nFile: {item.get('file')}\n"
            log_debug("RETRIEVAL METADATA", retrieval_info)

        log_step("SEARCH_DONE", session["mode"])

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
            log_debug("CHUNKS RECUPERADOS", debug_text)

        context = ""
        for result in results:
            item = result["data"]
            context += "\n\n" + item.get("content", "")

        if DEBUG_CONTEXT:
            log_debug(
                "RAG CONTEXT METADATA",
                f"CHUNKS_USED: {len(results)}\nCONTEXT_CHARACTERS: {len(context)}\nTOP_K: {TOP_K}\nSIM_THRESHOLD: {SIM_THRESHOLD}"
            )
            log_debug("RAG CONTEXT PREVIEW", context[:2000])

        if file_filter:
            context = f"[FILE FILTER ACTIVE: {file_filter}]\n{context}"

        # Búsqueda semántica en símbolos (Recuperación Multi-Símbolo Top-N v1.9)
        matched_symbols = find_symbol_context(user_input, symbols)
        symbol_context = build_symbol_context(matched_symbols)

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
