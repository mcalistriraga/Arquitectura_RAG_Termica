# 01 — Visión General del Proyecto

**Fecha:** 26 de agosto de 2026  
**Versión:** 0.5.1  
**Estado:** Consolidado / Documentación oficial  
**Módulo:** General / Arquitectura del Sistema  
**Propósito:** Definición de la visión general, modelo conceptual, objetivos, principios y estado real del pipeline de conocimiento (KS2) del proyecto.

---

> **Resumen ejecutivo:**  
> **Arquitectura_RAG_Termica** es una plataforma RAG experimental y modular diseñada para construir asistentes técnicos especializados en proyectos de software. La arquitectura desacopla completamente la base documental del proyecto objetivo, la extracción de símbolos (KS2), la recuperación semántica local, la construcción dinámica del contexto, la inferencia (local/cloud), la observabilidad y la supervisión térmica preventiva del hardware.

---

## 1. Descripción general

**Arquitectura_RAG_Termica** es un proyecto cuyo propósito es diseñar e implementar una arquitectura **RAG (Retrieval-Augmented Generation)** modular, desacoplada y ampliamente documentada para la construcción de asistentes técnicos especializados capaces de trabajar sobre distintos proyectos de software.

A diferencia de un asistente diseñado para una única aplicación, esta arquitectura se concibe como una plataforma reutilizable en la que el conocimiento consultado puede sustituirse mediante el cambio de la base documental del proyecto objetivo, sin modificar el núcleo del sistema.

El proyecto integra distintas áreas de la ingeniería de software y de la inteligencia artificial:

* procesamiento documental local y filtrado de workspace;
* extracción estructurada de símbolos de código fuente;
* generación de embeddings y reconciliación vectorial;
* recuperación semántica de información;
* construcción dinámica de contexto;
* inferencia mediante modelos de lenguaje;
* observabilidad del pipeline;
* supervisión térmica del hardware;
* mecanismos automáticos de protección.

La arquitectura ha evolucionado desde un sistema basado exclusivamente en modelos locales hacia una arquitectura híbrida en la que la recuperación del conocimiento permanece local mientras que la inferencia puede realizarse mediante distintos proveedores sin modificar el resto del pipeline.

El objetivo principal no consiste únicamente en obtener respuestas mediante inteligencia artificial, sino en construir una plataforma organizada, mantenible y preparada para evolucionar progresivamente hacia un asistente técnico reutilizable capaz de apoyar el desarrollo de diferentes proyectos de software.

---

## 2. Modelo conceptual

La arquitectura distingue claramente dos elementos independientes.

### Asistente técnico

Constituye el producto principal desarrollado en este proyecto.

Es responsable de:

* ejecutar el pipeline RAG y la extracción de conocimiento (KS2);
* recuperar conocimiento desde una base vectorial;
* construir el contexto enviado al modelo;
* seleccionar el backend de inferencia;
* generar respuestas técnicas;
* registrar métricas del sistema;
* supervisar la ejecución y la estabilidad térmica.

El asistente permanece inalterado independientemente del proyecto sobre el cual trabaje.

---

### Proyecto objetivo (Target Project)

Corresponde al sistema cuya documentación y código fuente serán utilizados como base de conocimiento.

Puede tratarse, por ejemplo, de:

* una aplicación .NET MAUI (caso de uso activo y validado);
* un proyecto Java;
* un sistema PLC;
* un servicio backend;
* cualquier otro proyecto documentado.

Cada proyecto objetivo dispone de su propia base documental, esquema de símbolos, embeddings y metadatos en un espacio de trabajo aislado (`~/rag_workspace/<Proyecto>`), permitiendo que un mismo asistente pueda especializarse dinámicamente sobre distintos dominios sin modificar su arquitectura.

---

## 3. Motivación

Los modelos de lenguaje ofrecen nuevas posibilidades para:

* consulta de documentación técnica;
* análisis de código fuente mediante extracción rigurosa de símbolos;
* comprensión arquitectónica de proyectos existentes;
* asistencia durante el desarrollo de software;
* generación de documentación técnica.

Sin embargo, su utilización sobre equipos con recursos limitados plantea diversos desafíos, especialmente durante tareas como:

