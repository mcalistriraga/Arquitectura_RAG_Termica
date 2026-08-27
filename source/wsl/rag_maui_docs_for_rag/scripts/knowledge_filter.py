# =============================================================
# Proyecto:
# Arquitectura RAG local con supervisión térmica
#
# Archivo:
# knowledge_filter.py
#
# Versión:
# 1.7
#
# Fecha:
# 21 de Agosto de 2026
#
# Descripción:
# ------------
# Módulo encargado de construir la fuente filtrada de conocimiento
# de un proyecto dentro del workspace RAG.
#
# Su responsabilidad es copiar únicamente los archivos autorizados
# mediante knowledge_policy.conf desde la fuente primaria del
# proyecto hacia el directorio source del workspace.
#
# Este módulo pertenece a la etapa:
# Adquisición de conocimiento
#
# Cambios versión 1.7:
# --------------------
# - Eliminado el nombre de proyecto hardcodeado ("MauiAppGestorMovil").
#   El workspace ahora se resuelve exclusivamente desde
#   'workspace_path' en project.conf, permitiendo que
#   knowledge_filter.py sea agnóstico de cualquier proyecto
#   particular.
# - Incorporada una validación de seguridad antes de shutil.rmtree()
#   sobre 'destination': se verifica que la ruta a borrar exista
#   dentro de workspace_path y que su nombre coincida con
#   'source_path_local' (por defecto "source"), para evitar un
#   borrado destructivo accidental si project.conf quedara mal
#   configurado.
#
# Cambios versión 1.6:
# --------------------
# - Eliminación total de listas estáticas/hardcodeadas en código.
#   Se mantiene la generalidad arquitectónica delegando el 100%
#   de las reglas a 'knowledge_policy.conf'.
# - Incorporación de sanitizador de caracteres raros / no imprimibles
#   (NBSP '\xa0', BOM '\ufeff', etc.) para prevenir corrupción de
#   claves y valores al procesar archivos de políticas.
# =============================================================

import os
import shutil
import sys
import re
from datetime import datetime


# =============================================================
# CONFIGURACIÓN Y LOGS
# =============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "knowledge_filter_log.txt")
LOGGER_ON = True

from config_loader import load_config


# =============================================================
# SANITIZACIÓN Y PARSER GENÉRICO DE CONFIGURACIÓN
# =============================================================

def sanitize_text(text):
    """
    Limpia caracteres invisibles, espacios no separables (NBSP \xa0),
    BOM (\ufeff) y saltos de carro (\r).
    """
    if not text:
        return ""
    # Reemplazar NBSP (\xa0) y tabuladores por espacios normales, remover BOM
    text = text.replace("\xa0", " ").replace("\ufeff", "").replace("\r", "")
    return text


def parse_policy_conf(file_path):
    """
    Parser agnóstico para knowledge_policy.conf.
    Soporta asignaciones multilínea y limpia automáticamente
    caracteres no imprimibles.
    """
    config = {}
    current_key = None

    if not os.path.exists(file_path):
        return config

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            clean_line = sanitize_text(raw_line).strip()

            # Ignorar líneas vacías, comentarios y divisores visuales
            if not clean_line or clean_line.startswith("#") or clean_line.startswith("="):
                continue

            if "=" in clean_line:
                parts = clean_line.split("=", 1)
                current_key = sanitize_text(parts[0]).strip()
                config[current_key] = []
                
                val_part = sanitize_text(parts[1]).strip()
                if val_part:
                    tokens = [t.strip() for t in val_part.split(",") if t.strip()]
                    config[current_key].extend(tokens)
            elif current_key:
                # Líneas de continuación multilínea
                tokens = [t.strip() for t in clean_line.split(",") if t.strip()]
                config[current_key].extend(tokens)

    return config


def normalize_wsl_path(path):
    r"""
    Traduce rutas de Windows (ej: E:\Developer\...) a formato WSL (/mnt/e/Developer/...)
    cuando el script se ejecuta en entorno POSIX/Linux.
    """
    if not path:
        return path

    if os.name == "posix" and len(path) >= 2 and path[1] == ":":
        drive = path[0].lower()
        rest = path[2:].replace("\\", "/")
        return f"/mnt/{drive}{rest}"

    return path


def log(message):
    if not LOGGER_ON:
        return
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{datetime.now()}] {message}\n")


def print_log(message):
    if LOGGER_ON:
        print(message, flush=True)
        log(message)


