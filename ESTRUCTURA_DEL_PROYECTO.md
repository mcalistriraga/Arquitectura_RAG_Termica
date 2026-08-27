# Estructura del Proyecto

Este documento describe la organización general del repositorio **Arquitectura_RAG_Termica** y el propósito de los principales archivos y directorios que lo componen.

La estructura del proyecto separa la documentación general, las decisiones arquitectónicas (ADR), la documentación técnica, las pruebas de validación y el código fuente distribuido por entorno (`windows` y `wsl`), con el objetivo de facilitar el mantenimiento, la evolución de la arquitectura y la consulta de la información.

---

## 1. Organización del repositorio

```text
Arquitectura_RAG_Termica/
│
├── README.md
│   Documento principal del proyecto.
│   Presenta la visión general, los objetivos, la arquitectura,
│   los componentes principales y el estado actual del sistema.
│
├── LICENSE
│   Licencia de distribución del proyecto.
│
├── ESTRUCTURA_DEL_PROYECTO.md
│   Descripción de la organización del repositorio y de la
│   documentación disponible.
│
├── docs/
│   │
│   ├── 01_vision_general.md
│   │   Contexto, motivación y objetivos del proyecto.
│   │
│   ├── 02_arquitectura_del_sistema.md
│   │   Arquitectura general del sistema, organización de los
│   │   componentes y comunicación entre los distintos entornos
│   │   de ejecución.
│   │
│   ├── 03_pipeline_RAG.md
│   │   Flujo del pipeline RAG, recuperación semántica,
│   │   construcción del contexto y organización del proceso
│   │   de consulta.
│   │
│   ├── 04_ollama_y_entorno.md
│   │   Configuración del entorno de ejecución, instalación
│   │   de Ollama, modelos utilizados y organización del
│   │   entorno RAG.
│   │
│   ├── 05_supervision_y_proteccion_termica.md
│   │   Arquitectura de supervisión térmica, comunicación
│   │   Windows–WSL2, watchdog y mecanismos de protección.
│   │
│   ├── 06_pruebas_y_validacion.md
│   │   Estrategia de pruebas, validación funcional de los
│   │   componentes y resultados obtenidos durante el desarrollo.
│   │
│   ├── 07_mantenimiento_y_evolucion.md
│   │   Organización del mantenimiento del sistema, operación,
│   │   copias de seguridad y líneas de evolución previstas.
│   │
│   ├── 08_backend_hibrido.md
│   │   Arquitectura del backend de inferencia, abstracción
│   │   mediante llm_backend.py y soporte para proveedores
│   │   LOCAL y CLOUD.
│   │
│   ├── adr/
│   │   │
│   │   ├── ADR-001-vision-asistente-tecnico-rag.md
│   │   ├── ADR-002-separacion-llm-backend.md
│   │   ├── ADR-003-uso-ollama-como-backend-local.md
│   │   ├── ADR-004-incorporacion-openrouter-backend-hibrido.md
│   │   ├── ADR-005-supervision-termica-del-pipeline.md
│   │   ├── ADR-006-evolucion-hacia-construccion-de-contexto.md
│   │   ├── ADR-007-knowledge-package-como-capa-intermedia.md
│   │   ├── ADR-008-adopcion-adr-como-memoria-arquitectonica.md
│   │   ├── ADR-009-politica-configurable-construccion-base-conocimiento.md
│   │   ├── ADR-010-separacion-carga-validacion-configuracion.md
│   │   ├── ADR-011-evolucion-logger-servicio-comun-observabilidad.md
│   │   └── ADR-012-desacoplamiento-identidad-estado-knowledge-sources.md
│   │
│   └── pruebas/
│       │
│       ├── README.md
│       │   Descripción de las pruebas realizadas durante el desarrollo.
│       │
│       ├── 2026-07-20_prueba01_backend_local_qwen2.5-coder-1.5b.md
│       ├── 2026-07-20_prueba02_backend_local_qwen2.5_abort_termico.md
│       ├── 2026-07-21_prueba03_backend_hibrido_local_cloud.md
│       └── 2026-07-28_prueba04_integracion_final.md
│
└── source/
    │
    ├── windows/
    │   └── LibreHardwareMonitor/
    │       └── python/
    │           Servicio de monitoreo térmico ejecutado en el
    │           entorno host de Windows.
    │
    └── wsl/
        │
        ├── rag_maui_docs_for_rag/
        │   │
        │   └── scripts/
        │       │
        │       ├── query.py
        │       ├── embed.py
        │       ├── llm_backend.py
        │       ├── config_loader.py
        │       ├── logger.py
        │       ├── knowledge_filter.py
        │       ├── symbols_extractor.py
        │       │
        │       └── parsers/
        │           └── csharp_parser.py
        │
        └── rag_workspace/
            │
            └── MauiAppGestorMovil/
                │
                ├── knowledge/
                │   ├── embeddings/
                │   └── symbols/
                │
                └── source/
```

