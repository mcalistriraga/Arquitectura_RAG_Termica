# 03 — Pipeline RAG

**Fecha:** 26 de agosto de 2026  
**Versión:** 0.5.1  
**Estado:** Consolidado / Documentación oficial  
**Módulo:** Pipeline RAG / Recuperación y Construcción de Contexto (KS2)  
**Propósito:** Especificación técnica detallada del flujo RAG, filtrado de workspace, extracción determinista de símbolos, persistencia vectorial, capa de consulta e inferencia híbrida.

---

> **Resumen ejecutivo:**  
> El pipeline **RAG (Retrieval-Augmented Generation)** de **Arquitectura_RAG_Termica** constituye el motor funcional del asistente técnico. El sistema procesa la base de conocimiento local mediante un ciclo seguro de filtrado (`knowledge_filter.py` v1.7), extracción atómica de símbolos C#/.NET MAUI (`symbols_extractor.py` v1.1 / `csharp_parser.py` v2.1.5), sincronización de vectores (`embed.py`), recuperación semántica y estructural (`query.py`), delegación de inferencia desacoplada (`llm_backend.py`) y observabilidad continua (`logger.py`).

---

## 1. Introducción

El pipeline **RAG** implementado en este proyecto constituye el núcleo funcional del asistente técnico desarrollado en **Arquitectura_RAG_Termica**.

Su propósito consiste en filtrar y extraer conocimiento desde una base de código y documentación local, construir un contexto técnico enriquecido y delegar la generación de respuestas a un backend de inferencia desacoplado.

Actualmente el pipeline implementa las siguientes etapas principales:

* filtrado y preparación del espacio de trabajo (`knowledge_filter.py`);
* extracción determinista de símbolos de código fuente (KS2);
* ingestión y clasificación documental (`ingest.py`);
* generación de embeddings y reconciliación vectorial (`embed.py`);
* recuperación semántica y selección estructural (`query.py`);
* construcción del contexto y prompt final;
* inferencia desacoplada mediante un modelo de lenguaje (LLM);
* observabilidad granular del pipeline (`logger.py`).

La arquitectura fue diseñada para ejecutarse de forma estable sobre hardware con recursos limitados, separando la preparación del conocimiento, la inferencia y la supervisión térmica.

Actualmente el proyecto soporta dos modalidades de inferencia:

* **Backend LOCAL**, utilizando Ollama.
* **Backend CLOUD**, utilizando OpenRouter.

Esta separación permite mantener exactamente el mismo pipeline RAG independientemente del proveedor encargado de generar la respuesta final.

Es fundamental distinguir entre dos conceptos clave:

* **el asistente técnico**, implementado por la plataforma Arquitectura_RAG_Termica;
* **la base de conocimiento activa (Target Project)**, ubicada aisladamente en `~/rag_workspace/<Proyecto>` con su código fuente y documentación.

En el estado actual del proyecto, la base de conocimiento activa corresponde a una aplicación desarrollada con **.NET MAUI**, utilizada como caso de uso de validación real de punta a punta.

---

## 2. Arquitectura general del pipeline

El flujo integral de ejecución del pipeline se organiza según la siguiente estructura:

```text
                     CÓDIGO FUENTE & DOCUMENTACIÓN (.NET MAUI)
                                         │
                                         ▼
                            knowledge_filter.py (v1.7)
                   (Filtro seguro + Policy config v1.2)
                                         │
                                         ▼
                           symbols_extractor.py (v1.1)
                          + csharp_parser.py (v2.1.5)
                                         │
                                         ├─────────────────────────┐
                                         ▼                         ▼
                                 output_raw.jsonl          symbols_raw.jsonl
                                         │                         │
                                         └────────────┬────────────┘
                                                      ▼
                                           embed.py (nomic-embed-text)
                                            (Reconciliación vectorial)
                                                      │
                                                      ▼
                                              embeddings.jsonl
                                                      │
                                                      ▼
Usuario ───────────────────────────────>           query.py
                                                      │
                                                      ▼
                                          Embedding de la consulta
                                                      │
                                                      ▼
                                       Recuperación semántica & Símbolos
                                                      │
                                                      ▼
                                           Construcción del contexto
                                                      │
                                                      ▼
                                            Construcción del prompt
                                                      │
                                                      ▼
                                             llm_backend.py
                                         ┌────────────┴────────────┐
                                         ▼                         ▼
                                   Backend LOCAL             Backend CLOUD
                                      Ollama                  OpenRouter
                                         └────────────┬────────────┘
                                                      ▼
                                         Respuesta final (en query_log.txt)
```

La supervisión térmica continúa ejecutándose de forma independiente mediante procesos auxiliares (`thermal_watchdog.py`), sin bloquear la lógica funcional del pipeline salvo en condiciones extremas de sobretemperatura.