def resolve_project_dir(workspace_root):
    """
    Determina qué proyecto del workspace procesar, sin hardcodear
    ningún nombre de proyecto en el código.

    Orden de resolución:
      1. Argumento de línea de comandos: python3 knowledge_filter.py <ProjectName>
      2. Variable de entorno RAG_PROJECT
      3. Autodetección: si el workspace contiene exactamente un
         subdirectorio con project.conf, se usa ese.

    Si ninguna de estas condiciones se cumple de forma inequívoca,
    se detiene la ejecución en vez de asumir un proyecto por defecto.
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


def is_safe_to_delete(destination, workspace, expected_name):
    """
    Verificación de seguridad antes de una operación destructiva
    (shutil.rmtree). Exige que 'destination':

      1. esté ubicado dentro de 'workspace' (el workspace del
         proyecto declarado en project.conf), y
      2. su nombre de carpeta coincida con 'expected_name'
         (source_path_local, por defecto "source").

    Esto evita que un project.conf mal configurado (por ejemplo,
    con source_path_local vacío o apuntando fuera del workspace)
    produzca un borrado accidental de una ubicación no deseada.
    """
    dest_abs = os.path.abspath(destination)
    workspace_abs = os.path.abspath(workspace)

    within_workspace = (
        dest_abs == workspace_abs
        or dest_abs.startswith(workspace_abs + os.sep)
    )
    correct_name = os.path.basename(dest_abs) == expected_name

    return within_workspace and correct_name


# =============================================================
# VALIDACIÓN DE REGLAS BASADAS EN POLICY
# =============================================================

def is_excluded_directory(relative_path, exclude_dirs):
    """
    Verifica si alguna de las carpetas contenedoras pertenece a la
    lista de exclusión definida en el archivo de políticas.
    """
    if not exclude_dirs:
        return False

    normalized_path = relative_path.replace("\\", "/")
    parts = normalized_path.split("/")

    # Evaluar todas las carpetas del camino de la ruta relativa
    for part in parts[:-1]:
        if part in exclude_dirs:
            return True
    return False


def allowed_extension(filename, extensions):
    if not extensions:
        return True
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    norm_exts = [e.lower().lstrip(".") for e in extensions]
    return ext in norm_exts


def allowed_directory(path, include_dirs):
    if not include_dirs or "*" in include_dirs or "." in include_dirs:
        return True

    normalized_path = path.replace("\\", "/")
    parts = normalized_path.split("/")

    for item in parts:
        if item in include_dirs:
            return True
    return False


# =============================================================
# PROCESO PRINCIPAL
# =============================================================

def filter_project():
    print_log("\n====================================")
    print_log("Inicio knowledge_filter (v1.7)")

    # workspace_root: única referencia fija, punto de entrada del
    # workspace de conocimiento. La identidad del proyecto concreto
    # (workspace_path) se resuelve exclusivamente desde project.conf,
    # nunca hardcodeada aquí.
    workspace_root = os.path.expanduser("~/rag_workspace")

    project_name = resolve_project_dir(workspace_root)
    if not project_name:
        print_log(
            "❌ Error: no se pudo determinar el proyecto a procesar. "
            "Indicalo como argumento (python3 knowledge_filter.py <ProjectName>), "
            "definí la variable de entorno RAG_PROJECT, o asegurate de que "
            "el workspace contenga un único proyecto con project.conf."
        )
        return

    project_file = os.path.join(workspace_root, project_name, "project.conf")
    project = load_config(project_file)

    workspace = os.path.expanduser(project.get("workspace_path", ""))
    if not workspace:
        print_log("❌ Error: 'workspace_path' no está definido en project.conf")
        return

    policy_file = os.path.join(workspace, "knowledge_policy.conf")
    policy = parse_policy_conf(policy_file)

    raw_source_path = project.get("source_path")
    source_path = normalize_wsl_path(raw_source_path)

    destination = os.path.join(
        workspace,
        project.get("source_path_local", "source")
    )

    include_dirs = policy.get("include_dirs", [])
    include_extensions = policy.get("include_extensions", [])
    include_files = policy.get("include_files", [])
    exclude_dirs = policy.get("exclude_dirs", [])
    exclude_extensions = policy.get("exclude_extensions", [])

    print_log(f"Origen raw : {raw_source_path}")
    print_log(f"Origen WSL : {source_path}")
    print_log(f"Destino    : {destination}")
    print_log("--- Reglas cargadas desde policy ---")
    print_log(f"Carpetas autorizadas : {include_dirs}")
    print_log(f"Ext. autorizadas     : {include_extensions}")
    print_log(f"Carpetas excluidas   : {exclude_dirs}")
    print_log(f"Ext. excluidas       : {exclude_extensions}")
    print_log("------------------------------------\n")

    if not os.path.exists(source_path):
        print_log(f"❌ Error: La ruta de origen no existe: {source_path}")
        return

    # Limpiar destino completamente
    expected_name = project.get("source_path_local", "source")
    if os.path.exists(destination):
        if not is_safe_to_delete(destination, workspace, expected_name):
            print_log(
                f"❌ Error: abortando por seguridad. '{destination}' no cumple "
                f"la validación (debe estar dentro de '{workspace}' y "
                f"llamarse '{expected_name}'). No se ejecuta rmtree()."
            )
            return
        shutil.rmtree(destination)

    os.makedirs(destination, exist_ok=True)

    total = 0
    copied = 0
    excluded = 0

    print_log("🔍 Escaneando y filtrando archivos...")

    for root, dirs, files in os.walk(source_path):
        # Podado dinámico de os.walk según exclude_dirs de la política
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for filename in files:
            total += 1

            full_path = os.path.join(root, filename)
            relative = os.path.relpath(full_path, source_path)

            # 1. Filtro de carpetas excluidas por política
            if is_excluded_directory(relative, exclude_dirs):
                excluded += 1
                continue

            # 2. Filtro de carpetas o archivos de raíz autorizados por política
            if (
                filename not in include_files
                and not allowed_directory(relative, include_dirs)
            ):
                excluded += 1
                continue

            # 3. Filtro de extensión autorizada por política
            if not allowed_extension(filename, include_extensions):
                excluded += 1
                continue

            # 4. Filtro de extensión excluida por política
            ext = os.path.splitext(filename)[1].lower().lstrip(".")
            norm_excludes = [e.lower().lstrip(".") for e in exclude_extensions]
            if ext in norm_excludes:
                excluded += 1
                continue

            destination_file = os.path.join(destination, relative)
            os.makedirs(os.path.dirname(destination_file), exist_ok=True)

            shutil.copy2(full_path, destination_file)
            copied += 1
            print_log(f"   [{copied}] COPIADO: {relative}")

    print_log("\n------------------------------------")
    print_log(f"Archivos analizados : {total}")
    print_log(f"Archivos copiados   : {copied}")
    print_log(f"Archivos excluidos  : {excluded}")
    print_log("Fin knowledge_filter")
    print_log("====================================")


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":
    filter_project()