La estructura anterior representa la organización general del repositorio y la separación entre documentación, decisiones arquitectónicas, pruebas y código fuente ejecutado en los distintos entornos.

---

## 2. Organización de la documentación

La documentación ha sido organizada de forma progresiva para facilitar la comprensión del proyecto.

Se recomienda seguir el siguiente orden de lectura:

```text
README.md
     │
     ▼
Visión general del proyecto
docs/01_vision_general.md
     │
     ▼
Arquitectura del sistema
docs/02_arquitectura_del_sistema.md
     │
     ▼
Pipeline RAG
docs/03_pipeline_RAG.md
     │
     ▼
Entorno de ejecución e inferencia
docs/04_ollama_y_entorno.md
     │
     ▼
Supervisión térmica
docs/05_supervision_y_proteccion_termica.md
     │
     ▼
Pruebas y validación
docs/06_pruebas_y_validacion.md
     │
     ▼
Mantenimiento y evolución
docs/07_mantenimiento_y_evolucion.md
     │
     ▼
Backend de inferencia
docs/08_backend_hibrido.md
     │
     ▼
Registro de Decisiones Arquitectónicas
docs/adr/
```

Este recorrido permite comprender primero los objetivos generales del proyecto y, posteriormente, profundizar en cada uno de sus componentes, decisiones de diseño, evolución arquitectónica registrada en los ADR y detalles de implementación.

---

## 3. Carpeta de pruebas

El repositorio incorpora una subcarpeta específica dentro de la documentación, `docs/pruebas/`, destinada a conservar evidencia de las pruebas realizadas durante el desarrollo.

```text
docs/pruebas/
│
├── README.md
│   Descripción de la organización y alcance de las pruebas.
│
├── 2026-07-20_prueba01_backend_local_qwen2.5-coder-1.5b.md
│   Validación inicial del backend LOCAL utilizando
│   qwen2.5-coder:1.5b.
│
├── 2026-07-20_prueba02_backend_local_qwen2.5_abort_termico.md
│   Validación del mecanismo de protección térmica
│   durante la ejecución del backend LOCAL.
│
├── 2026-07-21_prueba03_backend_hibrido_local_cloud.md
│   Validación de la arquitectura híbrida mediante
│   la selección de los backends LOCAL y CLOUD.
│
└── 2026-07-28_prueba04_integracion_final.md
    Prueba de integración del pipeline RAG,
    supervisión térmica, registro de eventos
    y capa de abstracción del backend de inferencia.
```

Los documentos de esta carpeta constituyen evidencia histórica del proceso de desarrollo y complementan la información resumida en `docs/06_pruebas_y_validacion.md`.

---

## 4. Alcance de este documento

Este documento describe únicamente la organización general del repositorio y de su documentación.

La descripción detallada de la arquitectura, del pipeline RAG, de la supervisión térmica, del backend de inferencia y de los distintos componentes del sistema se encuentra en el directorio `docs/`, mientras que `README.md` constituye la presentación general del proyecto.

---

## 5. Objetivo de la organización documental

La documentación del proyecto ha sido estructurada para favorecer:

* Una navegación sencilla por el repositorio.
* La separación entre información general, documentación técnica, registro de decisiones arquitectónicas (ADR) y evidencias de pruebas.
* El mantenimiento de la arquitectura a largo plazo.
* La incorporación progresiva de nuevas funcionalidades sin perder coherencia documental.
* La trazabilidad entre la implementación en `source/`, las decisiones registradas en `docs/adr/`, las pruebas realizadas en `docs/pruebas/` y la documentación técnica correspondiente.

Esta organización busca preservar tanto el estado actual del sistema como el contexto histórico de las decisiones y validaciones realizadas durante su evolución.

