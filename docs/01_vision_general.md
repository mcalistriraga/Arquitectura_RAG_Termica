# Visión General del Proyecto

## Nombre del proyecto

**Arquitectura RAG híbrida con supervisión térmica y arquitectura desacoplada para asistentes técnicos**

---

# 1. Descripción general

**Arquitectura_RAG_Termica** es un proyecto experimental cuyo propósito es diseñar e implementar una arquitectura **RAG (Retrieval-Augmented Generation)** modular, desacoplada y ampliamente documentada, orientada a la construcción de asistentes técnicos especializados.

El proyecto combina distintas áreas de la ingeniería de software y de la inteligencia artificial:

- procesamiento documental local;
- generación de embeddings;
- recuperación semántica de información;
- inferencia mediante modelos de lenguaje;
- observabilidad del pipeline;
- supervisión térmica del hardware;
- mecanismos automáticos de protección.

La arquitectura ha evolucionado desde un sistema basado exclusivamente en modelos locales hacia una arquitectura híbrida en la que la recuperación del conocimiento permanece local mientras que la inferencia puede realizarse mediante distintos proveedores sin modificar el núcleo del sistema.

El objetivo principal no consiste únicamente en obtener respuestas mediante inteligencia artificial, sino en construir una arquitectura organizada, mantenible y preparada para evolucionar de forma progresiva.

---

# 2. Motivación

Los modelos de lenguaje ofrecen nuevas posibilidades para la consulta de documentación técnica, el análisis de código y la asistencia al desarrollo de software.

Al mismo tiempo, su ejecución representa importantes desafíos cuando se trabaja sobre equipos con recursos limitados, especialmente durante tareas como:

- generación masiva de embeddings;
- recuperación semántica sobre bases documentales;
- procesos de inferencia prolongados.

Estas cargas pueden provocar:

- incremento sostenido de la temperatura del procesador;
- reducción del rendimiento del sistema;
- pérdida de estabilidad;
- interrupción inesperada de procesos.

Para abordar estas limitaciones, el proyecto incorpora una arquitectura que combina:

- recuperación local del conocimiento;
- inferencia desacoplada;
- observabilidad del pipeline;
- supervisión térmica independiente.

De esta forma es posible experimentar con distintas estrategias de inferencia manteniendo el control sobre los datos, la arquitectura y los recursos del equipo.

---

# 3. Objetivo general

Diseñar e implementar una arquitectura RAG híbrida, modular y desacoplada que mantenga la recuperación del conocimiento de forma local, permita utilizar distintos proveedores de inferencia y proporcione mecanismos de observabilidad y supervisión térmica para favorecer una operación estable sobre hardware con recursos limitados.

---

# 4. Objetivos específicos

## Recuperación del conocimiento

- Procesar documentación técnica local.
- Generar embeddings para representar semánticamente la información.
- Recuperar contexto relevante mediante búsqueda semántica.
- Mantener local la base de conocimiento utilizada por el sistema.

---

## Inferencia

- Desacoplar la generación de respuestas del resto del pipeline.
- Permitir la utilización de distintos backends de inferencia.
- Facilitar la incorporación de nuevos proveedores sin modificar la arquitectura principal.

---

## Observabilidad

- Registrar cada consulta como una sesión independiente.
- Medir automáticamente el tiempo de las principales etapas del pipeline.
- Facilitar el análisis del rendimiento del sistema mediante métricas objetivas.

---

## Supervisión del sistema

- Obtener información térmica del hardware.
- Supervisar continuamente la temperatura del procesador.
- Detectar condiciones térmicas críticas.
- Registrar eventos relevantes del sistema.
- Proteger la ejecución del pipeline cuando sea necesario.

---

# 5. Arquitectura conceptual

La solución se organiza en dos entornos principales con responsabilidades claramente diferenciadas.

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

Responsable de la ejecución del sistema RAG.

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
- inferencia mediante el backend seleccionado;
- registro de métricas;
- supervisión de la ejecución.

---

# 6. Arquitectura de alto nivel

```text
                     DOCUMENTACIÓN

                           │
                           ▼

                Generación de embeddings

                           │
                           ▼

                 Base documental local

                           │
                           ▼

                       Consulta usuario

                           │
                           ▼

                       Recuperación RAG

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

                     Respuesta LLM



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

# 7. Filosofía del proyecto

El proyecto evoluciona mediante cambios pequeños y controlados.

Cada modificación busca mantener una arquitectura coherente y fácilmente mantenible antes que incorporar nuevas funcionalidades de forma acelerada.

Los principios que orientan el desarrollo son:

- separación de responsabilidades;
- bajo acoplamiento entre componentes;
- alta cohesión funcional;
- observabilidad del sistema;
- documentación técnica extensa;
- evolución incremental de la arquitectura.

Más que una aplicación concreta, el proyecto constituye una plataforma experimental para estudiar la integración entre inteligencia artificial, arquitectura de software y administración de sistemas.

---

# 8. Tecnologías principales

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
| Control de versiones | Git / GitHub |

---

# 9. Estado actual del proyecto

Al 24 de julio de 2026 la arquitectura dispone de:

- pipeline RAG modular;
- recuperación local del conocimiento;
- generación local de embeddings;
- backend de inferencia desacoplado;
- soporte para inferencia local y cloud;
- registro automático de métricas por consulta;
- supervisión térmica independiente;
- documentación técnica organizada por componentes.

La arquitectura continúa evolucionando mediante mejoras incrementales, manteniendo como prioridad la estabilidad del diseño y la coherencia entre el código y su documentación.

