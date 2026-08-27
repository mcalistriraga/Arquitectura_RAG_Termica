# 06 — Pruebas y Validación del Sistema

**Fecha:** 26 de agosto de 2026
**Versión:** 0.5.1
**Estado:** Consolidado / Documentación oficial
**Módulo:** Calidad & Validación / Suite de Pruebas Integradas
**Propósito:** Documentar la estrategia de validación técnica, las pruebas de integración del pipeline RAG, la verificación de la extracción de símbolos (KS2), la reconciliación vectorial, las pruebas de aborto térmico, los límites de la validación actual y la deuda técnica identificada.

---

> **Resumen ejecutivo:**  
> La validación de **Arquitectura_RAG_Termica** (v0.5.1) se ha ejecutado bajo un enfoque bottom-up en un entorno de hardware limitado (AMD FX-6300, 16 GB RAM). El ciclo de preparación de conocimiento **KS2** (`knowledge_filter.py` v1.7, `symbols_extractor.py` v1.1, `csharp_parser.py` v2.1.5) y la reconciliación vectorial (`embed.py`) han sido completamente validados de punta a punta sobre el Target Project **MauiAppGestorMovil**.  
>  
> **Aviso de Alcance y Deuda Técnica:** La versión v0.5 previa en GitHub cuenta con validación end-to-end completa del pipeline de consulta (`query.py`). Sin embargo, en esta versión v0.5.1, la integración aguas abajo en `query.py` consumiendo los nuevos símbolos enriquecidos y la incorporación de parsers adicionales (como el parser CSS) **quedan registradas como deuda técnica pendiente para la siguiente iteración**, siendo la prioridad inmediata la sincronización de estos cambios congelados en GitHub antes de abordar la validación integral del motor de consultas.

---

## 1. Introducción y estrategia de pruebas

Durante el desarrollo del proyecto se realizaron pruebas progresivas e independientes para validar cada módulo antes de integrar el pipeline completo:

```text
 Sensores Físicos (Windows)
           │
           ▼
 LibreHardwareMonitor / export_temp_server.py (Flask :5005)
           │
           ▼
 thermal_watchdog.py (Supervisión continua & pkill)
           │
           ▼
 KS2 Pipeline (knowledge_filter v1.7 ──> symbols_extractor v1.1 / csharp_parser v2.1.5) [VALIDADO]
           │
           ▼
 Indexación Vectorial (embed.py - nomic-embed-text) [VALIDADO]
           │
           ▼
 Motor de Consultas (query.py ──> logger.py ──> llm_backend.py) [DEUDA PENDIENTE INTEGRACIÓN RICA]
           │
           ▼
 Backends de Inferencia (LOCAL: Ollama / CLOUD: OpenRouter) [VALIDADO EN BASE v0.5]
```

Este enfoque permitió aislar incidencias, garantizar trazabilidad mediante la carpeta `docs/pruebas/` y comprobar el rendimiento sin comprometer la integridad térmica del hardware.

---

## 2. Entorno de hardware y software de prueba

### Hardware de referencia (PC Manuel C)
```text
CPU:               AMD FX-6300 Six-Core Processor (3.50 GHz)
RAM:               16 GB DDR3
Almacenamiento:    SSD Patriot 480 GB (SO) + HDD 1 TB (Data)
GPU:               AMD Radeon R7 200 Series (Sin aceleración CUDA/IA)
Sistema Operativo: Windows 10 Pro + WSL2 Ubuntu 24.04 LTS
```

### Matriz de componentes evaluados

