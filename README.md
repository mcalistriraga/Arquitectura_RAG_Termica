# Arquitectura RAG Híbrida con Supervisión Térmica

> Arquitectura experimental para la construcción de asistentes técnicos basados en **Retrieval-Augmented Generation (RAG)**, con recuperación local del conocimiento, inferencia desacoplada y supervisión térmica del hardware.

---

# Descripción

**Arquitectura_RAG_Termica** es un proyecto experimental cuyo objetivo es diseñar e implementar una arquitectura RAG modular, desacoplada y documentada que sirva como base para asistentes técnicos especializados.

El proyecto explora la integración de distintas disciplinas:

- Inteligencia Artificial aplicada mediante modelos de lenguaje (LLM).
- Recuperación semántica de información (RAG).
- Arquitectura de software orientada al desacoplamiento de componentes.
- Observabilidad del pipeline mediante registro de métricas.
- Supervisión térmica para la protección del hardware durante la ejecución de cargas intensivas.

Aunque inicialmente fue concebido para ejecutar modelos locales mediante Ollama, la arquitectura ha evolucionado hacia un enfoque híbrido en el que la recuperación del conocimiento permanece local mientras la inferencia puede realizarse utilizando distintos proveedores sin modificar el núcleo del sistema.

---

# Objetivos del proyecto

Los principales objetivos son:

- Construir una arquitectura RAG limpia y modular.
- Mantener desacopladas las fases de recuperación e inferencia.
- Facilitar la incorporación de nuevos proveedores de modelos de lenguaje.
- Registrar métricas de rendimiento de cada consulta.
- Supervisar el comportamiento térmico del hardware durante la ejecución.
- Documentar la arquitectura para facilitar su mantenimiento y evolución.

El proyecto prioriza la estabilidad arquitectónica sobre la incorporación rápida de nuevas funcionalidades.

---

# Principios de diseño

La arquitectura se desarrolla siguiendo varios principios:

- Bajo acoplamiento entre componentes.
- Alta cohesión funcional.
- Responsabilidades claramente definidas.
- Evolución mediante pequeños cambios controlados.
- Documentación técnica extensa.
- Facilidad de mantenimiento.

Antes de introducir modificaciones importantes se analiza su impacto sobre la arquitectura general.

---

# Arquitectura general

Actualmente el sistema se distribuye entre dos entornos de ejecución.

```text
                    EQUIPO FÍSICO

          +--------------------------------------+
          |                                      |
          |                                      |
          ▼                                      ▼

     Windows                               WSL2 Ubuntu

LibreHardwareMonitor                    Pipeline RAG
export_temp_server.py                   query.py
                                        llm_backend.py
                                        logger.py
                                        Ollama

          │
          │ HTTP (JSON)
          ▼

thermal_watchdog.py
```

Cada entorno asume responsabilidades diferentes.

## Windows

Responsabilidades:

- Acceso a los sensores del hardware.
- Publicación de la temperatura mediante un servicio HTTP.

Componentes principales:

- LibreHardwareMonitor
- export_temp_server.py

---

## WSL2 Ubuntu

Responsabilidades:

- Procesamiento documental.
- Recuperación RAG.
- Generación de embeddings.
- Ejecución del pipeline.
- Supervisión térmica.
- Inferencia mediante el backend seleccionado.

---

# Pipeline RAG

El flujo general de una consulta es el siguiente:

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
Recuperación de contexto
(symbols.jsonl)
    │
    ▼
Construcción del prompt
    │
    ▼
llm_backend.py
    │
    ├────────► Ollama
    │
    └────────► OpenRouter
                 │
                 ▼
             Respuesta
```

Cada consulta constituye una sesión independiente de ejecución.

---

# Separación entre recuperación e inferencia

Una de las decisiones arquitectónicas más importantes del proyecto consiste en separar completamente la recuperación del conocimiento de la generación de respuestas.

Actualmente:

- La recuperación RAG se ejecuta íntegramente de forma local.
- Los embeddings se generan mediante `nomic-embed-text`.
- La búsqueda semántica utiliza `embeddings.jsonl`.
- El contexto arquitectónico utiliza `symbols.jsonl`.
- La inferencia se delega completamente a `llm_backend.py`.

Gracias a esta separación, `query.py` no necesita conocer cómo se comunica cada proveedor de inferencia.

Actualmente existen dos backends implementados:

- LOCAL (Ollama)
- CLOUD (OpenRouter)

La incorporación de nuevos proveedores puede realizarse ampliando `llm_backend.py` sin modificar el resto del pipeline.

---

# Supervisión térmica

El proyecto incorpora un sistema independiente de supervisión térmica destinado a proteger el hardware durante la ejecución de procesos intensivos.

Su funcionamiento permanece completamente desacoplado del pipeline RAG.

```text
LibreHardwareMonitor
        │
        ▼
