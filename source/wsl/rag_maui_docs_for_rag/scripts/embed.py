#!/usr/bin/env python3
"""
===============================================================================
Proyecto : Arquitectura_RAG_Termica
Módulo  : embed.py
Versión : 2.2
Fecha   : 2026-08-12

Descripción
-----------
Generador y reconciliador de embeddings para la Knowledge Source del proyecto.

Evolución de versiones
----------------------
v1.9
    - Formateo semántico enriquecido.
    - Sanitización Unicode.
    - Cliente HTTP mediante requests.
    - Validación de respuestas de Ollama.
    - Pacing/sleep para controlar la carga durante la vectorización.

v2.0
    - Implementación del contrato de identidad definido por ADR-012.
    - Separación entre identidad de entidad y estado de contenido.
    - Incorporación de record_id.
    - Incorporación de content_hash.
    - Reconciliación de entidades nuevas, sin cambios, modificadas y eliminadas.
    - Persistencia atómica de embeddings.jsonl.

v2.1
    - Incorporación de embedding_model.
    - Incorporación de embedding_dimension.
    - Validación de reutilización considerando modelo y vector.
    - Detección preventiva de duplicados de identidad en la Knowledge Source.

v2.2
    - Validación de duplicados también en el índice vectorial existente.
    - Validación explícita de dimensión del embedding.
    - Diagnóstico más preciso de las causas de regeneración.
    - Persistencia atómica reforzada mediante flush() + fsync() + os.replace().
    - Validación de registros vectoriales antes de permitir su reutilización.
    - Eliminación de artefactos de generación de texto ajenos al código.
    - Mantiene la compatibilidad conceptual con el contrato ADR-012.

Contrato arquitectónico ADR-012
--------------------------------
IDENTIDAD:

    canonical_key =
        source_type ::
        namespace ::
        entity_type ::
        name ::
        file

    record_id = SHA256(canonical_key)

ESTADO:

    content_hash = SHA256(content_normalizado)

El record_id NO depende de:
    - métodos
    - propiedades
    - parámetros
    - contenido textual
    - source_line
    - source_path

El content_hash representa el estado de la representación textual
que realmente será enviada al modelo de embeddings.

Reconciliación
--------------
    1. NUEVO
       record_id no existe en el índice anterior.

    2. SIN_CAMBIOS
       record_id existe y:
       - content_hash coincide
       - embedding_model coincide
       - embedding existe
       - embedding_dimension coincide con el vector

    3. MODIFICADO
       record_id existe pero cambió:
       - contenido
       - modelo
       - dimensión
       - o el vector almacenado no es válido

    4. ELIMINADO
       record_id existe en el índice anterior pero ya no existe
       en la Knowledge Source actual.

Persistencia
------------
La generación completa se realiza sobre memoria.

embeddings.jsonl solamente se reemplaza después de terminar
exitosamente la reconciliación.

El nuevo archivo se escribe primero como:

    embeddings.tmp

Luego se ejecuta:

    flush()
    fsync()
    os.replace()

Esto evita dejar un embeddings.jsonl parcialmente escrito.

===============================================================================
"""

import sys
import os
import json
import time
import hashlib
from pathlib import Path

import requests


# ==============================================================================
# CONFIGURACIÓN GENERAL
# ==============================================================================

SCRIPT_VERSION = "2.2"

# Tipo lógico de Knowledge Source utilizado en ADR-012.
#
# IMPORTANTE:
# Este valor forma parte de la identidad canónica del record_id.
# No debe modificarse arbitrariamente después de crear el índice.
LOGICAL_SOURCE_TYPE = "symbols"

DEFAULT_MODEL = "nomic-embed-text"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/embeddings"

DEFAULT_CPU_LOAD_TARGET = 40.0
DEFAULT_MAX_SLEEP = 1.5

EMBEDDING_TIMEOUT = 60


# ==============================================================================
# RESOLUCIÓN DE CONFIGURACIÓN
# ==============================================================================

