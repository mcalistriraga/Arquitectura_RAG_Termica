# =============================================================
# Proyecto:
# Arquitectura RAG local con supervisión térmica
#
# Archivo:
# test_config.py
#
# Versión:
# 1.1
#
# Fecha:
# 04 de Agosto de 2026
#
# Descripción:
# ------------
# Herramienta de diagnóstico y validación del sistema de
# configuración del proyecto.
#
# Permite comprobar que los archivos externos de configuración
# (.conf) son interpretados correctamente por config_loader.py.
#
# Genera un archivo de salida con extensión .test donde se
# muestran:
#
# - parámetros detectados;
# - valores cargados;
# - tipos asignados;
# - listas interpretadas.
#
# Su objetivo es permitir al usuario administrador verificar
# manualmente la configuración antes de ejecutar módulos
# funcionales del sistema.
#
# Este módulo no contiene lógica propia de configuración.
# La lectura e interpretación de archivos permanece bajo la
# responsabilidad exclusiva de config_loader.py.
#
# Responsabilidades:
# ------------------
# - Validar argumentos recibidos desde línea de comandos.
# - Verificar existencia del archivo .conf indicado.
# - Cargar configuración mediante config_loader.py.
# - Mostrar parámetros interpretados.
# - Mostrar tipos de datos asignados.
# - Generar archivo diagnóstico .conf.test.
#
# Este módulo no es responsable de:
#
# - modificar archivos de configuración;
# - guardar configuraciones;
# - validar reglas funcionales de cada módulo;
# - determinar si un parámetro es correcto para una aplicación
#   específica.
#
# Uso:
#
#     python3 test_config.py archivo.conf
#
# Ejemplo:
#
#     python3 test_config.py embed.conf
#
# Salida:
#
#     embed.conf.test
#
# Arquitectura:
#
#              archivo.conf
#                    │
#                    ▼
#            config_loader.py
#                    │
#                    ▼
#          Diccionario Python
#                    │
#                    ▼
#             test_config.py
#                    │
#                    ▼
#          archivo.conf.test
#
# Principios de diseño:
# ---------------------
# - Separación entre configuración y código.
# - Responsabilidad única.
# - Diagnóstico externo al funcionamiento normal.
# - Verificación humana antes de ejecución.
# - Bajo acoplamiento con módulos funcionales.
#
# Evolución prevista:
# -------------------
# Este módulo podrá incorporar posteriormente:
#
# - validación de parámetros obligatorios;
# - detección de claves desconocidas;
# - comparación contra esquemas esperados;
# - generación de reportes de configuración;
# - soporte para múltiples perfiles de ejecución.
#
# Cambios versión 1.1:
# --------------------
# - Se adapta al nuevo módulo config_loader.py.
# - Se incorpora soporte para validación de listas y tipos.
# - Se formaliza como herramienta de diagnóstico del sistema.
# - Se actualiza documentación arquitectónica.
#
# Objetivo de la versión:
# -----------------------
# Consolidar una herramienta independiente para verificar la
# correcta carga de archivos de configuración antes de que los
# parámetros sean utilizados por los módulos funcionales del
# sistema.
#
# =============================================================


import sys
import os

from config_loader import load_config



# =========================
# VALIDACIÓN DE PARAMETROS
# =========================

def validate_arguments():


    if len(sys.argv) < 2:

        print(
            "❌ Error: No se indicó archivo de configuración."
        )

        print()

        print(
            "Debe indicar un archivo .conf como parámetro."
        )

        print()

        print(
            "Ejemplo:"
        )

        print(
            "python3 test_config.py embed.conf"
        )

        return None



    config_file = sys.argv[1]


    if not config_file.endswith(".conf"):

        print(
            "❌ Error: El archivo debe tener extensión .conf"
        )

        print()

        print(
            "Ejemplo:"
        )

        print(
            "python3 test_config.py embed.conf"
        )

        return None



    if not os.path.exists(config_file):

        print(
            f"❌ Error: No existe archivo {config_file}"
        )

        return None



    return config_file



# =========================
# GENERAR ARCHIVO TEST
# =========================

def generate_test_file(
    config_file,
    config
):

    output_file = (
        config_file
        +
        ".test"
    )


    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:


        file.write(
            "================================\n"
        )

        file.write(
            "CONFIGURACION CARGADA\n"
        )

        file.write(
            "================================\n\n"
        )


        file.write(
            f"Archivo origen:\n{config_file}\n\n"
        )


        file.write(
            "Parametros detectados:\n\n"
        )


        for key, value in config.items():


            file.write(
                f"{key} = {value}\n"
            )


            file.write(
                f"Tipo: {type(value).__name__}\n\n"
            )


        file.write(
            "================================\n"
        )


    return output_file



# =========================
# MAIN
# =========================

def main():


    config_file = validate_arguments()


    if config_file is None:

        return



    print()

    print(
        f"📄 Cargando configuración: {config_file}"
    )


    config = load_config(
        config_file
    )


    if not config:


        print(
            "⚠️ Advertencia: El archivo no contiene parámetros."
        )



    output_file = generate_test_file(
        config_file,
        config
    )



    print()

    print(
        "✅ Configuración cargada correctamente."
    )

    print(
        f"📄 Archivo generado: {output_file}"
    )



# =========================
# EJECUCIÓN
# =========================

if __name__ == "__main__":

    main()
