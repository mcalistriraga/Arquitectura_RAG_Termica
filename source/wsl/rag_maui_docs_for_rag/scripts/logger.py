""""
=============================================================
Proyecto: Arquitectura RAG local con supervisión térmica

Archivo:
logger.py

Versión:
1.5

Fecha:
28 de Julio de 2026

Descripción:
------------
Módulo de registro y observabilidad del pipeline RAG.

Su responsabilidad es registrar cronológicamente la
ejecución de cada consulta y generar métricas de
rendimiento del pipeline sin interferir con la lógica
funcional del sistema.

Cada pregunta realizada por el usuario genera una nueva
sesión de registro independiente en query_log.txt.

Además del registro cronológico y las métricas de
rendimiento, el módulo proporciona un mecanismo genérico
de depuración que permite a cualquier componente del
proyecto registrar información técnica adicional durante
la ejecución del sistema.

Responsabilidades:
------------------
# Registrar los eventos relevantes del pipeline.
# Inicializar una nueva sesión de log por consulta.
# Calcular automáticamente métricas de rendimiento.
# Generar un resumen al finalizar la ejecución.
# Proporcionar un mecanismo genérico para registrar
# información de depuración.
# Mantener compatibilidad con el resto del proyecto.

Métricas registradas:
---------------------
# EMBEDDING_TIME
# SEARCH_TIME
# LLM_TIME
# PIPELINE_TIME

Capacidades de depuración:
--------------------------
# Registrar información arbitraria enviada por cualquier
# componente del sistema.
# Centralizar la información de diagnóstico en query_log.txt.
# Facilitar el análisis del pipeline sin modificar la lógica
# principal de los componentes.
# Mantener desacoplado el mecanismo de depuración del resto
# de la arquitectura.

Arquitectura:
-------------

                query.py
                    │
        log_step(...) / log_debug(...)
                    │
                    ▼
               logger.py
                    │
      ┌─────────────┼──────────────┐
      │             │              │
      ▼             ▼              ▼
 Registro      Métricas      Información
 cronológico   automáticas   de depuración
                    │
                    ▼
               query_log.txt

Cambios versión 1.5:
--------------------
# Se mantiene una sesión independiente por cada consulta.
# Se conservan las métricas automáticas del pipeline.
# Se mantiene PIPELINE_TIME como tiempo total de ejecución
# de la consulta.
# Se incorpora la función genérica log_debug().
# Cualquier componente del sistema puede registrar
# información adicional de depuración mediante log_debug().
# Se centraliza el registro de diagnóstico en logger.py,
# evitando código de depuración distribuido por el proyecto.
# Se mantiene compatibilidad completa con query.py y el
# resto de los módulos del sistema.

Principio arquitectónico:
-------------------------
logger.py constituye un componente de observabilidad.

No participa en la recuperación del conocimiento, la
búsqueda semántica, la construcción del contexto ni la
generación de respuestas.

Su única responsabilidad consiste en registrar el
comportamiento del sistema, calcular métricas de
rendimiento y almacenar la información de diagnóstico
que otros componentes decidan registrar, facilitando el
análisis, la optimización y la depuración del pipeline
RAG.

Objetivo de la versión:
-----------------------
Consolidar un mecanismo uniforme de trazabilidad,
medición del rendimiento y registro de información de
depuración, proporcionando un punto centralizado de
observabilidad para todos los componentes del sistema,
manteniendo completamente desacoplado el mecanismo de
registro respecto a la lógica funcional del pipeline.

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

# =========================
# DEBUG
# =========================

def log_debug(
    title,
    text
):
    """
    Registra información adicional de depuración
    en el archivo de log activo.

    Puede utilizarse desde cualquier módulo del
    proyecto para almacenar información temporal
    durante el desarrollo sin afectar el registro
    principal del pipeline.
    """

    if LOG_FILE is None:
        return

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
            f"{title}\n"
        )

        f.write(
            "================================\n\n"
        )

        f.write(text)

        f.write("\n")