def load_kv_config(config_path: Path) -> dict:
    """
    Lee un archivo de configuración simple:

        clave = valor

    Ignora:
        - líneas vacías
        - comentarios
        - líneas sin '='
    """

    config = {}

    if not config_path.exists():
        return config

    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            config[key.strip()] = value.strip()

    return config


def resolve_workspace() -> Path:
    """
    Resuelve la raíz del workspace mediante project.conf.

    Si project.conf no define workspace_dir se utiliza:

        ~/rag_workspace/MauiAppGestorMovil
    """

    script_dir = Path(__file__).resolve().parent

    project_conf = script_dir / "project.conf"

    config = load_kv_config(project_conf)

    workspace_str = config.get(
        "workspace_dir",
        "~/rag_workspace/MauiAppGestorMovil"
    )

    return Path(os.path.expanduser(workspace_str)).resolve()


# ==============================================================================
# SANITIZACIÓN
# ==============================================================================

def sanitize_text(text: str) -> str:
    """
    Normaliza el texto utilizado para generar el embedding.

    Operaciones:
        1. Elimina caracteres NUL.
        2. Convierte espacios no separables a espacios normales.
        3. Elimina espacios exteriores.
        4. Compacta secuencias de espacios.

    El resultado es determinista.
    """

    if not text:
        return ""

    text = text.replace("\x00", "")
    text = text.replace("\xa0", " ")
    text = text.strip()

    return " ".join(text.split())


# ==============================================================================
# FORMATEO SEMÁNTICO
# ==============================================================================

def format_symbols_item(item: dict) -> str:
    """
    Convierte una entidad estructurada de symbols_raw.jsonl
    en una representación textual semánticamente enriquecida.

    Se conserva la información estructural relevante de v1.9:

        - tipo de entidad
        - nombre
        - namespace
        - archivo
        - acceso
        - modificadores
        - herencia
        - interfaces
        - propiedades
        - métodos
        - parámetros
        - tipos de retorno
        - async
    """

    entity_type = item.get("entity_type", "entidad").capitalize()
    name = item.get("name", "Desconocido")
    namespace = item.get("namespace") or "SinNamespace"
    file_path = item.get("file", "Desconocido")
    access = item.get("access", "public")

    modifiers = item.get("modifiers", [])
    inherits = item.get("inherits")
    implements = item.get("implements", [])

    methods = item.get("methods", [])
    properties = item.get("properties", [])

    # --------------------------------------------------------------------------
    # Encabezado
    # --------------------------------------------------------------------------

    mod_str = ""

    if modifiers:
        mod_str = (
            f" Modificadores: {', '.join(modifiers)}."
        )

    header = (
        f"{entity_type} {name}. "
        f"Namespace: {namespace}. "
        f"Archivo fuente: {file_path}. "
        f"Acceso: {access}."
        f"{mod_str}"
    )

    parts = [header]

    # --------------------------------------------------------------------------
    # Herencia
    # --------------------------------------------------------------------------

    if inherits:
        parts.append(
            f"Hereda de: {inherits}."
        )

    # --------------------------------------------------------------------------
    # Interfaces
    # --------------------------------------------------------------------------

    if implements:
        parts.append(
            f"Implementa: {', '.join(implements)}."
        )

    # --------------------------------------------------------------------------
    # Propiedades
    # --------------------------------------------------------------------------

    if properties:

        property_details = []

        for prop in properties:

            if not isinstance(prop, dict):
                continue

            prop_name = prop.get("name")

            if not prop_name:
                continue

            prop_type = prop.get("type", "var")
            prop_access = prop.get("access", "public")

            property_details.append(
                f"{prop_access} {prop_type} {prop_name}"
            )

        if property_details:
            parts.append(
                f"Propiedades: {'; '.join(property_details)}."
            )

    # --------------------------------------------------------------------------
    # Métodos
    # --------------------------------------------------------------------------

    if methods:

        method_details = []

        for method in methods:

            if not isinstance(method, dict):
                continue

            method_name = method.get("name")

            if not method_name:
                continue

            method_access = method.get("access", "public")
            return_type = method.get("return_type", "void")

            async_prefix = ""

            if method.get("is_async"):
                async_prefix = "async "

            # --------------------------------------------------------------
            # Parámetros
            # --------------------------------------------------------------

            parameters = method.get("parameters", [])

            parameter_strings = []

            for parameter in parameters:

                if not isinstance(parameter, dict):
                    continue

                parameter_name = parameter.get("name")

                if not parameter_name:
                    continue

                parameter_type = parameter.get(
                    "type",
                    "object"
                )

                parameter_strings.append(
                    f"{parameter_type} {parameter_name}"
                )

            parameter_text = ", ".join(parameter_strings)

            method_details.append(
                f"{method_access} "
                f"{async_prefix}"
                f"{return_type} "
                f"{method_name}"
                f"({parameter_text})"
            )

        if method_details:
            parts.append(
                f"Métodos: {'; '.join(method_details)}."
            )

    return " ".join(parts)