* generación masiva de embeddings;
* recuperación semántica sobre grandes volúmenes documentales;
* procesos prolongados de inferencia.

Estas cargas pueden provocar:

* incremento sostenido de la temperatura del procesador;
* reducción del rendimiento del sistema;
* pérdida de estabilidad;
* interrupción inesperada de procesos.

Para afrontar estas limitaciones, el proyecto incorpora una arquitectura que combina:

* recuperación local del conocimiento;
* extracción de símbolos y filtrado seguro de espacio de trabajo;
* inferencia desacoplada;
* observabilidad del pipeline;
* supervisión térmica independiente.

De esta forma es posible experimentar con distintos proveedores de inferencia manteniendo el control sobre la arquitectura, los datos y los recursos del equipo.

---

## 4. Objetivo general

Diseñar e implementar una arquitectura RAG híbrida, modular y desacoplada para la construcción de asistentes técnicos reutilizables, manteniendo la recuperación del conocimiento de forma local, permitiendo utilizar distintos proveedores de inferencia y proporcionando mecanismos de observabilidad y supervisión térmica que favorezcan una operación estable sobre hardware con recursos limitados.

---

## 5. Objetivos específicos

### Plataforma del asistente

* Construir un asistente técnico reutilizable.
* Mantener desacoplados los componentes principales del sistema.
* Permitir la reutilización del pipeline sobre distintos proyectos objetivo mediante configuraciones dinámicas.
* Facilitar la evolución incremental de la arquitectura.

---

### Recuperación y estructuración del conocimiento (KS2)

* Filtrar dinámicamente el espacio de trabajo excluyendo respaldos y componentes obsoletos.
* Extraer símbolos de código fuente de forma determinista y extensible (`symbols_extractor.py`).
* Soportar parsers especializados por lenguaje, incluyendo detección explícita de constructores C# (`csharp_parser.py` v2.1.5).
* Generar embeddings para representar semánticamente la información y los símbolos.
* Reconciliar atómicamente los índices de embeddings ante cambios en los archivos fuente.
* Mantener local la base de conocimiento utilizada por el sistema.

---

### Inferencia

* Desacoplar completamente la generación de respuestas del resto del pipeline.
* Permitir la utilización de distintos backends de inferencia.
* Facilitar la incorporación de nuevos proveedores sin modificar la arquitectura principal.
* Reutilizar la misma construcción de contexto independientemente del backend seleccionado.

---

### Observabilidad

* Registrar cada consulta como una sesión independiente.
* Medir automáticamente el tiempo de las principales etapas del pipeline.
* Facilitar el análisis del rendimiento mediante métricas objetivas.
* Incorporar mecanismos de registro adicionales durante tareas de depuración cuando sea necesario.

---

### Supervisión del sistema

* Obtener información térmica del hardware.
* Supervisar continuamente la temperatura del procesador.
* Detectar condiciones térmicas críticas.
* Registrar eventos relevantes del sistema.
* Proteger automáticamente la ejecución del pipeline cuando sea necesario.

---

## 6. Arquitectura conceptual

La solución se organiza en dos niveles claramente diferenciados:

* **el asistente técnico**, que constituye el producto desarrollado en este proyecto;
* **el proyecto objetivo**, que representa el conocimiento sobre el cual trabajará el asistente.

Esta separación permite reutilizar completamente el pipeline RAG sobre distintos proyectos sin modificar su arquitectura interna.

---

### Asistente técnico

Responsable de:

* gestionar el pipeline RAG y el pipeline de símbolos (KS2);
* filtrar el espacio de trabajo de forma segura (`knowledge_filter.py`);
* recuperar conocimiento desde la base vectorial activa;
* construir el contexto enviado al modelo;
* seleccionar el backend de inferencia;
* registrar métricas del pipeline;
* supervisar la ejecución;
* proporcionar respuestas técnicas especializadas.

El asistente permanece independiente del proyecto cuya información consulta.

---

### Proyecto objetivo

Corresponde al conjunto de documentos y código fuente que alimentan la base de conocimiento.

Puede estar compuesto por:

* código fuente (.cs, .xaml, etc.);
* documentación técnica;
* manuales;
* diagramas;
* archivos Markdown;
* documentación generada durante el desarrollo.

Actualmente el proyecto objetivo corresponde a una aplicación desarrollada en **.NET MAUI**, utilizada como primer caso de uso para validar la arquitectura del asistente y congelar la base de conocimiento KS2.

En futuras versiones podrán incorporarse otros proyectos sin modificar el núcleo del sistema.

---

### Windows

Responsable del acceso al hardware físico.

Componentes principales:

* `LibreHardwareMonitor`
* `export_temp_server.py`
* Herramientas auxiliares de monitoreo.

Responsabilidades:

* obtener información de los sensores del sistema;
* publicar dicha información mediante un servicio HTTP;
* proporcionar los datos necesarios para la supervisión térmica.

---

### WSL2 Ubuntu

Responsable de la ejecución del asistente técnico.

Componentes principales:

* Pipeline de símbolos / KS2 (`knowledge_filter.py`, `symbols_extractor.py`, `csharp_parser.py`).
* Pipeline de embeddings y sincronización (`embed.py`).
* Pipeline RAG (`query.py`).
* Ollama.
* `llm_backend.py`
* `logger.py`
* `thermal_watchdog.py`

Responsabilidades:

* procesamiento y filtrado documental;
* extracción atómica de símbolos de código fuente;
* generación y reconciliación de embeddings;
* recuperación semántica;
* construcción del contexto;
* selección del backend de inferencia;
* generación de respuestas;
* registro de métricas;
* supervisión de la ejecución.

---

## 7. Arquitectura de alto nivel

```text
                  ASISTENTE TÉCNICO RAG
               (Arquitectura_RAG_Termica)

                          │
                          ▼

               Selección del Proyecto Objetivo

                          │

        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼

 Proyecto objetivo A                 Proyecto objetivo B
 (.NET MAUI actual)                  (Futuro proyecto)

        │                                   │
        ▼                                   ▼

 Base documental / Código C#          Base documental local

        │                                   │
        ▼                                   ▼

 Filtrado (knowledge_filter v1.7)           │
 Exclusión de Deprecated / Backups         │
        │                                   │
        ▼                                   ▼

 Extracción Símbolos (v1.1)                 │
 Parsers (csharp_parser v2.1.5)             │
        │                                   │
        └─────────────────┬─────────────────┘
                          ▼

               Generación / Reconciliación 
               de Embeddings (embed.py)

                          │
                          ▼

             Recuperación semántica (RAG)

                          │
                          ▼

               Construcción del contexto

                          │
                          ▼

                   llm_backend.py

            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼

         Ollama                      OpenRouter

            │                           │
            └─────────────┬─────────────┘
                          ▼

               Respuesta del modelo



               SUPERVISIÓN DEL SISTEMA

         LibreHardwareMonitor
                  │
                  ▼
        export_temp_server.py
                  │
                  ▼
         thermal_watchdog.py
                  │
                  ▼
    Protección preventiva del pipeline
```

---

## 8. Filosofía del proyecto

El proyecto evoluciona mediante cambios pequeños, controlados y completamente documentados. Cada modificación busca mantener una arquitectura coherente y fácilmente mantenible antes que incorporar nuevas funcionalidades de forma acelerada.

Los principios que orientan el desarrollo son:

* Separación de responsabilidades.
* Bajo acoplamiento entre componentes.
* Alta cohesión funcional.
* Reutilización de componentes.
* Observabilidad del sistema.
* Documentación técnica extensa.
* Evolución incremental de la arquitectura.
* Independencia entre el asistente y el proyecto objetivo.

El asistente constituye una plataforma técnica reutilizable, mientras que el conocimiento especializado reside en la base documental del proyecto activo. Esta separación facilita la utilización del mismo pipeline sobre diferentes proyectos sin alterar su funcionamiento interno.

---

## 9. Tecnologías principales

