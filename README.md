# Arquitectura RAG Híbrida con Supervisión Térmica

> Arquitectura experimental para la construcción de asistentes técnicos basados en **Retrieval-Augmented Generation (RAG)**, con recuperación local del conocimiento, inferencia desacoplada y supervisión térmica del hardware.

---

# Descripción

**Arquitectura_RAG_Termica** es un proyecto experimental cuyo objetivo es diseñar e implementar una arquitectura RAG modular, desacoplada y documentada que sirva como base para asistentes técnicos especializados.

El proyecto explora la integración de distintas disciplinas:

- Inteligencia Artificial aplicada mediante modelos de lenguaje (LLM).
- Recuperación Semántica de Información (RAG).
- Arquitectura de software orientada al desacoplamiento de componentes.
- Observabilidad del pipeline mediante registro de eventos y métricas.
- Supervisión térmica para la protección del hardware durante la ejecución de cargas intensivas.

Aunque inicialmente fue concebido para ejecutar modelos locales mediante Ollama, la arquitectura ha evolucionado hacia un enfoque híbrido en el que la recuperación del conocimiento permanece local mientras la inferencia puede realizarse utilizando distintos proveedores sin modificar el núcleo del sistema.

El objetivo a largo plazo es disponer de una plataforma experimental que facilite el estudio, evaluación y evolución de arquitecturas RAG sobre hardware de propósito general, manteniendo una documentación técnica coherente con la implementación real.

---

# Objetivos del proyecto

Los principales objetivos del proyecto son:

- Construir una arquitectura RAG limpia, modular y mantenible.
- Mantener desacopladas las fases de recuperación e inferencia.
- Facilitar la incorporación de nuevos proveedores de modelos de lenguaje.
- Registrar métricas relevantes durante cada consulta.
- Supervisar el comportamiento térmico del hardware.
- Proteger el sistema frente a condiciones de sobretemperatura.
- Mantener una documentación técnica alineada con la implementación.
- Servir como plataforma de experimentación para futuras investigaciones.

El proyecto prioriza la estabilidad arquitectónica, la mantenibilidad y la trazabilidad sobre la incorporación acelerada de nuevas funcionalidades.

---

# Principios de diseño

La arquitectura fue desarrollada siguiendo una serie de principios que guían su evolución.

## Bajo acoplamiento

Cada componente mantiene responsabilidades claramente definidas y conoce únicamente la información necesaria para realizar su función.

## Alta cohesión

Cada módulo implementa una única responsabilidad principal.

## Separación de responsabilidades

La recuperación documental, la inferencia, la supervisión térmica y el registro de eventos se implementan como componentes independientes.

## Evolución incremental

Las nuevas funcionalidades se incorporan mediante pequeños cambios controlados, procurando preservar la estabilidad de la arquitectura existente.

## Observabilidad

El comportamiento del sistema puede analizarse mediante registros cronológicos y métricas de ejecución.

## Documentación como parte del desarrollo

Cada modificación significativa de la arquitectura se refleja en la documentación técnica del proyecto.

---

# Arquitectura general

Actualmente el sistema se distribuye entre dos entornos de ejecución que colaboran entre sí.

```text
                     EQUIPO FÍSICO

      +---------------------------------------------------+

          Windows                           WSL2 Ubuntu

      LibreHardwareMonitor              Pipeline RAG

      export_temp_server.py             ingest.py
                                        embed.py
                                        symbol_extractor.py
                                        query.py
                                        llm_backend.py
                                        logger.py
                                        thermal_watchdog.py

                │
                │ HTTP (JSON)
                ▼

      Supervisión térmica desacoplada
```

Cada entorno mantiene responsabilidades claramente diferenciadas.

---

# Windows

El entorno Windows concentra los componentes relacionados con la adquisición de información del hardware.

Responsabilidades principales:

- acceso a los sensores físicos;
- ejecución de LibreHardwareMonitor;
- publicación simplificada de la temperatura mediante Flask;
- generación automática del archivo `windows_ip.txt`;
- suministro de información térmica al entorno WSL2.

Componentes principales:

```text
LibreHardwareMonitor

        │

        ▼

export_temp_server.py

        │

        ▼

windows_ip.txt

        │

        ▼

HTTP JSON
```

El pipeline RAG no interactúa directamente con los sensores físicos, sino únicamente con la información publicada por este servicio.