---

## 3. Preparación del conocimiento y filtrado (KS2)

### 3.1 knowledge_filter.py (v1.7)

`knowledge_filter.py` asegura la preparación del espacio de trabajo evitando incluir archivos duplicados, respaldos o código obsoleto.

Características principales:

* **Autodetección de Workspace:** Resuelve dinámicamente el proyecto activo mediante CLI, variables de entorno `RAG_PROJECT` o la ruta por defecto `~/rag_workspace`.
* **Protección de Destrucción:** Implementa la función `is_safe_to_delete()` antes de invocar limpiezas de directorio para prevenir pérdidas accidentales de datos.
* **Políticas de Exclusión (`knowledge_policy.conf` v1.2):** Excluye automáticamente carpetas de respaldo como `DatosIniciales` y directorios marcados como `Deprecated`.

**Métrica de Validación Real:** Sobre el proyecto .NET MAUI analizó **141 archivos**, de los cuales **76 fueron copiados** para procesamiento y **65 fueron excluidos** por política.

---

### 3.2 Extractor de Símbolos y Parsers (KS2)

El subsistema de extracción estructural analiza el código fuente procesado para generar índices precisos de código:

| Componente | Versión | Responsabilidad |
| :--- | :--- | :--- |
| **`symbols_extractor.py`** | v1.1 | Selección dinámica de parsers por extensión via `importlib` y escritura atómica del archivo de salida. |
| **`csharp_parser.py`** | v2.1.5 | Parser especializado en C#/.NET MAUI con clasificación explícita de constructores (`is_constructor`). |

**Métrica de Validación Real:** Procesó **53 archivos C#**, registrando con precisión **57 símbolos** (clases, métodos, interfaces y constructores como `public App()`) sin falsas clasificaciones.

El resultado se persiste en `symbols_raw.jsonl` dentro del espacio de trabajo.

---

## 4. Ingestión y clasificación documental

### 4.1 ingest.py

`ingest.py` lee los documentos provenientes del filtrado, los clasifica por capa técnica y los estructura en registros individuales para la posterior fragmentación.

#### Tipos de archivos procesados
El pipeline admite múltiples extensiones técnicas:

```text
.cs
.xaml
.md
.json
```

#### Clasificación documental
Durante la ingestión, cada archivo es etiquetado para facilitar su contextualización:

| Ubicación / Estructura detectada | Clasificación asignada |
| :--- | :--- |
| ViewModel | `ViewModel` |
| View / XAML | `UI` |
| Service / API | `Service` |
| Modelo de Datos / Otros | `Model` |

#### Salida generada (`output_raw.jsonl`)
Cada línea contiene la representación de un documento:

```json
{
  "file": "GestionDeProductosViewModel.cs",
  "layer": "ViewModel",
  "content": "..."
}
```

---

## 5. Generación de embeddings y reconciliación

### 5.1 embed.py

`embed.py` transforma el texto y la estructura de símbolos en vectores semánticos utilizando el modelo:

```text
nomic-embed-text
```

ejecutado localmente via Ollama.

#### Resolución Dinámica de Workspace
`embed.py` incorpora la función `resolve_workspace()`, leyendo la clave `workspace_path` desde `~/rag_workspace/<Proyecto>/project.conf`, garantizando consistencia sin rutas estáticas *hardcodeadas*.

#### Reconciliación Atómica de Índices
Para evitar la regeneración redundante de vectores, `embed.py` compara el índice vectorial previo con el contenido procesado actual.

**Resultados de la Reconciliación Validada (24-ago-2026):**

* **Índice previo:** 63 registros.
* **Entidades leídas:** 57.
* **Nuevos:** 0.
* **Sin cambios:** 14.
* **Modificados:** 43 (reflejando las mejoras en la clasificación de constructores de `csharp_parser.py` v2.1.5).
* **Eliminados:** 6 (correspondientes a símbolos de carpetas `Deprecated` o respaldos ahora excluidos).
* **Consistencia aritmética:** $14 + 43 = 57$ entidades leídas; $57 + 6 = 63$ índice previo.

El resultado unificado se almacena atómicamente en `embeddings.jsonl`.

---

## 6. Persistencia e índices documentales

El pipeline utiliza archivos estructurados JSONL para garantizar la transparencia y permitir la inspección directa sin sobrecarga de base de datos externas:

| Archivo Índice | Propósito y Contenido |
| :--- | :--- |
| **`embeddings.jsonl`** | Contiene el mapa de fragmentos de texto, metadatos y vectores flotantes generados por `nomic-embed-text`. |
| **`symbols_raw.jsonl` / `symbols.jsonl`** | Contiene el esquema atómico de los símbolos C# (clases, métodos, firmas, visibilidad, flag de constructor). |

