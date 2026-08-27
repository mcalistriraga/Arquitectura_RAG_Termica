# =============================================================
# Proyecto:
# Arquitectura RAG local con supervisión térmica
#
# Archivo:
# symbols_extractor.py
#
# Versión:
# 1.1
#
# Fecha:
# 21 de Agosto de 2026
#
# Descripción:
# ------------
# Extractor de la Knowledge Source: Símbolos y Estructura de Código.
#
# Lee project.conf para determinar el lenguaje del proyecto,
# invoca la estrategia de parsing correspondiente y genera
# el catálogo estructurado en knowledge/symbols/symbols_raw.jsonl.
#
# Cambios versión 1.1:
# --------------------
# - Eliminado WORKSPACE_DIR hardcodeado ("~/rag_workspace/
#   MauiAppGestorMovil"). El proyecto y su workspace se resuelven
#   igual que en knowledge_filter.py v1.7 y symbol_extractor.py v2.0:
#   argumento CLI, variable de entorno RAG_PROJECT, o autodetección
#   de un único project.conf en ~/rag_workspace.
# - Escritura de symbols_raw.jsonl ahora es atómica (tmp + flush +
#   fsync + os.replace), consistente con el patrón ya usado en
#   embed.py, para no dejar el archivo a medio escribir si el
#   proceso se interrumpe.
# - Se conserva sin cambios el diseño original de v1.0: selección
#   dinámica del parser según "language" en project.conf, vía
#   importlib.import_module(f"parsers.{language}_parser"). Esto
#   es lo que permite incorporar a futuro parsers para otros
#   lenguajes (java, python) sin modificar este módulo.
# =============================================================

import os
import sys
import json
import importlib

from config_loader import load_config


# =============================================================
# RESOLUCIÓN DE PROYECTO / WORKSPACE
#
# Mismo patrón que knowledge_filter.py v1.7: ningún nombre de
# proyecto queda hardcodeado en el código.
# =============================================================

def resolve_project_dir(workspace_root):
    """
    Determina qué proyecto del workspace procesar.

    Orden de resolución:
      1. Argumento de línea de comandos: python3 symbols_extractor.py <ProjectName>
      2. Variable de entorno RAG_PROJECT
      3. Autodetección: si el workspace contiene exactamente un
         subdirectorio con project.conf, se usa ese.
    """
    if len(sys.argv) > 1:
        return sys.argv[1]

    env_project = os.environ.get("RAG_PROJECT")
    if env_project:
        return env_project

    if os.path.isdir(workspace_root):
        candidates = [
            d for d in os.listdir(workspace_root)
            if os.path.isfile(os.path.join(workspace_root, d, "project.conf"))
        ]
        if len(candidates) == 1:
            return candidates[0]

    return None


# =============================================================
# PERSISTENCIA ATÓMICA
# =============================================================

def write_symbols_atomically(output_path, symbols):
    """
    Escribe symbols_raw.jsonl de forma atómica (tmp + flush +
    fsync + os.replace), evitando dejar el archivo a medio
    escribir si el proceso se interrumpe.
    """
    tmp_path = output_path + ".tmp"

    with open(tmp_path, "w", encoding="utf-8") as f:
        for symbol in symbols:
            f.write(json.dumps(symbol, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp_path, output_path)


# =============================================================
# MAIN
# =============================================================

def main():
    print("====================================")
    print("Inicio Extracción de Símbolos (KS 2)")

    workspace_root = os.path.expanduser("~/rag_workspace")

    project_name = resolve_project_dir(workspace_root)
    if not project_name:
        print(
            "❌ Error: no se pudo determinar el proyecto a procesar. "
            "Indicalo como argumento (python3 symbols_extractor.py <ProjectName>), "
            "definí la variable de entorno RAG_PROJECT, o asegurate de que "
            "el workspace contenga un único proyecto con project.conf."
        )
        return

    workspace_dir = os.path.join(workspace_root, project_name)
    project_conf_file = os.path.join(workspace_dir, "project.conf")

    print(f"Workspace : {workspace_dir}")

    if not os.path.exists(project_conf_file):
        print(f"❌ Error: No se encontró project.conf en {workspace_dir}")
        return

    config = load_config(project_conf_file)

    language = config.get("language", "csharp").lower()
    source_dir = os.path.join(workspace_dir, config.get("source_path_local", "source"))

    symbols_rel_path = config.get("symbols_path", "knowledge/symbols")
    output_dir = os.path.join(workspace_dir, symbols_rel_path)
    output_file = os.path.join(output_dir, "symbols_raw.jsonl")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Lenguaje  : {language}")
    print(f"Origen    : {source_dir}")
    print(f"Destino   : {output_file}")
    print("====================================\n")

    if not os.path.isdir(source_dir):
        print(f"❌ Error: no existe el directorio de fuente: {source_dir}")
        return

    # Selección dinámica de estrategia de parser
    try:
        parser_module = importlib.import_module(f"parsers.{language}_parser")
    except ImportError:
        print(f"❌ Error: No existe parser implementado para el lenguaje '{language}'")
        return

    # Mapeo de extensiones por lenguaje
    ext_map = {
        "csharp": [".cs"],
        "java": [".java"],
        "python": [".py"]
    }
    allowed_exts = ext_map.get(language, [".cs"])

    total_files = 0
    all_symbols = []

    for root, _, files in os.walk(source_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in allowed_exts:
                total_files += 1
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, source_dir)

                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Invocación delegada según la estrategia
                if language == "csharp":
                    symbols = parser_module.parse_csharp_file(content, rel_path)
                else:
                    symbols = []

                all_symbols.extend(symbols)

    write_symbols_atomically(output_file, all_symbols)

    print("================================")
    print("✅ Extracción de símbolos finalizada")
    print(f"📊 Archivos procesados : {total_files}")
    print(f"📊 Símbolos extraídos  : {len(all_symbols)}")
    print("================================")


if __name__ == "__main__":
    main()
