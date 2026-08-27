# 02 — Arquitectura del Sistema

**Fecha:** 26 de agosto de 2026  
**Versión:** 0.5.1  
**Estado:** Consolidado / Documentación oficial  
**Módulo:** Arquitectura del Sistema / Distribución de Componentes  
**Propósito:** Especificación de la arquitectura híbrida, distribución de responsabilidades en WSL2 y Windows, pipeline de símbolos (KS2), abstracción de inferencia y mecanismos de supervisión térmica.

---

> **Resumen ejecutivo:**  
> La arquitectura de **Arquitectura_RAG_Termica** se organiza como una plataforma híbrida, modular y desacoplada para asistentes técnicos. El sistema separa estrictamente la preparación y filtrado del espacio de trabajo (`knowledge_filter.py`), la extracción determinista de símbolos (`symbols_extractor.py` / `csharp_parser.py`), la sincronización vectorial (`embed.py`), el pipeline de consulta (`query.py`), la abstracción de inferencia (`llm_backend.py`), la observabilidad (`logger.py`) y la protección térmica independiente sobre hardware anfitrión (`thermal_watchdog.py`).

---

## 1. Introducción

La arquitectura de **Arquitectura_RAG_Termica** ha evolucionado desde un sistema orientado exclusivamente a la ejecución local de modelos de lenguaje hacia una arquitectura híbrida, modular y desacoplada, diseñada para servir como plataforma de construcción de asistentes técnicos especializados.

El objetivo principal es separar claramente las distintas responsabilidades del sistema para facilitar su mantenimiento, su evolución y la incorporación de nuevos componentes sin afectar al funcionamiento del pipeline principal.

Actualmente la arquitectura distingue dos niveles claramente diferenciados:

* **La plataforma asistente**, implementada por el proyecto Arquitectura_RAG_Termica.
* **El proyecto técnico asistido**, cuya documentación y código fuente constituyen la base de conocimiento activa utilizada por el pipeline RAG y el extractor de símbolos (KS2).

En el estado actual del proyecto, la base de conocimiento activa corresponde a una aplicación desarrollada con **.NET MAUI**, procesada dinámicamente desde el espacio de trabajo `~/rag_workspace/<Proyecto>`. La arquitectura ha sido diseñada para que dicha base pueda sustituirse posteriormente por la documentación o el código fuente de cualquier otro proyecto, sin modificar el funcionamiento interno del asistente.

La arquitectura continúa organizándose en dos entornos complementarios:

* **Windows**, responsable del acceso al hardware físico y de la publicación de la información térmica mediante un servicio HTTP en Flask.
* **WSL2 Ubuntu**, responsable de la ejecución del pipeline RAG, la filtración del workspace, la extracción atómica de símbolos, la recuperación del conocimiento, la inferencia mediante modelos de lenguaje y la supervisión del sistema.

Uno de los principios arquitectónicos más importantes consiste en la separación entre:

* filtrado y preparación documental;
* extracción de símbolos y parsers de lenguaje (KS2);
* recuperación del conocimiento y persistencia vectorial;
* construcción del contexto;
* generación de respuestas (inferencia desacoplada);
* observabilidad y métricas;
* supervisión térmica independiente.

Esta separación permite incorporar nuevos modelos, nuevos proveedores de inferencia y nuevas bases documentales sin modificar el núcleo del pipeline.

---

## 2. Arquitectura general

La arquitectura actual se representa mediante el siguiente esquema de componentes interactivos:

```text
                               EQUIPO FÍSICO

                  +-----------------------------------+
                  |                                   |
                  v                                   v

               WINDOWS                            WSL2 Ubuntu

        LibreHardwareMonitor                     Pipeline RAG / KS2
                 |                                    |
                 v                                    v
       export_temp_server.py                knowledge_filter.py (v1.7)
                 |                                    |
                 | HTTP / JSON                        v
                 |                          symbols_extractor.py (v1.1)
                 |                          + csharp_parser.py (v2.1.5)
                 |                                    |
                 +-------------------+                v
                                     |            embed.py
                                     v                |
                            thermal_watchdog.py       v
                                     |             query.py
                                     +----------------+
                                                      |
                                     Recuperación del conocimiento
                                                      |
                                     +----------------+----------------+
                                     |                                 |
                                     v                                 v
                              embeddings.jsonl                   symbols.jsonl /
                                                                 symbols_raw.jsonl
                                     |                                 |
                                     +----------------+----------------+
                                                      |
                                                      v
                                           Construcción del contexto
                                                      |
                                                      v
                                              llm_backend.py
                                              /                                                          /                                                           v                 v
                                       Ollama Local     OpenRouter Cloud
                                                      |
                                                      v
                                               Respuesta final
```

