# Visión General del Proyecto

## Nombre del proyecto

**Arquitectura RAG híbrida con supervisión térmica y arquitectura desacoplada para asistentes técnicos**

---

# 1. Descripción general

**Arquitectura_RAG_Termica** es un proyecto cuyo propósito es diseñar e implementar una arquitectura **RAG (Retrieval-Augmented Generation)** modular, desacoplada y ampliamente documentada para la construcción de asistentes técnicos especializados capaces de trabajar sobre distintos proyectos de software.

A diferencia de un asistente diseñado para una única aplicación, esta arquitectura se concibe como una plataforma reutilizable en la que el conocimiento consultado puede sustituirse mediante el cambio de la base documental del proyecto objetivo, sin modificar el núcleo del sistema.

El proyecto integra distintas áreas de la ingeniería de software y de la inteligencia artificial:

- procesamiento documental local;
- generación de embeddings;
- recuperación semántica de información;
- construcción dinámica de contexto;
- inferencia mediante modelos de lenguaje;
- observabilidad del pipeline;
- supervisión térmica del hardware;
- mecanismos automáticos de protección.

La arquitectura ha evolucionado desde un sistema basado exclusivamente en modelos locales hacia una arquitectura híbrida en la que la recuperación del conocimiento permanece local mientras que la inferencia puede realizarse mediante distintos proveedores sin modificar el resto del pipeline.

El objetivo principal no consiste únicamente en obtener respuestas mediante inteligencia artificial, sino en construir una plataforma organizada, mantenible y preparada para evolucionar progresivamente hacia un asistente técnico reutilizable capaz de apoyar el desarrollo de diferentes proyectos de software.

---

# 2. Modelo conceptual

La arquitectura distingue claramente dos elementos independientes.

## Asistente técnico

Constituye el producto principal desarrollado en este proyecto.

Es responsable de:

- ejecutar el pipeline RAG;
- recuperar conocimiento desde una base vectorial;
- construir el contexto enviado al modelo;
- seleccionar el backend de inferencia;
- generar respuestas técnicas;
- registrar métricas del sistema;
- supervisar la ejecución.

El asistente permanece inalterado independientemente del proyecto sobre el cual trabaje.

---

## Proyecto objetivo (Target Project)

Corresponde al sistema cuya documentación y código fuente serán utilizados como base de conocimiento.

Puede tratarse, por ejemplo, de:

- una aplicación .NET MAUI;
- un proyecto Java;
- un sistema PLC;
- un servicio backend;
- cualquier otro proyecto documentado.

Cada proyecto objetivo dispone de su propia base documental, embeddings y metadatos, permitiendo que un mismo asistente pueda especializarse dinámicamente sobre distintos dominios sin modificar su arquitectura.

---

# 3. Motivación

Los modelos de lenguaje ofrecen nuevas posibilidades para:

- consulta de documentación técnica;
- análisis de código fuente;
- comprensión arquitectónica de proyectos existentes;
- asistencia durante el desarrollo de software;
- generación de documentación técnica.

Sin embargo, su utilización sobre equipos con recursos limitados plantea diversos desafíos, especialmente durante tareas como:

- generación masiva de embeddings;
- recuperación semántica sobre grandes volúmenes documentales;
- procesos prolongados de inferencia.

Estas cargas pueden provocar:

- incremento sostenido de la temperatura del procesador;
- reducción del rendimiento del sistema;
- pérdida de estabilidad;
- interrupción inesperada de procesos.

Para afrontar estas limitaciones, el proyecto incorpora una arquitectura que combina:

- recuperación local del conocimiento;
- inferencia desacoplada;
- observabilidad del pipeline;
- supervisión térmica independiente.

De esta forma es posible experimentar con distintos proveedores de inferencia manteniendo el control sobre la arquitectura, los datos y los recursos del equipo.

---

# 4. Objetivo general

Diseñar e implementar una arquitectura RAG híbrida, modular y desacoplada para la construcción de asistentes técnicos reutilizables, manteniendo la recuperación del conocimiento de forma local, permitiendo utilizar distintos proveedores de inferencia y proporcionando mecanismos de observabilidad y supervisión térmica que favorezcan una operación estable sobre hardware con recursos limitados.

---

# 5. Objetivos específicos

## Plataforma del asistente

- Construir un asistente técnico reutilizable.
- Mantener desacoplados los componentes principales del sistema.
- Permitir la reutilización del pipeline sobre distintos proyectos objetivo.
- Facilitar la evolución incremental de la arquitectura.

---

## Recuperación del conocimiento

- Procesar documentación técnica local.
- Generar embeddings para representar semánticamente la información.
- Recuperar contexto relevante mediante búsqueda semántica.
- Mantener local la base de conocimiento utilizada por el sistema.
- Permitir sustituir la base documental sin modificar el pipeline.

---

## Inferencia

- Desacoplar completamente la generación de respuestas del resto del pipeline.
- Permitir la utilización de distintos backends de inferencia.
- Facilitar la incorporación de nuevos proveedores sin modificar la arquitectura principal.
- Reutilizar la misma construcción de contexto independientemente del backend seleccionado.

---

## Observabilidad

- Registrar cada consulta como una sesión independiente.
- Medir automáticamente el tiempo de las principales etapas del pipeline.
- Facilitar el análisis del rendimiento mediante métricas objetivas.
- Incorporar mecanismos de registro adicionales durante tareas de depuración cuando sea necesario.

---

## Supervisión del sistema

- Obtener información térmica del hardware.
- Supervisar continuamente la temperatura del procesador.
- Detectar condiciones térmicas críticas.
- Registrar eventos relevantes del sistema.
- Proteger automáticamente la ejecución del pipeline cuando sea necesario.

