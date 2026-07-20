# Visión General del Proyecto

## Nombre del proyecto

**Arquitectura RAG local con supervisión térmica y mecanismos de protección para ejecución segura en hardware limitado**

---

# 1. Descripción general

Este proyecto explora la ejecución local de modelos de lenguaje (LLM) mediante una arquitectura de Recuperación Aumentada de Generación (**RAG - Retrieval Augmented Generation**), incorporando mecanismos de supervisión y protección del sistema para operar de forma segura en equipos con recursos computacionales limitados.

La propuesta combina:

* procesamiento documental local,
* generación de embeddings,
* recuperación semántica de información,
* modelos de lenguaje ejecutados localmente mediante Ollama,
* supervisión térmica del hardware,
* mecanismos automáticos de protección ante condiciones críticas.

El objetivo principal es construir una arquitectura experimental que permita utilizar capacidades de inteligencia artificial generativa sin depender exclusivamente de servicios externos, manteniendo el control sobre los datos, los modelos y los recursos del equipo.

---

# 2. Motivación

Los modelos de lenguaje locales ofrecen ventajas importantes:

* privacidad de la información,
* independencia de servicios externos,
* posibilidad de experimentar y aprender sobre arquitecturas de IA,
* control completo del entorno de ejecución.

Sin embargo, su ejecución puede representar una carga importante para equipos con recursos limitados, especialmente durante:

* generación de embeddings sobre grandes volúmenes documentales,
* consultas con modelos locales,
* procesos prolongados de inferencia.

Estas cargas pueden provocar:

* aumento sostenido de temperatura del procesador,
* pérdida de estabilidad del sistema,
* degradación del rendimiento,
* interrupción inesperada de procesos.

Para abordar este escenario se incorpora una capa de supervisión térmica capaz de monitorear el comportamiento del hardware y actuar automáticamente cuando se alcanzan condiciones que puedan comprometer la estabilidad del sistema.

---

# 3. Objetivo general

Diseñar e implementar una arquitectura experimental para ejecutar aplicaciones RAG locales mediante modelos LLM ejecutados en el equipo, incorporando mecanismos de supervisión térmica y protección automática para garantizar una operación segura en hardware limitado.

---

# 4. Objetivos específicos

## Inteligencia artificial local

* Ejecutar modelos de lenguaje localmente mediante Ollama.
* Integrar modelos de embeddings para representación semántica de documentos.
* Construir un flujo RAG completo para consulta sobre información propia.

## Gestión documental

* Procesar documentos locales.
* Generar una base de conocimiento mediante embeddings.
* Recuperar información relevante para complementar las respuestas del modelo.

## Supervisión del sistema

* Obtener información térmica del hardware.
* Implementar un servicio intermedio para la lectura de sensores.
* Supervisar la temperatura durante la ejecución de procesos intensivos.

## Protección automática

* Detectar condiciones térmicas críticas.
* Registrar eventos de protección.
* Detener procesos RAG cuando sea necesario.
* Permitir la recuperación del sistema después de normalizarse las condiciones térmicas.

---

# 5. Arquitectura conceptual

El proyecto está compuesto por dos entornos principales:

## Windows

Responsable de la interacción con el hardware físico.

Componentes:

* LibreHardwareMonitor.
* Servicio de exportación térmica mediante Flask.
* Herramientas auxiliares de monitoreo.

Responsabilidad:

Obtener información real de los sensores del equipo y publicarla para otros componentes del sistema.

---

## WSL2 Ubuntu

Responsable de la ejecución de inteligencia artificial.

Componentes:

* Ollama.
* Modelos LLM locales.
* Scripts Python del pipeline RAG.
* Thermal Watchdog.

Responsabilidad:

Ejecutar los procesos de inteligencia artificial y aplicar mecanismos de protección cuando las condiciones del sistema lo requieran.

---

# 6. Arquitectura de alto nivel

```text
                         DOCUMENTOS
                              |
                              v
                     Generación de embeddings
                              |
                              v
                       Base documental local
                              |
                              v

Usuario ---> Consulta RAG ---> Recuperación ---> Contexto
                                                  |
                                                  v
                                             Ollama LLM
                                                  |
                                                  v
                                             Respuesta


                 SUPERVISIÓN DEL SISTEMA

LibreHardwareMonitor
          |
          v
export_temp_server.py
          |
          v
thermal_watchdog.py
          |
          v
Protección de procesos RAG
```

---

# 7. Filosofía del proyecto

El proyecto busca demostrar que la ejecución local de modelos de inteligencia artificial puede realizarse incluso en equipos con recursos limitados mediante una arquitectura organizada que considere:

* uso eficiente de recursos,
* observabilidad del sistema,
* separación de responsabilidades,
* protección automática,
* control sobre los datos.

Más que una aplicación puntual, representa una experiencia práctica de integración entre inteligencia artificial local, administración de sistemas y automatización.

---

# 8. Tecnologías principales

| Área                       | Tecnología           |
| -------------------------- | -------------------- |
| Sistema operativo IA       | WSL2 Ubuntu          |
| Sistema operativo hardware | Windows              |
| Modelo LLM                 | Ollama + llama3.2:3b |
| Embeddings                 | nomic-embed-text     |
| Lenguaje principal         | Python               |
| API de supervisión         | Flask                |
| Monitoreo hardware         | LibreHardwareMonitor |
| Arquitectura IA            | RAG                  |
| Control de versiones       | Git / GitHub         |

---

# 9. Estado actual del proyecto

Actualmente se cuenta con:

* Pipeline RAG funcional.
* Generación de embeddings documentales.
* Consultas mediante modelo local Ollama.
* Servicio de monitoreo térmico Windows.
* Watchdog térmico ejecutándose en WSL.
* Registro de eventos críticos.
* Protección automática del proceso RAG ante sobretemperatura.

Las próximas etapas contemplan:

* consolidación de documentación técnica,
* pruebas finales,
* organización del repositorio,
* publicación del proyecto.