export_temp_server.py
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

El watchdog realiza, entre otras tareas:

- lectura periódica de la temperatura;
- cálculo de promedio móvil;
- detección de umbrales configurados;
- registro de eventos;
- interrupción preventiva de procesos cuando se alcanzan condiciones críticas.

---

# Observabilidad del sistema

Cada consulta genera automáticamente un nuevo registro de ejecución.

El módulo `logger.py` registra cronológicamente los eventos del pipeline y calcula métricas de rendimiento como:

- EMBEDDING_TIME
- SEARCH_TIME
- LLM_TIME
- PIPELINE_TIME

Estas métricas permiten analizar el comportamiento del sistema sin modificar la lógica funcional del pipeline.

---

# Componentes principales

| Componente | Responsabilidad |
|------------|-----------------|
| `query.py` | Coordinador principal del pipeline RAG. |
| `llm_backend.py` | Abstracción del backend de inferencia. |
| `logger.py` | Registro de eventos y métricas del pipeline. |
| `embed.py` | Generación de embeddings. |
| `ingest.py` | Procesamiento e ingestión documental. |
| `chunk.py` | Fragmentación de documentos. |
| `symbol_extractor.py` | Construcción del contexto arquitectónico. |
| `thermal_watchdog.py` | Supervisión térmica del sistema. |
| `monitor_temperatura.py` | Herramientas de monitoreo térmico. |
| `test_env.py` | Validación del entorno de ejecución. |

---

# Organización del repositorio

```text
Arquitectura_RAG_Termica
│
├── README.md
├── LICENSE
├── ESTRUCTURA_DEL_PROYECTO.md
└── docs/
```

La organización completa del repositorio se describe en `ESTRUCTURA_DEL_PROYECTO.md`.

La documentación técnica detallada se encuentra en el directorio `docs/`.

---

# Tecnologías utilizadas

| Área | Tecnología |
|------|------------|
| Lenguaje principal | Python |
| Sistema operativo IA | WSL2 Ubuntu |
| Sistema anfitrión | Windows |
| Recuperación RAG | Embeddings locales |
| Modelo de embeddings | nomic-embed-text |
| Inferencia local | Ollama |
| Inferencia cloud | OpenRouter |
| Monitoreo hardware | LibreHardwareMonitor |
| API de monitoreo | Flask |

---

# Estado actual del proyecto

Al 24 de julio de 2026 el proyecto dispone de:

- Arquitectura modular desacoplada.
- Recuperación RAG completamente local.
- Backend de inferencia desacoplado.
- Soporte para inferencia local y cloud.
- Registro automático de métricas.
- Supervisión térmica independiente.
- Documentación técnica organizada por componentes.

La evolución del proyecto continúa mediante mejoras incrementales sobre esta arquitectura.

---

# Documentación

El proyecto incluye documentación técnica organizada en varios documentos.

| Documento | Contenido |
|-----------|-----------|
| `01_vision_general.md` | Visión y objetivos del proyecto. |
| `02_arquitectura_del_sistema.md` | Arquitectura general. |
| `03_pipeline_RAG.md` | Flujo del pipeline RAG. |
| `04_ollama_y_entorno.md` | Entorno de inferencia y configuración. |
| `05_supervision_y_proteccion_termica.md` | Supervisión térmica. |
| `06_pruebas_y_validacion.md` | Pruebas realizadas. |
| `07_mantenimiento_y_evolucion.md` | Evolución prevista. |

---

# Evolución prevista

La arquitectura ha sido diseñada para facilitar su crecimiento progresivo.

Entre las posibles líneas de evolución se encuentran:

- incorporación de nuevos proveedores de inferencia;
- mejora de las métricas de observabilidad;
- ampliación del sistema de supervisión;
- optimización del pipeline RAG;
- especialización para asistentes técnicos de desarrollo.

Estas líneas representan objetivos de evolución y no funcionalidades implementadas actualmente.

---

# Licencia

Este proyecto se distribuye bajo la licencia MIT.

Las herramientas, modelos de lenguaje y bibliotecas utilizadas mantienen sus respectivas licencias de distribución.

