import time
from datetime import datetime


# =========================
# ESTADO GLOBAL
# =========================

LOG_FILE = None
t0 = None


# =========================
# INIT LOGGER
# =========================

def init_logger(
    question="",
    mode="",
    model_chat="",
    model_embedding=""
):

    global LOG_FILE, t0

    LOG_FILE = "query_log.txt"

    t0 = time.time()


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
            f"Fecha:\n"
            f"{datetime.now()}\n\n"
        )

        f.write(
            f"Modelo IA:\n"
            f"{model_chat}\n\n"
        )

        f.write(
            f"Modelo embedding:\n"
            f"{model_embedding}\n\n"
        )

        f.write(
            f"Modo seleccionado:\n"
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
# LOG STEP
# =========================

def log_step(step, mode=""):

    global LOG_FILE, t0


    now = time.time()

    delta = round(
        now - t0,
        3
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


# =========================
# CONSULTA ESTADO
# =========================

def is_aborted():

    return False