# ==============================================================================
# IDENTIDAD CANÓNICA - ADR-012
# ==============================================================================

def generate_record_id(
    item: dict,
    source_type: str
) -> str:
    """
    Genera la identidad estable de una entidad.

    canonical_key:

        source_type::namespace::entity_type::name::file

    record_id:

        SHA256(canonical_key)

    El contenido descriptivo NO forma parte de la identidad.
    """

    namespace = item.get("namespace") or "SinNamespace"
    entity_type = item.get("entity_type") or "entidad"
    name = item.get("name") or "Desconocido"
    file_ref = item.get("file") or "Desconocido"

    canonical_key = (
        f"{source_type}::"
        f"{namespace}::"
        f"{entity_type}::"
        f"{name}::"
        f"{file_ref}"
    )

    return hashlib.sha256(
        canonical_key.encode("utf-8")
    ).hexdigest()


# ==============================================================================
# ESTADO DE CONTENIDO - ADR-012
# ==============================================================================

def generate_content_hash(
    sanitized_content: str
) -> str:
    """
    Calcula el hash del contenido normalizado que será
    enviado al modelo de embeddings.
    """

    return hashlib.sha256(
        sanitized_content.encode("utf-8")
    ).hexdigest()


# ==============================================================================
# PACING
# ==============================================================================

def calculate_sleep_time(
    cpu_load_target: float,
    max_sleep: float
) -> float:
    """
    Calcula el tiempo de pausa entre solicitudes a Ollama.

    Mantiene el mecanismo de pacing heredado de v1.9.
    """

    if cpu_load_target <= 0:
        return 0.0

    factor = max(
        0.1,
        min(
            1.0,
            (100.0 - cpu_load_target) / 100.0
        )
    )

    return round(
        max_sleep * factor,
        2
    )


# ==============================================================================
# OLLAMA
# ==============================================================================

def get_embedding(
    text: str,
    model: str,
    ollama_url: str
) -> list:
    """
    Obtiene un embedding desde Ollama.

    Valida:

        - HTTP exitoso
        - JSON válido
        - existencia de 'embedding'
        - tipo lista
        - lista no vacía
        - valores numéricos

    Devuelve:

        list[float]
    """

    payload = {
        "model": model,
        "prompt": text
    }

    try:

        response = requests.post(
            ollama_url,
            json=payload,
            timeout=EMBEDDING_TIMEOUT
        )

        response.raise_for_status()

        response_data = response.json()

        if not isinstance(response_data, dict):
            raise ValueError(
                "La respuesta de Ollama no es un objeto JSON."
            )

        if "embedding" not in response_data:
            raise ValueError(
                "La respuesta de Ollama no contiene "
                "el campo 'embedding'."
            )

        embedding = response_data["embedding"]

        if not isinstance(embedding, list):
            raise ValueError(
                "El embedding devuelto no es una lista."
            )

        if not embedding:
            raise ValueError(
                "Ollama devolvió un embedding vacío."
            )

        if not all(
            isinstance(value, (int, float))
            for value in embedding
        ):
            raise ValueError(
                "El embedding contiene valores no numéricos."
            )

        vector = [
            float(value)
            for value in embedding
        ]

        return vector

    except requests.exceptions.RequestException as exc:

        print(
            f"[ERROR HTTP] Fallo de comunicación con Ollama: {exc}",
            file=sys.stderr
        )

        raise

    except Exception as exc:

        print(
            f"[ERROR VALIDACIÓN] Fallo al procesar embedding: {exc}",
            file=sys.stderr
        )

        raise