| Componente | Versión / Tecnología | Entorno | Alcance de Validación v0.5.1 |
| :--- | :--- | :--- | :---: |
| **Telemetría Térmica** | `export_temp_server.py` (Flask 5005) | Windows | ✅ Validado |
| **Supervisión Daemon** | `thermal_watchdog.py` | WSL2 (`~/rag_maui_docs_for_rag/scripts`) | ✅ Validado |
| **Filtrado Workspace** | `knowledge_filter.py` (v1.7) | WSL2 (`~/rag_maui_docs_for_rag/scripts`) | ✅ Validado |
| **Extractor de Símbolos** | `symbols_extractor.py` (v1.1) | WSL2 (`~/rag_maui_docs_for_rag/scripts`) | ✅ Validado |
| **Parser C# / MAUI** | `csharp_parser.py` (v2.1.5) | WSL2 (`~/rag_maui_docs_for_rag/scripts/parsers`) | ✅ Validado (9/9 PASS) |
| **Parser CSS / Otros** | `css_parser.py` | WSL2 (`~/rag_maui_docs_for_rag/scripts/parsers`) | ⏳ Pendiente Próxima Versión |
| **Embeddings & Reconciliación** | `embed.py` (`nomic-embed-text`) | WSL2 (`~/rag_maui_docs_for_rag/scripts`) | ✅ Validado |
| **Integración Rica `query.py`** | `query.py` (Consumo EsquemaKS2) | WSL2 (`~/rag_maui_docs_for_rag/scripts`) | ⏳ Pendiente (Validado en base v0.5) |
| **Inferencia Local/Cloud** | `llm_backend.py` (Ollama / OpenRouter) | WSL2 (`localhost:11434` / API) | ✅ Validado |

---

## 3. Validación de la infraestructura de telemetría térmica

### 3.1 Servicio Windows (`export_temp_server.py`)
* **Objetivo:** Verificar la captura de temperatura del procesador y la publicación de la API HTTP.
* **Sensor Validado:** `Nuvoton NCT6776F -> Temperatures -> Temperature #1`.
* **Respuesta HTTP (Puerto 5005):**
  ```json
  {
    "id": 0,
    "Text": "CPU Temperature",
    "Value": 45.0,
    "Min": 38.0,
    "Max": 72.0,
    "timestamp": 1784056081
  }
  ```
* **Verificación de Descubrimiento de IP:** Escritura correcta en `windows_ip.txt` (`192.168.1.37`).

---

### 3.2 Supervisión y Aborto Térmico (`thermal_watchdog.py`)
* **Evidencia Documentada:** `docs/pruebas/2026-07-20_prueba02_backend_local_qwen2.5_abort_termico.md`.
* **Escenario de Prueba:** Carga intensiva continua sobre los 6 núcleos del CPU durante inferencia local con Ollama.
* **Resultado:** Al alcanzar el umbral `TEMP_CRITICAL` (62.0 °C en promedio móvil $N=5$), el *watchdog* ejecutó de forma atómica:
  ```bash
  pkill -f query.py
  ```
* **Trazabilidad:** Registro completo del evento almacenado en `thermal_watchdog_log.txt` confirmando la detención inmediata y el posterior enfriamiento del procesador hasta la zona segura (`< 58.0 °C`).

---

## 4. Validación del ciclo de conocimiento KS2 (21–24 de agosto de 2026)

Se validó end-to-end el subsistema de estructuración de conocimiento (KS2) sobre el Target Project real **MauiAppGestorMovil** (`~/rag_workspace/MauiAppGestorMovil`).

### 4.1 Filtrado de Workspace (`knowledge_filter.py` v1.7)
* **Reglas:** `knowledge_policy.conf` v1.2 (exclusión de `DatosIniciales/` y carpetas `Deprecated`).
* **Seguridad:** Verificación del método `is_safe_to_delete()` antes de la limpieza de directorios.
* **Resultado Obtención:** **141 archivos analizados**, **76 archivos copiados** para procesamiento y **65 archivos excluidos** por política.

---

### 4.2 Extracción de Símbolos (`symbols_extractor.py` v1.1 + `csharp_parser.py` v2.1.5)
* **Mejora Evaluada:** Corrección del parser C# v2.1.5 para la clasificación explícita de constructores (`is_constructor: true`) como `public App()`.
* **Pruebas Unitarias:** Suite `test_parser_v215.py` con **9/9 PASS** (7 tests base + 2 tests específicos de constructores).
* **Resultado de Extracción:** **53 archivos C# procesados**, obteniendo **57 símbolos estructurados** guardados atómicamente en `knowledge/symbols/symbols_raw.jsonl`.

---