| Área | Tecnología / Componente |
| :--- | :--- |
| **Lenguaje principal** | Python 3.x |
| **Sistema anfitrión** | Windows |
| **Entorno de ejecución IA** | WSL2 Ubuntu |
| **Filtrado de Workspace** | `knowledge_filter.py` (v1.7) con borrado seguro (`is_safe_to_delete`) |
| **Extracción de Símbolos** | `symbols_extractor.py` (v1.1) con carga dinámica via `importlib` |
| **Parser C# / MAUI** | `csharp_parser.py` (v2.1.5) con clasificación explícita de constructores |
| **Recuperación y Vectorial** | `embed.py` con resolución dinámica en `~/rag_workspace` |
| **Modelo de embeddings** | `nomic-embed-text` |
| **Inferencia local** | Ollama |
| **Inferencia cloud** | OpenRouter |
| **Supervisión hardware** | `LibreHardwareMonitor` |
| **Servicio de monitoreo** | Flask (`export_temp_server.py`) |
| **Registro del pipeline** | `logger.py` con `log_debug()` |
| **Control de versiones** | Git / GitHub |

---

## 10. Estado actual del proyecto

Al **26 de agosto de 2026**, la arquitectura dispone de:

* **Pipeline RAG modular y dinámico:** Operativo en WSL2 Ubuntu con autodetección de espacio de trabajo en `~/rag_workspace/<Proyecto>`.
* **Fuente de Símbolos Estructurados (KS2 Cerrado End-to-End):**
  * `knowledge_filter.py` (v1.7): Filtrado seguro sin rutas *hardcodeadas*, validado sobre 141 archivos analizados (76 copiados / 65 excluidos).
  * `knowledge_policy.conf` (v1.2): Exclusión explícita de respaldos en `DatosIniciales` y carpetas `Deprecated`.
  * `symbols_extractor.py` (v1.1): Selección dinámica de parsers por lenguaje con escritura atómica (53 archivos procesados / 57 símbolos extraídos).
  * `csharp_parser.py` (v2.1.5): Detección explícita de constructores (`is_constructor`) para C#/.NET MAUI con suite de pruebas aprobada (9/9 PASS).
* **Indexación y Reconciliación Vectorial (`embed.py`):** Sincronización atómica validada contra datos reales (57 entidades leídas, 14 sin cambios, 43 modificadas, 6 eliminadas).
* **Recuperación Local del Conocimiento:** Generación de embeddings mediante `nomic-embed-text` y persistencia vectorial.
* **Backend de Inferencia Desacoplado:** Soporte operativo para inferencia local (Ollama) y cloud (OpenRouter) mediante `llm_backend.py`.
* **Observabilidad y Registro:** Métricas automáticas por consulta con `logger.py` y depuración granular vía `log_debug()`.
* **Supervisión Térmica Independiente:** Servicio HTTP en Windows (`export_temp_server.py`) y watchdog preventivo en WSL2 (`thermal_watchdog.py`).

**Caso de Uso de Validación Real:**  
El sistema se encuentra completamente validado de punta a punta sobre el proyecto real en **.NET MAUI**. El ciclo KS2 ha quedado **congelado y matemáticamente verificado**, listo para sincronización prioritaria en GitHub previa a la integración rica en `query.py`.

---

## 11. Evolución prevista

La arquitectura ha sido diseñada para evolucionar sin modificar el núcleo del asistente.

Las siguientes etapas contemplan, entre otras posibilidades:

* **Paso Inmediato (v0.5.x -> Commit):** Sincronizar los cambios de KS2 en el repositorio GitHub.
* **Integración en Consulta:** Actualizar `query.py` para aprovechar la rica estructura de símbolos extraída por KS2.
* **Transición a la Fase II (v0.6):** Implementación de la arquitectura orientada a contexto (*Context-Driven Architecture*) mediante contratos de datos (`IntentSpec`, `Knowledge Package`) y *Context Providers*.
* **Incorporación de Múltiples Proyectos:** Selección dinámica de la base de conocimiento activa sin alterar el pipeline.
* **Ampliación de Parsers:** Incorporar soporte para nuevos lenguajes manteniendo la arquitectura modular de `symbols_extractor.py`.

Cada nueva funcionalidad deberá respetar los principios de desacoplamiento, reutilización y evolución incremental que guían el desarrollo del proyecto.