# ==============================================================================
# VALIDACIÓN DE REGISTROS VECTORIALES
# ==============================================================================

def is_valid_embedding_record(
    record: dict,
    expected_model: str
) -> tuple[bool, str]:
    """
    Determina si un registro existente puede reutilizar su vector.

    Retorna:

        (True, "")
    
    o:

        (False, motivo)
    """

    if not isinstance(record, dict):
        return False, "registro no es un objeto JSON"

    stored_hash = record.get("content_hash")

    if not stored_hash:
        return False, "falta content_hash"

    stored_model = record.get("embedding_model")

    if stored_model != expected_model:
        return False, "modelo de embedding diferente"

    vector = record.get("embedding")

    if not isinstance(vector, list):
        return False, "embedding no es una lista"

    if not vector:
        return False, "embedding vacío"

    if not all(
        isinstance(value, (int, float))
        for value in vector
    ):
        return False, "embedding contiene valores no numéricos"

    stored_dimension = record.get(
        "embedding_dimension"
    )

    if stored_dimension is not None:

        if stored_dimension != len(vector):
            return (
                False,
                "embedding_dimension no coincide con el vector"
            )

    return True, ""


# ==============================================================================
# CARGA DEL ÍNDICE EXISTENTE
# ==============================================================================

def load_existing_index(
    embeddings_path: Path
) -> dict:
    """
    Carga embeddings.jsonl como:

        record_id -> registro

    También detecta duplicados de record_id.

    Un índice existente con identidades duplicadas se considera
    inconsistente y provoca aborto antes de modificar el archivo.
    """

    index = {}

    if not embeddings_path.exists():
        return index

    with open(
        embeddings_path,
        "r",
        encoding="utf-8"
    ) as f:

        for line_num, line in enumerate(f, 1):

            line = line.strip()

            if not line:
                continue

            try:

                record = json.loads(line)

            except json.JSONDecodeError as exc:

                raise RuntimeError(
                    f"embeddings.jsonl contiene JSON inválido "
                    f"en línea {line_num}: {exc}"
                )

            if not isinstance(record, dict):

                raise RuntimeError(
                    f"embeddings.jsonl contiene un registro "
                    f"no válido en línea {line_num}."
                )

            record_id = record.get("record_id")

            if not record_id:

                raise RuntimeError(
                    f"embeddings.jsonl contiene un registro "
                    f"sin record_id en línea {line_num}."
                )

            if record_id in index:

                raise RuntimeError(
                    "Se detectó record_id duplicado en "
                    f"embeddings.jsonl: {record_id} "
                    f"(línea {line_num})."
                )

            index[record_id] = record

    return index


# ==============================================================================
# PERSISTENCIA ATÓMICA
# ==============================================================================

def save_index_atomically(
    embeddings_path: Path,
    index_map: dict
):
    """
    Persiste embeddings.jsonl de forma atómica.

    Secuencia:

        1. Crear embeddings.tmp
        2. Escribir todos los registros
        3. flush()
        4. fsync()
        5. os.replace()

    El archivo destino anterior no se modifica hasta que
    el nuevo archivo ha sido escrito correctamente.
    """

    embeddings_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_path = embeddings_path.with_suffix(
        ".tmp"
    )

    try:

        with open(
            temp_path,
            "w",
            encoding="utf-8"
        ) as f:

            for record in index_map.values():

                f.write(
                    json.dumps(
                        record,
                        ensure_ascii=False
                    )
                    + "\n"
                )

            f.flush()

            os.fsync(
                f.fileno()
            )

        os.replace(
            temp_path,
            embeddings_path
        )

    except Exception:

        if temp_path.exists():

            try:
                temp_path.unlink()
            except OSError:
                pass

        raise


