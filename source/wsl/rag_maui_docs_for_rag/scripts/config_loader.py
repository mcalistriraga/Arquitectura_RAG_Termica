# =============================================================
# Proyecto:
# Arquitectura RAG local con supervisión térmica
#
# Archivo:
# config_loader.py
#
# Versión:
# 1.2
#
# Fecha:
# 04 de Agosto de 2026
#
# Descripción:
# ------------
# Módulo encargado de cargar archivos de configuración externos
# del sistema.
#
# Su responsabilidad consiste en leer archivos de texto con
# formato de configuración simple, interpretar su contenido y
# devolver la información como un diccionario Python para ser
# utilizada por cualquier componente del proyecto.
#
# La lógica de lectura e interpretación de archivos de
# configuración permanece completamente desacoplada de los
# módulos funcionales, evitando duplicación de código y
# facilitando la evolución del sistema.
#
# Este módulo implementa únicamente la interpretación sintáctica
# de la configuración.
#
# La validación funcional de parámetros corresponde a cada módulo
# consumidor o a herramientas específicas de diagnóstico.
#
# Responsabilidades:
# ------------------
# - Leer archivos de configuración externos.
# - Ignorar líneas vacías.
# - Ignorar comentarios.
# - Interpretar parámetros con formato:
#
#       parametro = valor
#
# - Convertir automáticamente valores a tipos básicos cuando
#   sea posible.
# - Soportar listas de valores.
# - Devolver la configuración como un diccionario Python.
# - Proporcionar una interfaz común de carga para los módulos
#   del proyecto.
#
# Formato soportado:
# ------------------
#
# Comentarios:
#
#       # comentario
#
#
# Parámetros simples:
#
#       nombre = valor
#
#
# Listas:
#
#       nombre =
#       valor1,
#       valor2,
#       valor3
#
#
# Conversión automática:
#
# - booleanos:
#
#       true / false
#
# - enteros:
#
#       10
#
# - flotantes:
#
#       1.5
#
# - texto:
#
#       cualquier cadena no reconocida
#
# - listas:
#
#       conjunto de valores convertidos individualmente.
#
#
# Los parámetros desconocidos son igualmente cargados,
# permitiendo que cada módulo decida posteriormente cómo
# utilizarlos.
#
# Arquitectura simplificada:
# --------------------------
#
#             archivo.conf
#                  │
#                  ▼
#          config_loader.py
#                  │
#                  ▼
#        Diccionario Python
#                  │
#      ┌───────────┼───────────┐
#      ▼           ▼           ▼
#   embed.py    query.py   otros módulos
#
#
# Principios de diseño:
# ---------------------
# - Responsabilidad única.
# - Bajo acoplamiento.
# - Configuración externa al código.
# - Separación entre lectura y validación.
# - Independencia respecto a módulos funcionales.
# - Reutilización por cualquier componente del sistema.
#
# Este módulo no es responsable de:
#
# - validar reglas funcionales de cada parámetro;
# - comprobar dependencias entre configuraciones;
# - modificar archivos .conf;
# - generar reportes de diagnóstico;
# - ejecutar acciones basadas en la configuración cargada.
#
# Cambios versión 1.2:
# --------------------
# - Se documenta formalmente el soporte de listas.
# - Se documenta la conversión automática de tipos básicos.
# - Se aclara la separación entre carga de configuración y
#   validación funcional.
# - Se consolida como componente común para todos los módulos
#   que requieran parámetros externos.
#
# Evolución prevista:
# -------------------
# Este módulo continuará especializado únicamente en la carga
# e interpretación de configuraciones.
#
# Posibles extensiones futuras:
#
# - soporte de estructuras jerárquicas;
# - perfiles de configuración;
# - validadores externos por módulo;
# - esquemas de configuración.
#
# La evolución debe mantener la separación entre:
#
#       lectura de configuración
#              │
#              ▼
#       validación específica
#              │
#              ▼
#       ejecución del módulo
#
# Objetivo de la versión:
# -----------------------
# Consolidar un componente reutilizable y desacoplado para la
# carga de configuraciones del sistema, estableciendo una base
# común para todos los módulos que requieran parámetros externos
# sin incorporar lógica específica de aplicación.
#
# =============================================================


import os

# =========================
# CONVERSIÓN DE TIPOS
# =========================

def parse_value(value):

    value = value.strip()


    # Booleanos

    if value.lower() == "true":
        return True


    if value.lower() == "false":
        return False


    # Enteros

    try:

        return int(value)

    except ValueError:

        pass


    # Flotantes

    try:

        return float(value)

    except ValueError:

        pass


    # Texto

    return value


# =========================
# CARGAR CONFIGURACIÓN
# =========================

def load_config(filename):

    config = {}

    if not os.path.exists(filename):
        return config

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as file:

        lines = file.readlines()

    i = 0

    while i < len(lines):

        line = lines[i].strip()

        # Ignorar líneas vacías

        if not line:
            i += 1
            continue

        # Ignorar comentarios

        if line.startswith("#"):
            i += 1
            continue

        # Buscar asignaciones

        if "=" not in line:
            i += 1
            continue

        key, value = line.split(
            "=",
            1
        )

        key = key.strip()
        value = value.strip()

        # ----------------------------------
        # Valor simple
        # ----------------------------------

        if value != "":

            config[key] = parse_value(value)
            i += 1
            continue

        # ----------------------------------
        # Lista
        # ----------------------------------

        values = []

        i += 1

        while i < len(lines):

            item = lines[i].strip()

            if not item:
                break

            if item.startswith("#"):
                break

            if "=" in item:
                break

            item = item.rstrip(",")

            if item:

                values.append(
                    parse_value(item)
                )

            i += 1

        config[key] = values

    return config

