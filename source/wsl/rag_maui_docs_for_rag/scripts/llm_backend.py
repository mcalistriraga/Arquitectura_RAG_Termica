# =============================================================
# Proyecto: Arquitectura RAG local con supervisión térmica
#
# Archivo:
# llm_backend.py
#
# Versión:
# 0.3
#
# Fecha:
# 24 de Julio de 2026
#
# Descripción:
# ------------
# Módulo de abstracción del backend de inferencia LLM.
#
# Su propósito es desacoplar completamente el pipeline RAG del
# proveedor encargado de generar la respuesta, permitiendo
# incorporar nuevos servicios de inferencia sin modificar
# query.py ni el resto de la arquitectura.
#
# Responsabilidades:
# ------------------
# - Recibir la solicitud de generación enviada por query.py.
# - Construir el prompt de consulta.
# - Seleccionar el backend configurado.
# - Invocar el proveedor correspondiente.
# - Gestionar la comunicación HTTP.
# - Devolver únicamente el texto generado por el modelo.
#
# Backends disponibles:
# ---------------------
# - LOCAL : Ollama ejecutándose en el equipo.
# - CLOUD : OpenRouter mediante API REST.
#
# Cambios versión 0.3:
# --------------------
# - Se mantiene el backend LOCAL mediante Ollama.
# - Se implementa completamente el backend CLOUD utilizando
#   OpenRouter.
# - Ambos proveedores reutilizan la función build_prompt().
# - La API Key se obtiene desde el archivo .env mediante
#   python-dotenv.
# - El payload enviado a OpenRouter utiliza el formato
#   "messages" compatible con la API Chat Completions.
# - La respuesta generada se obtiene desde:
#       choices[0].message.content
# - Se mantiene completamente desacoplado query.py del
#   proveedor de inferencia utilizado.
#
# Arquitectura:
# -------------
#
#                    query.py
#                        │
#                        ▼
#              ask_llm_backend()
#                        │
#            ┌───────────┴───────────┐
#            │                       │
#            ▼                       ▼
#      ask_ollama()          ask_openrouter()
#            │                       │
#            ▼                       ▼
#        Ollama Local         OpenRouter Cloud
#            │                       │
#            └───────────┬───────────┘
#                        ▼
#              Respuesta del modelo
#
# Principio arquitectónico:
# -------------------------
# Este módulo no participa en la recuperación del conocimiento
# (RAG). Su única responsabilidad consiste en transformar el
# contexto recibido en una solicitud para el proveedor de
# inferencia seleccionado y devolver la respuesta generada.
#
# La separación entre recuperación e inferencia permite
# incorporar nuevos proveedores (OpenAI, Gemini, Claude,
# modelos locales, etc.) sin modificar el núcleo del sistema.
#
# Objetivo de la versión:
# -----------------------
# Consolidar una capa de abstracción para la inferencia LLM
# que permita seleccionar dinámicamente el proveedor de
# generación manteniendo inalterado el pipeline RAG.
#
# =============================================================

import os

import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURACIÓN
# ============================================================

load_dotenv()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)


OPENROUTER_CHAT_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

BACKEND_LOCAL = "local"

BACKEND_CLOUD = "cloud"

OLLAMA_CHAT_URL = "http://localhost:11434/api/generate"


def ask_llm_backend(
    context,
    question,
    model,
    error_info=None,
    symbol_context="",
    backend=BACKEND_LOCAL
):

    if backend == BACKEND_LOCAL:

        return ask_ollama(
            context,
            question,
            model,
            error_info,
            symbol_context
        )


    elif backend == BACKEND_CLOUD:

         return ask_openrouter(
            context,
            question,
            model,
            error_info,
            symbol_context
        )


    else:

        return "❌ Backend no válido"


# ============================================================
# CONSTRUCCIÓN DEL PROMPT
# ============================================================

def build_prompt(
    context,
    question,
    error_info=None,
    symbol_context=""
):

    full_context = f"""
{symbol_context}

{context}
"""[:1500]


    # =========================
    # PROMPT PARA ANÁLISIS DE ERRORES
    # =========================

    if error_info:

        return f"""
Eres un ingeniero experto en desarrollo C# y .NET MAUI.

Analiza el siguiente error de compilación.

ERROR:
{error_info['raw']}

ARCHIVO:
{error_info['file']}

CONTEXTO ARQUITECTÓNICO:
{full_context}

OBJETIVO:
Ayudar a un técnico a corregir el problema.

RESPUESTA ESPERADA:

1. Explicación de la causa probable.
2. Clase, método o propiedad involucrada.
3. Corrección recomendada.
4. Impacto sobre ViewModel, UI o arquitectura.

RESPUESTA:
"""


    # =========================
    # PROMPT PARA CONSULTAS
    # =========================

    return f"""
Eres un arquitecto senior especializado en sistemas
.NET MAUI, C# y arquitectura de software.

Utiliza el contexto proporcionado para responder.

CONTEXTO:
{full_context}

PREGUNTA:
{question}

REQUISITOS:
- Responde de forma técnica.
- Explica decisiones arquitectónicas.
- Propón mejoras cuando sean necesarias.
- Evita respuestas genéricas.

RESPUESTA:
"""


# ============================================================
# BACKEND LOCAL OLLAMA
# ============================================================

def ask_ollama(
    context,
    question,
    model,
    error_info=None,
    symbol_context=""
):

    prompt = build_prompt(
        context,
        question,
        error_info,
        symbol_context
    )


    # =========================
    # LLAMADA A OLLAMA
    # =========================

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


        if response.status_code == 200:

            result = response.json().get(
                "response",
                ""
            )

            return result


        return (
            f"❌ Error Ollama HTTP "
            f"{response.status_code}"
        )


    except Exception as e:

        return (
            f"❌ Error backend local Ollama: {e}"
        )

# ============================================================
# BACKEND CLOUD OPENROUTER
# ============================================================

def ask_openrouter(
    context,
    question,
    model,
    error_info=None,
    symbol_context=""
):

    if not OPENROUTER_API_KEY:

        return (
            "❌ Error OpenRouter: "
            "No se encontró OPENROUTER_API_KEY."
        )


    prompt = build_prompt(
        context,
        question,
        error_info,
        symbol_context
    )


    headers = {

        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json"
    }


    payload = {
    
        "model": model,
    
        "messages": [
    
            {
                "role": "user",
                "content": prompt
            }
    
        ],
    
        "max_tokens": 512
    
    }


    try:

        response = requests.post(

            OPENROUTER_CHAT_URL,

            headers=headers,

            json=payload,

            timeout=120
        )


        if response.status_code != 200:

            return (
                f"❌ Error OpenRouter HTTP "
                f"{response.status_code}: "
                f"{response.text}"
            )


        data = response.json()


        return (
            data["choices"][0]
                ["message"]["content"]
                .strip()
        )


    except requests.exceptions.Timeout:

        return (
            "❌ Error OpenRouter: "
            "Tiempo de espera agotado."
        )


    except requests.exceptions.RequestException as e:

        return (
            f"❌ Error OpenRouter: {e}"
        )


    except (
        KeyError,
        IndexError,
        ValueError
    ) as e:

        return (
            f"❌ Error procesando respuesta "
            f"OpenRouter: {e}"
        )