# ==============================================================================
# LECTURA Y VALIDACIÓN DE KNOWLEDGE SOURCE
# ==============================================================================

def load_raw_records(
    symbols_raw_path: Path,
    source_type: str
) -> list:
    """
    Carga symbols_raw.jsonl.

    Además de leer los registros, calcula preventivamente
    sus record_id y detecta colisiones de identidad.

    Si existe una colisión:

        - se informa línea
        - se informa entidad
        - se aborta
        - embeddings.jsonl no es modificado
    """

    records = []

    seen_ids = {}

    with open(
        symbols_raw_path,
        "r",
        encoding="utf-8"
    ) as f:

        for line_num, line in enumerate(f, 1):

            line = line.strip()

            if not line:
                continue

            try:

                item = json.loads(line)

            except json.JSONDecodeError as exc:

                raise RuntimeError(
                    f"JSON inválido en Knowledge Source "
                    f"línea {line_num}: {exc}"
                )

            if not isinstance(item, dict):

                raise RuntimeError(
                    f"La línea {line_num} de la Knowledge Source "
                    "no contiene un objeto JSON."
                )

            record_id = generate_record_id(
                item,
                source_type
            )

            if record_id in seen_ids:

                previous_line = seen_ids[record_id]

                entity_type = item.get(
                    "entity_type",
                    "entidad"
                )

                name = item.get(
                    "name",
                    "desconocido"
                )

                namespace = item.get(
                    "namespace",
                    "SinNamespace"
                )

                file_ref = item.get(
                    "file",
                    "desconocido"
                )

                raise RuntimeError(
                    "\n"
                    "[ERROR CRÍTICO] Colisión de identidad.\n"
                    f"  record_id : {record_id}\n"
                    f"  entidad   : {entity_type} {name}\n"
                    f"  namespace : {namespace}\n"
                    f"  archivo   : {file_ref}\n"
                    f"  línea     : {line_num}\n"
                    f"  anterior  : línea {previous_line}\n"
                    "\n"
                    "La Knowledge Source contiene dos entidades "
                    "con la misma identidad canónica."
                )

            seen_ids[record_id] = line_num

            records.append(item)

    return records


# ==============================================================================
# CONSTRUCCIÓN DE REGISTRO VECTORIAL
# ==============================================================================

def build_vector_record(
    item: dict,
    source_type: str,
    content: str,
    content_hash: str,
    model: str,
    vector: list
) -> dict:
    """
    Construye un registro homogéneo para embeddings.jsonl.
    """

    file_ref = item.get(
        "file",
        "Desconocido"
    )

    source_path = item.get(
        "source_path",
        file_ref
    )

    source_line = item.get(
        "source_line",
        1
    )

    record_id = generate_record_id(
        item,
        source_type
    )

    return {
        "record_id": record_id,
        "content_hash": content_hash,
        "source_type": source_type,
        "file": file_ref,
        "source_path": source_path,
        "source_line": source_line,
        "content": content,
        "embedding_model": model,
        "embedding_dimension": len(vector),
        "embedding": vector
    }


# ==============================================================================
# MAIN
# ==============================================================================