### 4.3 Sincronización y Reconciliación Vectorial (`embed.py` - ADR-012)
* **Evidencia Documentada:** `docs/pruebas/2026-08-12_prueba05_adr012_reconciliacion_embeddings.md`.
* **Verificación Aritmética:**
  * Índice previo: 63 registros
  * Entidades leídas actuales: 57
  * Registros sin cambios: 14
  * Registros modificados: 43 (actualización de metadata de constructores C# v2.1.5)
  * Registros eliminados: 6 (símbolos provenientes de carpetas marcadas como Deprecated)
  * **Consistencia:** $14 + 43 = 57$ leídos; $57 + 6 = 63$ previos.
* **Resultado:** `embeddings.jsonl` actualizado atómicamente en `knowledge/embeddings/` sin re-vectorización innecesaria.

---

## 5. Delimitación de alcance y Deuda Técnica en `query.py`

Es importante distinguir la frontera entre lo validado en esta versión y los desarrollos pendientes:

1. **Estado del Pipeline en GitHub (Versión Base v0.5):** La versión actualmente publicada en GitHub cuenta con validación funcional de punta a punta desde la ingestión hasta la respuesta final de `query.py` utilizando embeddings estándar.
2. **Estado en Versión v0.5.1 (Actual):** El ciclo de preparación de conocimiento KS2 (`knowledge_filter` v1.7, `symbols_extractor` v1.1, `csharp_parser` v2.1.5 y `embed.py`) está **congelado, probado y verificado al 100%**.
3. **Deuda Técnica Identificada (Próxima Actualización):**
   * **Consumo de Símbolos Ricos en `query.py`:** La adaptación de `query.py` para aprovechar la rica estructura de constructores y metadatos extraídos por KS2 se abordará tras sincronizar estos cambios en GitHub.
   * **Inclusión y Validación de Parsers Adicionales:** El soporte y validación end-to-end de parsers para otros formatos (como el parser CSS) no formó parte del índice actual congelado y queda agendado para la posterior versión del sistema.

---

## 6. Observabilidad y Auditoría (`logger.py`)

Se confirmó que cada ejecución en `query.py` registra de forma independiente la sesión en `query_log.txt`, auditando:
1. Secuencia cronológica de eventos (`INPUT_RECEIVED`, `SEARCH_START`, `LLM_START`, `LLM_DONE`).
2. Tiempos por fase (`EMBEDDING_TIME`, `SEARCH_TIME`, `LLM_TIME`, `PIPELINE_TIME`).
3. Diagnóstico de chunks recuperados mediante la bandera `DEBUG_CHUNKS` y la función `log_debug()`.

---

## 7. Matriz de Estado Final de Pruebas (Al 26 de agosto de 2026)

| Módulo / Prueba | Componente Evaluado | Estado v0.5.1 |
| :--- | :--- | :---: |
| Telemetría Windows | `export_temp_server.py` | ✅ VALIDADO |
| Descubrimiento de IP | `windows_ip.txt` / Fallback Gateway | ✅ VALIDADO |
| Daemon Watchdog | `thermal_watchdog.py` | ✅ VALIDADO |
| Interrupción Preventiva | Aborto `pkill` por sobretemperatura | ✅ VALIDADO |
| Filtrado Workspace | `knowledge_filter.py` (v1.7) | ✅ VALIDADO |
| Extracción Símbolos C# | `symbols_extractor.py` (v1.1) / `csharp_parser.py` (v2.1.5) | ✅ VALIDADO |
| Extracción Parsers Extra | Parser CSS y extensiones secundarias | ⏳ DEUDA PENDIENTE |
| Reconciliación Vectorial | `embed.py` (ADR-012) | ✅ VALIDADO |
| RAG End-to-End Base | `query.py` (Base v0.5 en GitHub) | ✅ VALIDADO |
| RAG Integración Rica KS2 | `query.py` (Consumo de `symbols_raw.jsonl` v2.1.5) | ⏳ DEUDA PENDIENTE |
| Inferencia LOCAL / CLOUD | `llm_backend.py` (Ollama / OpenRouter) | ✅ VALIDADO |
| Auditoría & Observabilidad | `logger.py` (`query_log.txt`) | ✅ VALIDADO |

---

## 8. Conclusión

La suite de validación confirma que **Arquitectura_RAG_Termica** dispone de un subsistema de preparación de conocimiento (KS2) y protección térmica **completamente verificado y predecible**. 

Al haber cerrado el ciclo `knowledge_filter` ➔ `symbols_extractor` ➔ `csharp_parser` ➔ `embed.py` con consistencia matemática exacta sobre **MauiAppGestorMovil**, el sistema queda congelado en v0.5.1 y listo para subir al repositorio GitHub. La integración en `query.py` del esquema rico de símbolos y la validación con parsers adicionales (CSS) se constituyen como la hoja de ruta prioritaria inmediatamente posterior al commit.

