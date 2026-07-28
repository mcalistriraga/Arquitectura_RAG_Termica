"""
=============================================================
Proyecto: Arquitectura RAG local con supervisión térmica

Archivo:
logger.py

Versión:
1.4

Fecha:
24 de Julio de 2026

Descripción:
------------
Módulo de registro y observabilidad del pipeline RAG.

Su responsabilidad es registrar cronológicamente la
ejecución de cada consulta y generar métricas de
rendimiento del pipeline sin interferir con la lógica
funcional del sistema.

Cada pregunta realizada por el usuario genera una nueva
sesión de registro independiente en query_log.txt.

Responsabilidades:
------------------
# Registrar los eventos relevantes del pipeline.
# Inicializar una nueva sesión de log por consulta.
# Calcular automáticamente métricas de rendimiento.
# Generar un resumen al finalizar la ejecución.
# Mantener compatibilidad con el resto del proyecto.

Métricas registradas:
---------------------
# EMBEDDING_TIME
# SEARCH_TIME
# LLM_TIME
# PIPELINE_TIME

Arquitectura:
-------------

                query.py
                    │
          log_step(...) / init_logger()
                    │
                    ▼
               logger.py
                    │
      ┌─────────────┼─────────────┐
      │             │             │
      ▼             ▼             ▼
 Registro      Métricas      Resumen final
 cronológico   automáticas    query_log.txt

Cambios versión 1.4:
--------------------
# Se registra una sesión independiente por cada consulta.
# Se incorporan métricas automáticas del pipeline.
# El tiempo total pasa a medirse como PIPELINE_TIME.
# PIPELINE_TIME comprende desde INPUT_RECEIVED hasta
# ANSWER_PRINTED, excluyendo el tiempo de espera del usuario.
# Se genera automáticamente un resumen de rendimiento
# al finalizar cada consulta.
# Se mantiene compatibilidad completa con query.py.

Principio arquitectónico:
-------------------------
logger.py constituye un componente de observabilidad.
No participa en la recuperación del conocimiento ni en
la generación de respuestas; únicamente registra el
comportamiento del sistema para facilitar análisis,
optimización y diagnóstico.

Objetivo de la versión:
-----------------------
Consolidar un mecanismo uniforme de trazabilidad y
medición del rendimiento del pipeline RAG mediante un
registro independiente para cada consulta realizada.

=============================================================
"""

import time
from datetime import datetime


# =========================
# ESTADO GLOBAL
# =========================

LOG_FILE = None

t0 = None


# =========================
# MÉTRICAS
# =========================

stage_times = {}

metrics = {
    "embedding": None,
    "search": None,
    "llm": None,
    "pipeline": None
}


# =========================
# INIT LOGGER
# =========================

def init_logger(
    question="",
    mode="",
    model_chat="",
    model_embedding="",
    backend=""
):

    global LOG_FILE
    global t0
    global stage_times
    global metrics

    LOG_FILE = "query_log.txt"

    t0 = time.time()

    stage_times = {}

    metrics = {
        "embedding": None,
        "search": None,
        "llm": None,
        "pipeline": None
    }

    with open(
        LOG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "=== RAG QUERY SESSION START ===\n\n"
        )

        f.write(
            "Origen:\n"
            "query.py\n\n"
        )

        f.write(
            "Modulo:\n"
            "logger.py\n\n"
        )

        f.write(
            "Fecha:\n"
            f"{datetime.now()}\n\n"
        )

        f.write(
            "Backend IA:\n"
            f"{backend}\n\n"
        )

        f.write(
            "Modelo IA:\n"
            f"{model_chat}\n\n"
        )

        f.write(
            "Modelo embedding:\n"
            f"{model_embedding}\n\n"
        )

        f.write(
            "Modo seleccionado:\n"
            f"{mode}\n\n"
        )

        f.write(
            "Pregunta:\n"
            f"{question}\n\n"
        )

        f.write(
            "================================\n\n"
        )


# =========================
# ACTUALIZAR MÉTRICAS
# =========================

def _update_metrics(step, now):

    global stage_times
    global metrics

    if step == "INPUT_RECEIVED":

        stage_times["pipeline"] = now

    elif step == "EMBEDDING_START":

        stage_times["embedding"] = now

    elif step == "EMBEDDING_OK":

        if "embedding" in stage_times:

            metrics["embedding"] = (
                now - stage_times["embedding"]
            )

    elif step == "SEARCH_START":

        stage_times["search"] = now

    elif step == "SEARCH_DONE":

        if "search" in stage_times:

            metrics["search"] = (
                now - stage_times["search"]
            )

    elif step == "LLM_START":

        stage_times["llm"] = now

    elif step == "LLM_DONE":

        if "llm" in stage_times:

            metrics["llm"] = (
                now - stage_times["llm"]
            )

    elif step == "ANSWER_PRINTED":

        if "pipeline" in stage_times:

            metrics["pipeline"] = (
                now - stage_times["pipeline"]
            )


# =========================
# ESCRIBIR RESUMEN
# =========================

def _write_metrics_summary():

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write("\n")

        f.write(
            "================================\n"
        )

        f.write(
            "RESUMEN DE RENDIMIENTO\n"
        )

        f.write(
            "================================\n\n"
        )

        if metrics["embedding"] is not None:

            f.write(
                f"EMBEDDING_TIME : "
                f"{metrics['embedding']:.3f} s\n"
            )

        if metrics["search"] is not None:

            f.write(
                f"SEARCH_TIME    : "
                f"{metrics['search']:.3f} s\n"
            )

        if metrics["llm"] is not None:

            f.write(
                f"LLM_TIME       : "
                f"{metrics['llm']:.3f} s\n"
            )

        if metrics["pipeline"] is not None:

            f.write(
                f"PIPELINE_TIME  : "
                f"{metrics['pipeline']:.3f} s\n"
            )

        f.write(
            "\n================================\n"
        )


# =========================
# LOG STEP
# =========================

def log_step(step, mode=""):

    global LOG_FILE
    global t0

    now = time.time()

    delta = round(
        now - t0,
        3
    )

    _update_metrics(
        step,
        now
    )

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"[{delta}s] "
            f"STEP={step} "
            f"MODE={mode}\n"
        )

    if step == "ANSWER_PRINTED":

        _write_metrics_summary()


# =========================
# COMPATIBILIDAD
# =========================

def is_aborted():

    """
    Mantiene compatibilidad con versiones anteriores.

    La decisión de abortar por temperatura
    corresponde actualmente a
    thermal_watchdog.py.
    """

    return False