def main():

    script_dir = Path(__file__).resolve().parent

    # --------------------------------------------------------------------------
    # Configuración
    # --------------------------------------------------------------------------

    embed_conf_path = script_dir / "embed.conf"

    embed_conf = load_kv_config(
        embed_conf_path
    )

    model = embed_conf.get(
        "model",
        DEFAULT_MODEL
    )

    ollama_url = embed_conf.get(
        "ollama_url",
        DEFAULT_OLLAMA_URL
    )

    cpu_load_target = float(
        embed_conf.get(
            "cpu_load",
            str(DEFAULT_CPU_LOAD_TARGET)
        )
    )

    max_sleep = float(
        embed_conf.get(
            "max_sleep",
            str(DEFAULT_MAX_SLEEP)
        )
    )

    sleep_time = calculate_sleep_time(
        cpu_load_target,
        max_sleep
    )

    # --------------------------------------------------------------------------
    # Rutas
    # --------------------------------------------------------------------------

    workspace_dir = resolve_workspace()

    symbols_raw_path = (
        workspace_dir
        / "knowledge"
        / "symbols"
        / "symbols_raw.jsonl"
    )

    embeddings_path = (
        workspace_dir
        / "knowledge"
        / "embeddings"
        / "embeddings.jsonl"
    )

    # --------------------------------------------------------------------------
    # Validación de Knowledge Source
    # --------------------------------------------------------------------------

    if not symbols_raw_path.exists():

        print(
            "[ERROR] No existe la Knowledge Source primaria:",
            file=sys.stderr
        )

        print(
            f"        {symbols_raw_path}",
            file=sys.stderr
        )

        return 1

    # --------------------------------------------------------------------------
    # Inicio
    # --------------------------------------------------------------------------

    print(
        f"=== Vectorización embed.py v{SCRIPT_VERSION} ==="
    )

    print(
        "Contrato de identidad : ADR-012"
    )

    print(
        f"Knowledge Source       : {symbols_raw_path}"
    )

    print(
        f"Artefacto destino      : {embeddings_path}"
    )

    print(
        f"Source Type            : {LOGICAL_SOURCE_TYPE}"
    )

    print(
        f"Modelo                 : {model}"
    )

    print(
        f"Pacing por entidad     : {sleep_time}s"
    )

    # --------------------------------------------------------------------------
    # 1. Cargar índice anterior
    # --------------------------------------------------------------------------

    try:

        existing_index = load_existing_index(
            embeddings_path
        )

    except Exception as exc:

        print(
            f"[ERROR] No se pudo cargar el índice existente: {exc}",
            file=sys.stderr
        )

        return 1

    print(
        "Registros vectoriales "
        f"en índice previo      : {len(existing_index)}"
    )

    # --------------------------------------------------------------------------
    # 2. Cargar Knowledge Source
    # --------------------------------------------------------------------------

    try:

        raw_records = load_raw_records(
            symbols_raw_path,
            LOGICAL_SOURCE_TYPE
        )

    except Exception as exc:

        print(
            f"[ERROR] Knowledge Source inválida: {exc}",
            file=sys.stderr
        )

        print(
            "No se realizaron cambios en embeddings.jsonl.",
            file=sys.stderr
        )

        return 1

    print(
        "Entidades leídas       : "
        f"{len(raw_records)}"
    )

    # --------------------------------------------------------------------------
    # 3. Reconciliación
    # --------------------------------------------------------------------------

    updated_index = {}

    stats = {
        "nuevos": 0,
        "sin_cambios": 0,
        "modificados": 0,
        "eliminados": 0
    }

    for item in raw_records:

        # ----------------------------------------------------------------------
        # Identidad
        # ----------------------------------------------------------------------

        record_id = generate_record_id(
            item,
            LOGICAL_SOURCE_TYPE
        )

        # ----------------------------------------------------------------------
        # Representación
        # ----------------------------------------------------------------------

        formatted_content = format_symbols_item(
            item
        )

        sanitized_content = sanitize_text(
            formatted_content
        )

        content_hash = generate_content_hash(
            sanitized_content
        )

        file_ref = item.get(
            "file",
            "Desconocido"
        )

        entity_name = item.get(
            "name",
            "Desconocido"
        )

        # ----------------------------------------------------------------------
        # CASO 1 - NUEVO
        # ----------------------------------------------------------------------

        if record_id not in existing_index:

            print(
                f"[NUEVO] {entity_name} ({file_ref})"
            )

            try:

                vector = get_embedding(
                    sanitized_content,
                    model,
                    ollama_url
                )

            except Exception:

                print(
                    "Proceso abortado. "
                    "embeddings.jsonl no fue modificado.",
                    file=sys.stderr
                )

                return 1

            record = build_vector_record(
                item=item,
                source_type=LOGICAL_SOURCE_TYPE,
                content=sanitized_content,
                content_hash=content_hash,
                model=model,
                vector=vector
            )

            updated_index[record_id] = record

            stats["nuevos"] += 1

            if sleep_time > 0:
                time.sleep(sleep_time)

            continue

        # ----------------------------------------------------------------------
        # Registro existente
        # ----------------------------------------------------------------------

        previous_record = existing_index[
            record_id
        ]

        previous_hash = previous_record.get(
            "content_hash"
        )

        is_same_content = (
            previous_hash == content_hash
        )

        is_valid_vector, validation_reason = (
            is_valid_embedding_record(
                previous_record,
                model
            )
        )

        # ----------------------------------------------------------------------
        # CASO 2 - SIN CAMBIOS
        # ----------------------------------------------------------------------

        if (
            is_same_content
            and is_valid_vector
        ):

            previous_vector = previous_record[
                "embedding"
            ]

            record = build_vector_record(
                item=item,
                source_type=LOGICAL_SOURCE_TYPE,
                content=sanitized_content,
                content_hash=content_hash,
                model=model,
                vector=previous_vector
            )

            updated_index[record_id] = record

            stats["sin_cambios"] += 1

            continue

        # ----------------------------------------------------------------------
        # CASO 3 - MODIFICADO
        # ----------------------------------------------------------------------

        if not is_same_content:

            reason = "content_hash cambió"

        else:

            reason = validation_reason

        print(
            f"[MODIFICADO] {entity_name} ({file_ref}) "
            f"-> {reason}"
        )

        try:

            vector = get_embedding(
                sanitized_content,
                model,
                ollama_url
            )

        except Exception:

            print(
                "Proceso abortado. "
                "embeddings.jsonl no fue modificado.",
                file=sys.stderr
            )

            return 1

        record = build_vector_record(
            item=item,
            source_type=LOGICAL_SOURCE_TYPE,
            content=sanitized_content,
            content_hash=content_hash,
            model=model,
            vector=vector
        )

        updated_index[record_id] = record

        stats["modificados"] += 1

        if sleep_time > 0:
            time.sleep(sleep_time)

    # --------------------------------------------------------------------------
    # 4. CASO 4 - ELIMINADOS
    # --------------------------------------------------------------------------

    previous_ids = set(
        existing_index.keys()
    )

    current_ids = set(
        updated_index.keys()
    )

    eliminated_ids = (
        previous_ids - current_ids
    )

    stats["eliminados"] = len(
        eliminated_ids
    )

    # --------------------------------------------------------------------------
    # 5. Persistencia atómica
    # --------------------------------------------------------------------------

    try:

        save_index_atomically(
            embeddings_path,
            updated_index
        )

    except Exception as exc:

        print(
            f"[ERROR] Fallo durante persistencia atómica: {exc}",
            file=sys.stderr
        )

        print(
            "El índice anterior debería permanecer intacto.",
            file=sys.stderr
        )

        return 1

    # --------------------------------------------------------------------------
    # 6. Resumen
    # --------------------------------------------------------------------------

    print()

    print(
        "=== Resumen de Reconciliación ==="
    )

    print(
        f"Total procesados : {len(updated_index)}"
    )

    print(
        f"  Nuevos         : {stats['nuevos']}"
    )

    print(
        f"  Sin Cambios    : {stats['sin_cambios']}"
    )

    print(
        f"  Modificados    : {stats['modificados']}"
    )

    print(
        f"  Eliminados     : {stats['eliminados']}"
    )

    print()

    print(
        f"Vectorización embed.py v{SCRIPT_VERSION} "
        "completada exitosamente."
    )

    return 0


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":

    sys.exit(
        main()
    )