La recuperación del conocimiento y la extracción estructural de código permanecen completamente locales.

El contexto construido a partir de la búsqueda semántica y la información arquitectónica extraída constituye la principal fuente de conocimiento enviada al modelo de lenguaje.

La generación de la respuesta se delega completamente al backend de inferencia seleccionado via `llm_backend.py`.

---

## 3. Distribución de componentes

### 3.1 Componentes Windows

Windows mantiene el acceso directo al hardware físico y proporciona la información necesaria para la supervisión térmica.

Los principales componentes son:

| Componente | Responsabilidad |
| :--- | :--- |
| **`LibreHardwareMonitor`** | Acceso a sensores físicos del procesador y hardware |
| **`export_temp_server.py`** | Publicación de la información térmica mediante servicio HTTP Flask en puerto 5005 |
| **`start_server.bat`** | Inicio automático del servicio térmico en Windows |
| **`stop_server.bat`** | Finalización del servicio térmico |

#### Flujo de funcionamiento térmico:

```text
LibreHardwareMonitor
          |
          v
export_temp_server.py
          |
          v
http://IP_WINDOWS:5005/data.json  ---> (Escritura automática de windows_ip.txt)
          |
          v
thermal_watchdog.py (WSL2)
```

El servicio HTTP constituye el mecanismo de comunicación desacoplado entre Windows y WSL2 para la supervisión térmica.

---

### 3.2 Componentes WSL2 Ubuntu

En WSL2 se ejecutan todos los componentes relacionados con el filtrado del workspace, la extracción de símbolos, el procesamiento vectorial, la inteligencia artificial y el pipeline RAG.

Los módulos principales son:

| Componente | Versión / Estado | Responsabilidad Principal |
| :--- | :--- | :--- |
| **`knowledge_filter.py`** | v1.7 | Filtrado seguro del workspace con detección de `~/rag_workspace` y guardas de borrado `is_safe_to_delete()`. |
| **`knowledge_policy.conf`** | v1.2 | Reglas de exclusión explícita para carpetas `DatosIniciales` (respaldos) y `Deprecated`. |
| **`symbols_extractor.py`** | v1.1 | Extractor multi-lenguaje determinista con carga dinámica via `importlib` y escritura atómica. |
| **`csharp_parser.py`** | v2.1.5 | Parser especializado de C#/.NET MAUI con clasificación explícita de constructores (`is_constructor`). |
| **`ingest.py`** | Estabilizado | Procesamiento inicial e ingestión documental. |
| **`chunk.py`** | Estabilizado | Fragmentación semántica del contenido para indexación. |
| **`embed.py`** | Estabilizado | Generación de embeddings y reconciliación atómica de índices vectoriales. |
| **`query.py`** | Estabilizado | Coordinación del pipeline RAG, construcción de contexto y delegación a inferencia. |
| **`llm_backend.py`** | Estabilizado | Capa de abstracción de inferencia (LOCAL: Ollama / CLOUD: OpenRouter). |
| **`logger.py`** | Estabilizado | Observabilidad, métricas por fase y mecanismo de depuración granular via `log_debug()`. |
| **`thermal_watchdog.py`** | Estabilizado | Supervisión térmica independiente y detención preventiva de procesos por sobretemperatura. |

Cada módulo posee una responsabilidad claramente definida y evoluciona de forma independiente.

---

## 4. Pipeline RAG y Extracción KS2

El flujo integral de datos desde la extracción del conocimiento hasta la respuesta del usuario es el siguiente:

```text
                        Código Fuente & Documentación (.NET MAUI)
                                           |
                                           v
                              knowledge_filter.py (v1.7)
                       (Exclusión de Deprecated y respaldos)
                                           |
                                           v
                             symbols_extractor.py (v1.1)
                            + csharp_parser.py (v2.1.5)
                                           |
                                           v
                                   symbols_raw.jsonl
                                           |
                                           v
                                 embed.py (Sincronización)
                                           |
                                           v
                                   embeddings.jsonl
                                           |
                                           v
Usuario ----> query.py (Recepción de consulta)
                |
                v
       Generación Embedding Consulta (nomic-embed-text)
                |
                v
       Búsqueda Semántica + Selección de Símbolos
                |
                v
       Construcción del Contexto RAG
                |
                v
       Construcción del Prompt Final
                |
                v
         llm_backend.py
         /                    v              v
  Ollama Local    OpenRouter Cloud
        |
        v
    Respuesta Final (Registrada por logger.py)
```

El pipeline mantiene completamente separadas las etapas de:

* filtrado seguro y extracción de símbolos de código;
* recepción de la consulta y embedding de usuario;
* recuperación del conocimiento semántico y estructural;
* construcción del contexto y prompt;
* inferencia desacoplada;
* observabilidad y métricas de rendimiento.

El contenido recuperado desde `embeddings.jsonl` y la estructura obtenida de `symbols_raw.jsonl` forman parte activa de la construcción del contexto antes de invocar al modelo de lenguaje.

Asimismo, `query.py` e `ingest.py` incorporan mecanismos de depuración controlados por banderas de configuración (`DEBUG_CHUNKS`), permitiendo inspeccionar el comportamiento interno sin afectar el flujo principal.

---

## 5. Separación entre recuperación e inferencia

Uno de los principales logros de la arquitectura consiste en separar completamente la preparación y recuperación del conocimiento de la generación final de respuestas.

### Recuperación y Estructuración del Conocimiento (KS2)

El pipeline de WSL2 mantiene la responsabilidad de:

* procesar y filtrar el workspace activo en `~/rag_workspace/<Proyecto>`;
* analizar el código fuente C# mediante `csharp_parser.py` (v2.1.5) determinando clases, métodos, interfaces y constructores;
* generar los vectores con `nomic-embed-text` a través de `embed.py`;
* reconciliar atómicamente el índice vectorial (`embeddings.jsonl`);
* recuperar fragmentos relevantes y símbolos arquitectónicos durante la consulta.

Todo este proceso permanece local y desacoplado del modelo de inferencia.

### Inferencia

Una vez construido el contexto enriquecido, `query.py` delega completamente la generación de la respuesta a `llm_backend.py`.

Este módulo constituye una capa de abstracción cuya responsabilidad es seleccionar el proveedor configurado e invocar el modelo correspondiente.

Actualmente se encuentran implementados dos backends:

| Backend | Proveedor / Motor | Ámbito |
| :--- | :--- | :--- |
| **`LOCAL`** | Ollama | Ejecución local desacoplada |
| **`CLOUD`** | OpenRouter | API de inferencia remota |

Gracias a esta separación, la incorporación de nuevos proveedores de inferencia requiere únicamente ampliar `llm_backend.py`, manteniendo inalterada la arquitectura de recuperación y extracción de conocimiento.

---

## 6. Observabilidad y Métricas

La observabilidad del sistema se centraliza en `logger.py`. Este componente constituye una capa independiente que registra cronológicamente la ejecución y calcula métricas de rendimiento sin intervenir en la lógica funcional.

Cada consulta genera una sesión estructurada de registro en `query_log.txt`, almacenando datos de fecha, backend, modelos utilizados, pregunta del usuario y tiempos por fase.

Las métricas automáticas calculadas son:

| Métrica | Descripción |
| :--- | :--- |
| **`EMBEDDING_TIME`** | Tiempo empleado en generar el embedding de la consulta del usuario |
| **`SEARCH_TIME`** | Tiempo dedicado a la recuperación semántica e inspección de símbolos |
| **`LLM_TIME`** | Tiempo consumido por el backend de inferencia (Ollama / OpenRouter) |
| **`PIPELINE_TIME`** | Tiempo total del pipeline desde la entrada del usuario hasta la entrega de la respuesta |

Además, `logger.py` expone la función genérica `log_debug()`, utilizada por `query.py`, `symbols_extractor.py` y `embed.py` para registrar eventos técnicos detallados sin alterar la ejecución funcional.

---

## 7. Supervisión térmica independiente

La protección térmica constituye una capa complementaria y completamente desacoplada del pipeline RAG. Su ejecución no interrumpe el flujo lógico a menos que se alcancen condiciones de sobretemperatura en el procesador.