---

# 6. Arquitectura conceptual

La solución se organiza en dos niveles claramente diferenciados:

- **el asistente técnico**, que constituye el producto desarrollado en este proyecto;
- **el proyecto objetivo**, que representa el conocimiento sobre el cual trabajará el asistente.

Esta separación permite reutilizar completamente el pipeline RAG sobre distintos proyectos sin modificar su arquitectura interna.

---

## Asistente técnico

Responsable de:

- gestionar el pipeline RAG;
- recuperar conocimiento desde la base vectorial activa;
- construir el contexto enviado al modelo;
- seleccionar el backend de inferencia;
- registrar métricas del pipeline;
- supervisar la ejecución;
- proporcionar respuestas técnicas especializadas.

El asistente permanece independiente del proyecto cuya información consulta.

---

## Proyecto objetivo

Corresponde al conjunto de documentos y código fuente que alimentan la base de conocimiento.

Puede estar compuesto por:

- código fuente;
- documentación técnica;
- manuales;
- diagramas;
- archivos Markdown;
- documentación generada durante el desarrollo.

Actualmente el proyecto objetivo corresponde a una aplicación desarrollada en **.NET MAUI**, utilizada como primer caso de uso para validar la arquitectura del asistente.

En futuras versiones podrán incorporarse otros proyectos sin modificar el núcleo del sistema.

---

## Windows

Responsable del acceso al hardware físico.

Componentes principales:

- LibreHardwareMonitor.
- export_temp_server.py.
- Herramientas auxiliares de monitoreo.

Responsabilidades:

- obtener información de los sensores del sistema;
- publicar dicha información mediante un servicio HTTP;
- proporcionar los datos necesarios para la supervisión térmica.

---

## WSL2 Ubuntu

Responsable de la ejecución del asistente técnico.

Componentes principales:

- Pipeline RAG.
- Ollama.
- llm_backend.py.
- logger.py.
- thermal_watchdog.py.

Responsabilidades:

- procesamiento documental;
- generación de embeddings;
- recuperación semántica;
- construcción del contexto;
- selección del backend de inferencia;
- generación de respuestas;
- registro de métricas;
- supervisión de la ejecución.

---

# 7. Arquitectura de alto nivel

```text
                  ASISTENTE TÉCNICO RAG
               (Arquitectura_RAG_Termica)

                         │
                         ▼

             Selección del Proyecto Objetivo

                         │

        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼

 Proyecto objetivo A              Proyecto objetivo B
 (.NET MAUI actual)               (Futuro proyecto)

        │                                 │
        ▼                                 ▼

 Base documental local            Base documental local

        │                                 │
        └──────────────┬──────────────────┘
                       ▼

             Generación de embeddings

                       │
                       ▼

            Recuperación semántica (RAG)

                       │
                       ▼

            Construcción del contexto

                       │
                       ▼

                 llm_backend.py

            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼

         Ollama             OpenRouter

            │                     │
            └──────────┬──────────┘
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

# 8. Filosofía del proyecto

El proyecto evoluciona mediante cambios pequeños, controlados y completamente documentados.

Cada modificación busca mantener una arquitectura coherente y fácilmente mantenible antes que incorporar nuevas funcionalidades de forma acelerada.

Los principios que orientan el desarrollo son:

- separación de responsabilidades;
- bajo acoplamiento entre componentes;
- alta cohesión funcional;
- reutilización de componentes;
- observabilidad del sistema;
- documentación técnica extensa;
- evolución incremental de la arquitectura;
- independencia entre el asistente y el proyecto objetivo.

El asistente constituye una plataforma técnica reutilizable, mientras que el conocimiento especializado reside en la base documental del proyecto activo.

Esta separación facilita la utilización del mismo pipeline sobre diferentes proyectos sin alterar su funcionamiento interno.

---

# 9. Tecnologías principales

| Área | Tecnología |
|------|------------|
| Lenguaje principal | Python |
| Sistema anfitrión | Windows |
| Entorno de ejecución IA | WSL2 Ubuntu |
| Recuperación RAG | Base documental local |
| Modelo de embeddings | nomic-embed-text |
| Inferencia local | Ollama |
| Inferencia cloud | OpenRouter |
| Supervisión hardware | LibreHardwareMonitor |
| Servicio de monitoreo | Flask |
| Registro del pipeline | logger.py |
| Control de versiones | Git / GitHub |

---

# 10. Estado actual del proyecto

Al 28 de julio de 2026 la arquitectura dispone de:

- pipeline RAG modular;
- recuperación local del conocimiento;
- construcción dinámica del contexto utilizando los fragmentos recuperados;
- generación local de embeddings;
- backend de inferencia desacoplado;
- soporte para inferencia local y cloud;
- registro automático de métricas por consulta;
- registro opcional de información de depuración durante el desarrollo;
- supervisión térmica independiente;
- documentación técnica organizada por componentes.

Como primer caso de uso, el asistente trabaja sobre una base de conocimiento generada a partir de una aplicación desarrollada en **.NET MAUI**, permitiendo validar el funcionamiento del pipeline sobre un proyecto real.

---

# 11. Evolución prevista

La arquitectura ha sido diseñada para evolucionar sin modificar el núcleo del asistente.

Las siguientes etapas contemplan, entre otras posibilidades:

- incorporación de múltiples proyectos objetivo;
- selección dinámica de la base de conocimiento activa;
- ampliación de los proveedores de inferencia;
- mejoras en los mecanismos de recuperación semántica;
- incorporación progresiva de nuevas capacidades de observabilidad y análisis.

Cada nueva funcionalidad deberá respetar los principios de desacoplamiento, reutilización y evolución incremental que guían el desarrollo del proyecto.