---

# WSL2 Ubuntu

El entorno WSL2 concentra todos los componentes relacionados con el procesamiento documental y la inteligencia artificial.

Responsabilidades principales:

- procesamiento de documentos;
- generación de embeddings;
- extracción de símbolos arquitectónicos;
- recuperación semántica;
- construcción del contexto RAG;
- coordinación del pipeline RAG;
- selección del backend de inferencia;
- registro de eventos y métricas;
- supervisión térmica.

Arquitectura simplificada:

```text
Documentos

      │

      ▼

ingest.py

      │

      ▼

output_raw.jsonl

      │

      ├──────────────┐

      ▼              ▼

embed.py     symbol_extractor.py

      │              │

      ▼              ▼

embeddings.jsonl   symbols.jsonl

          │

          ▼

       query.py

          │

          ▼

    llm_backend.py

     ┌─────────────┐

     ▼             ▼

  LOCAL         CLOUD

 Ollama      OpenRouter

          │

          ▼

      logger.py

thermal_watchdog.py
```

Los componentes auxiliares (`logger.py` y `thermal_watchdog.py`) permanecen desacoplados del flujo principal de inferencia, permitiendo registrar información, métricas y supervisar el sistema sin modificar la lógica funcional del pipeline RAG.

---
# Pipeline RAG

El flujo de una consulta sigue una arquitectura desacoplada en la que la recuperación del conocimiento permanece independiente del mecanismo de inferencia.

A partir de la versión 1.5, el pipeline no solo recupera información relevante, sino que construye explícitamente el contexto RAG que será enviado al modelo de lenguaje junto con el contexto arquitectónico obtenido mediante `symbols.jsonl`.

```text
Usuario

    │

    ▼

Recepción de la consulta

    │

    ▼

Generación del embedding
(nomic-embed-text)

    │

    ▼

Búsqueda semántica
(embeddings.jsonl)

    │

    ▼

Construcción del contexto RAG

    │

    ▼

Recuperación del contexto arquitectónico
(symbols.jsonl)

    │

    ▼

Construcción del prompt

    │

    ▼

llm_backend.py

    │

 ┌───┴──────────┐

 ▼              ▼

LOCAL        CLOUD

Ollama    OpenRouter

    │

    ▼

Respuesta
```

Este flujo permanece invariable independientemente del backend de inferencia seleccionado. La única etapa que cambia es el proveedor encargado de generar la respuesta.

---

# Separación entre recuperación e inferencia

Uno de los principios arquitectónicos fundamentales del proyecto consiste en separar completamente la recuperación del conocimiento de la generación de respuestas.

Actualmente:

- la recuperación RAG se ejecuta íntegramente de forma local;
- los embeddings se generan mediante `nomic-embed-text`;
- la búsqueda semántica recupera los fragmentos más relevantes desde `embeddings.jsonl`;
- `query.py` construye el contexto RAG utilizando dichos fragmentos;
- el contexto arquitectónico se obtiene mediante `symbols.jsonl`;
- ambos contextos se integran antes de construir el prompt final;
- la inferencia se delega completamente a `llm_backend.py`.

Gracias a esta organización:

- `query.py` no depende de un proveedor específico de inferencia;
- `llm_backend.py` desconoce cómo fue recuperado el conocimiento;
- la recuperación documental permanece independiente del modelo utilizado para responder;
- es posible incorporar nuevos proveedores realizando cambios únicamente en la capa de inferencia.

Actualmente existen dos backends implementados:

- **LOCAL**, basado en Ollama.
- **CLOUD**, basado en OpenRouter.

La incorporación de nuevos proveedores únicamente requiere ampliar `llm_backend.py`, manteniendo intacto el resto del pipeline.

---

# Supervisión térmica

El proyecto incorpora un sistema independiente de supervisión térmica destinado a proteger el hardware durante la ejecución de tareas intensivas.

Su funcionamiento permanece completamente desacoplado del pipeline RAG.

```text
LibreHardwareMonitor

        │

        ▼

export_temp_server.py

        │

        ▼

HTTP JSON

        │

        ▼

thermal_watchdog.py

        │

        ▼

Supervisión del CPU

        │

        ▼

Protección preventiva
```

Entre sus funciones principales se encuentran:

- lectura periódica de la temperatura;
- cálculo del promedio móvil;
- clasificación del estado térmico;
- registro de eventos críticos;
- detención preventiva de procesos cuando se alcanzan los umbrales configurados;
- recuperación automática una vez restablecidas las condiciones normales.

La supervisión térmica protege la ejecución del pipeline independientemente del backend de inferencia utilizado.

---

# Observabilidad del sistema

La arquitectura incorpora mecanismos de observabilidad que permiten analizar el comportamiento del sistema durante cada consulta sin introducir dependencias entre los distintos componentes.

El módulo `logger.py` registra cronológicamente los eventos del pipeline e incorpora métricas automáticas como:

- tiempo de generación del embedding (`EMBEDDING_TIME`);
- tiempo de recuperación semántica (`SEARCH_TIME`);
- tiempo de inferencia (`LLM_TIME`);
- tiempo total del pipeline (`PIPELINE_TIME`).

Además del registro cronológico y las métricas de rendimiento, `logger.py` proporciona un mecanismo genérico de depuración mediante la función `log_debug()`, permitiendo que cualquier módulo registre información técnica adicional sin incorporar lógica de diagnóstico dentro de sus propias responsabilidades.

De esta forma, componentes como `query.py` pueden registrar información útil para el análisis —por ejemplo, los fragmentos recuperados durante la búsqueda semántica— manteniendo completamente desacoplado el sistema de observabilidad del resto de la arquitectura.

Esta organización facilita:

- el diagnóstico de incidencias;
- la validación del funcionamiento del pipeline;
- la comparación entre distintos modos de operación;
- el análisis del rendimiento del sistema;
- la incorporación de nuevos mecanismos de depuración sin modificar los componentes funcionales.

---

# Componentes principales

| Componente | Responsabilidad |
|------------|-----------------|
| `ingest.py` | Procesamiento e ingestión documental. |
| `chunk.py` | Fragmentación de documentos para su indexación. |
| `embed.py` | Generación de embeddings. |
| `symbol_extractor.py` | Construcción del índice arquitectónico (`symbols.jsonl`). |
| `query.py` | Coordinador principal del pipeline RAG y constructor del contexto enviado al backend de inferencia. |
| `llm_backend.py` | Abstracción del backend de inferencia. |
| `logger.py` | Registro cronológico, métricas del pipeline y observabilidad. |
| `thermal_watchdog.py` | Supervisión térmica y protección preventiva. |
| `export_temp_server.py` | Adaptación de LibreHardwareMonitor para WSL2 mediante Flask. |
| `LibreHardwareMonitor` | Obtención de información térmica del hardware. |

---

# Organización del repositorio

La documentación del proyecto se encuentra organizada para facilitar su consulta y mantenimiento.

```text
Arquitectura_RAG_Termica
│
├── README.md
├── LICENSE
├── ESTRUCTURA_DEL_PROYECTO.md
├── docs/
└── source/
```

La descripción detallada de la estructura del repositorio se encuentra en `ESTRUCTURA_DEL_PROYECTO.md`.

La documentación técnica completa se organiza dentro del directorio `docs/`, mientras que el directorio `source/` conserva una copia documentada de los principales componentes implementados durante la evolución del proyecto.

---

# Tecnologías utilizadas

| Área | Tecnología |
|------|------------|
| Lenguaje principal | Python |
| Sistema anfitrión | Windows 10 |
| Entorno IA | WSL2 Ubuntu |
| Recuperación RAG | Embeddings locales |
| Modelo de embeddings | `nomic-embed-text` |
| Inferencia LOCAL | Ollama |
| Inferencia CLOUD | OpenRouter |
| Supervisión térmica | LibreHardwareMonitor |
| Servicio de monitoreo | Flask |
| Comunicación Windows–WSL2 | HTTP + JSON |
| Control de versiones | Git / GitHub |

---
# Estado actual del proyecto

**Estado de la documentación:** 28 de julio de 2026.

En su estado actual, el proyecto dispone de:

- Arquitectura RAG modular y desacoplada.
- Recuperación semántica completamente local.
- Construcción explícita del contexto RAG antes de la inferencia.
- Índice de embeddings mediante `embeddings.jsonl`.
- Índice arquitectónico mediante `symbols.jsonl`.
- Capa de abstracción de inferencia implementada en `llm_backend.py`.
- Backend **LOCAL** basado en Ollama.
- Backend **CLOUD** basado en OpenRouter.
- Registro cronológico de eventos mediante `logger.py`.
- Métricas automáticas del pipeline (`EMBEDDING_TIME`, `SEARCH_TIME`, `LLM_TIME` y `PIPELINE_TIME`).
- Mecanismo centralizado de depuración mediante `log_debug()`.
- Supervisión térmica desacoplada mediante `thermal_watchdog.py`.
- Protección preventiva frente a sobretemperatura.
- Documentación técnica organizada por componentes.
- Evidencias históricas de pruebas documentadas.

La arquitectura continúa evolucionando mediante mejoras incrementales, procurando mantener la coherencia entre la implementación, la documentación técnica y los principios de diseño definidos para el proyecto.

---

# Documentación

La documentación técnica del proyecto se encuentra organizada en documentos independientes, cada uno dedicado a un aspecto específico de la arquitectura.

| Documento | Contenido |
|-----------|-----------|
| `01_vision_general.md` | Contexto, motivación y objetivos del proyecto. |
| `02_arquitectura_del_sistema.md` | Arquitectura general del sistema y organización de componentes. |
| `03_pipeline_RAG.md` | Flujo del pipeline RAG y construcción del contexto. |
| `04_ollama_y_entorno.md` | Configuración del entorno de ejecución e inferencia. |
| `05_supervision_y_proteccion_termica.md` | Arquitectura de supervisión térmica y mecanismos de protección. |
| `06_pruebas_y_validacion.md` | Estrategia de pruebas y validación del sistema. |
| `07_mantenimiento_y_evolucion.md` | Operación, mantenimiento y evolución prevista. |
| `08_backend_hibrido.md` | Arquitectura del backend de inferencia y desacoplamiento entre recuperación e inferencia. |

El directorio `docs/pruebas/` conserva la evidencia histórica de las principales pruebas realizadas durante el desarrollo del proyecto.

Actualmente incluye, entre otras:

- validación del backend LOCAL;
- validación de la protección térmica;
- validación de la arquitectura híbrida LOCAL/CLOUD;
- validación de la integración del pipeline RAG con la construcción efectiva del contexto.

---

# Evolución prevista

La arquitectura fue diseñada para facilitar la incorporación progresiva de nuevas capacidades sin modificar los principios fundamentales del sistema.

Entre las posibles líneas de evolución se encuentran:

- incorporación de nuevos proveedores de inferencia;
- selección dinámica del backend según las condiciones del sistema;
- ampliación de las métricas de observabilidad;
- incorporación de métricas de recuperación documental;
- ampliación de la supervisión de recursos del sistema;
- automatización del entorno de ejecución;
- incorporación de herramientas de administración y diagnóstico;
- especialización de asistentes técnicos para distintos dominios.

Estas líneas representan objetivos de evolución y no funcionalidades implementadas actualmente.

---

# Filosofía del proyecto

Más allá de la implementación de un pipeline RAG, este proyecto persigue el diseño de una arquitectura capaz de evolucionar de forma ordenada, documentada y sostenible.

Cada decisión de diseño busca favorecer:

- modularidad;
- bajo acoplamiento;
- alta cohesión;
- facilidad de mantenimiento;
- observabilidad del sistema;
- trazabilidad entre código y documentación;
- reutilización de componentes;
- incorporación progresiva de nuevas capacidades sin comprometer la estabilidad de la arquitectura.

La documentación constituye un componente esencial del proyecto y evoluciona de forma coordinada con la implementación.

---

# Licencia

Este proyecto se distribuye bajo la licencia **MIT**.

Las herramientas, modelos de lenguaje, bibliotecas y servicios utilizados durante el desarrollo mantienen sus respectivas licencias y condiciones de uso.

---

# Agradecimientos

Este proyecto ha servido como plataforma experimental para estudiar la integración de recuperación semántica, modelos de lenguaje, arquitectura de software y supervisión de recursos sobre hardware de propósito general.

La evolución del sistema ha permitido consolidar una arquitectura híbrida en la que la recuperación del conocimiento, la construcción del contexto, la inferencia, la observabilidad y la supervisión térmica permanecen claramente desacopladas.

Esta organización constituye una base sólida para continuar evolucionando el proyecto hacia asistentes técnicos especializados, manteniendo la coherencia entre el código fuente, la documentación técnica y los principios arquitectónicos definidos desde sus primeras versiones.