El componente principal en WSL2 es:

```text
thermal_watchdog.py
```

Sus funciones son:

* consultar periódicamente la temperatura a `export_temp_server.py`;
* calcular un promedio móvil de temperatura para evitar falsos positivos;
* clasificar el estado térmico (Normal, Advertencia, Crítico);
* registrar eventos térmicos en los logs del sistema;
* detener preventivamente la ejecución de `query.py` o procesos de embeddings al superar los umbrales configurados.

```text
LibreHardwareMonitor (Windows)
          |
          v
export_temp_server.py (Flask 5005)
          |
          v
HTTP / JSON
          |
          v
thermal_watchdog.py (WSL2)
          |
          +----------------------+
          |                      |
          v                      v
     Estado Normal         Estado Crítico
          |                      |
          v                      v
  Continuar Pipeline      Finalizar Procesos Preventivamente
```

---

## 8. Comunicación entre Windows y WSL2

La comunicación entre el entorno Windows (sensores) y WSL2 (pipeline) se realiza mediante un servicio HTTP ligero implementado con Flask.

El flujo de descubrimiento de IP se resume en:

```text
Windows: export_temp_server.py ──> Escribe windows_ip.txt ──> Publica /data.json
                                                                    │
WSL2: thermal_watchdog.py <── Lee windows_ip.txt o Auto-detecta host ┘
```

El archivo `windows_ip.txt` permite que WSL2 localice dinámicamente al anfitrión Windows. En caso de ausencia, el sistema cuenta con resolución fallback automática del gateway de WSL2, eliminando la necesidad de IPs estáticas o configuraciones manuales permanentes.

---

## 9. Principios de diseño aplicados

La arquitectura se rige por los siguientes principios:

* **Separación de responsabilidades:** Cada componente posee un propósito exclusivo (filtrado en `knowledge_filter.py`, parsing en `csharp_parser.py`, inferencia en `llm_backend.py`).
* **Bajo acoplamiento:** Los módulos interactúan a través de interfaces estandarizadas y archivos JSONL de intercambio atómico (`symbols_raw.jsonl`, `embeddings.jsonl`).
* **Recuperación local del conocimiento:** El procesamiento de documentos, extracción de AST/símbolos y vectores se realiza íntegramente en WSL2.
* **Inferencia desacoplada:** La capa de inferencia es completamente agnóstica a la forma en que el conocimiento fue recuperado o estructurado.
* **Observabilidad integrada:** Registro transparente de sesiones, latencias por fase e información de depuración via `log_debug()`.

---

## 10. Estado actual de la arquitectura

Al **26 de agosto de 2026**, la arquitectura implementada ofrece:

* **Pipeline KS2 Validado:** Proceso de filtrado (`knowledge_filter.py` v1.7) y extracción de símbolos (`symbols_extractor.py` v1.1 con `csharp_parser.py` v2.1.5) completamente probado end-to-end con 53 archivos y 57 símbolos extraídos en el proyecto real .NET MAUI.
* **Sincronización Vectorial Robusta:** Reconciliación atómica en `embed.py` sobre 57 entidades reales leídas (14 sin cambios, 43 modificadas, 6 eliminadas por políticas de exclusión).
* **Inferencia Híbrida Desacoplada:** Selección dinámica entre Ollama (Local) y OpenRouter (Cloud) via `llm_backend.py`.
* **Observabilidad Completa:** Métricas automáticas (`EMBEDDING_TIME`, `SEARCH_TIME`, `LLM_TIME`, `PIPELINE_TIME`) y depuración granular con `log_debug()`.
* **Supervisión Térmica Desacoplada:** Monitoreo activo via `thermal_watchdog.py` y `export_temp_server.py`.

---

## 11. Consideraciones finales

La arquitectura de **Arquitectura_RAG_Termica** ha alcanzado una madurez estructural donde la plataforma del asistente técnico es completamente independiente del proyecto asistido.

La separación entre el **asistente técnico** (motor RAG, extractor KS2, supervisión y logger) y el **proyecto asistido** (ubicado en `~/rag_workspace/<Proyecto>`) permite reutilizar este pipeline sobre cualquier otro sistema de software mediante la adición de nuevos parsers o bases documentales, manteniendo intacto el núcleo de la arquitectura.