Esta persistencia basada en archivos locales simplifica el despliegue sobre WSL2, reduce el consumo de RAM y facilita la observabilidad manual de los índices.

---

## 7. Motor de consultas (`query.py`)

`query.py` coordina el pipeline durante las consultas del usuario.

Responsabilidades principales:

* recibir la consulta del usuario;
* gestionar la sesión activa;
* generar el embedding de la pregunta mediante `nomic-embed-text`;
* ejecutar la búsqueda por similitud coseno sobre `embeddings.jsonl`;
* seleccionar información de símbolos arquitectónicos desde `symbols_raw.jsonl`;
* construir explícitamente el contexto RAG combinando texto y estructura;
* armar el prompt técnico estandarizado;
* delegar la inferencia al backend seleccionado en `llm_backend.py`;
* registrar métricas y eventos mediante `logger.py`.

El pipeline incluye banderas de depuración como `DEBUG_CHUNKS`, que al ser activadas escriben los fragmentos recuperados directamente en consola y en `query_log.txt` para análisis de diagnóstico.

---

## 8. Recuperación semántica y parámetros de similitud

El cálculo de relevancia entre la consulta del desarrollador y la base vectorial se efectúa mediante **similitud coseno**.

Parámetros de configuración vigentes en el código:

```python
TOP_K = 1
SIM_THRESHOLD = 0.25
```

Estos valores filtran los resultados con baja correlación semántica antes de construir el prompt. El contexto recuperado no se usa solo para diagnóstico, sino que se inyecta directamente en la plantilla de prompt entregada al LLM.

---

## 9. Layer de inferencia desacoplado (`llm_backend.py`)

La generación de respuestas se realiza de forma independiente mediante `llm_backend.py`.

### Backend LOCAL (Ollama)
Endpoint habitual: `http://localhost:11434`

| Rol / Función | Modelo Configurado |
| :--- | :--- |
| **Embeddings** | `nomic-embed-text` |
| **Depuración de Código** | `qwen2.5-coder:1.5b` |
| **Razonamiento & Doc** | `llama3.2:3b` |

### Backend CLOUD (OpenRouter)
Permite enviar el mismo prompt enriquecido a modelos remotos mediante API de alta capacidad sin alterar ninguna fase previa del pipeline de recuperación local.

---

## 10. Observabilidad y registro (`logger.py`)

Cada consulta ejecutada por `query.py` inicia una sesión de auditoría en `query_log.txt`.

Eventos registrados cronológicamente:

```text
INPUT_RECEIVED
EMBEDDING_START
EMBEDDING_OK
SEARCH_START
SEARCH_DONE
LLM_START
LLM_DONE
ANSWER_PRINTED
```

Métricas calculadas por sesión:

* **`EMBEDDING_TIME`:** Latencia de generación del vector de la pregunta.
* **`SEARCH_TIME`:** Latencia del escaneo y cálculo de similitud coseno.
* **`LLM_TIME`:** Tiempo empleado por Ollama u OpenRouter en generar la respuesta.
* **`PIPELINE_TIME`:** Duración total del ciclo end-to-end.

Asimismo, la función genérica `log_debug()` permite que cualquier script (`embed.py`, `symbols_extractor.py`, `query.py`) registre trazabilidad técnica detallada sin ensuciar la salida estándar del usuario.

---

## 11. Protección térmica preventiva (`thermal_watchdog.py`)

El proceso `thermal_watchdog.py` supervisa el estado del CPU de la máquina host (Windows) consultando periódicamente el servidor Flask (`export_temp_server.py`:5005).

Si la temperatura supera los umbrales de seguridad durante la ejecución masiva de embeddings o inferencia pesada, el *watchdog* aborta o detiene preventivamente la tarea en WSL2 para evitar el sobrecalentamiento del equipo anfitrión.

---

## 12. Estado actual de validación

Al **26 de agosto de 2026**, el pipeline RAG y la fuente de símbolos (KS2) presentan el siguiente estado operativo:

* **Ciclo KS2 Congelado:** Ingestión, filtrado (`knowledge_filter` v1.7), extracción (`symbols_extractor` v1.1) y parsing (`csharp_parser` v2.1.5) totalmente validados sobre el repositorio real .NET MAUI.
* **Reconciliación Vectorial Consistente:** Matriz de actualización atómica comprobada en `embed.py` ($14 + 43 = 57$ entidades).
* **Inferencia Híbrida Operativa:** Backend LOCAL (Ollama) y CLOUD (OpenRouter) probados en `llm_backend.py`.
* **Próximo Hito:** Commit de la versión validada en GitHub y posterior integración de la rica estructura de símbolos en la construcción del prompt dentro de `query.py`.

