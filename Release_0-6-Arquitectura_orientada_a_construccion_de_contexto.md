# Release 0.6 — Arquitectura orientada a construcción de contexto

**Fecha:** 26 de agosto de 2026  
**Versión:** 0.6  
**Estado:** Propuesta de evolución / Roadmap de ingeniería  
**Módulo:** Arquitectura General / Pipeline RAG  
**Propósito:** Definición de la transición desde un RAG tradicional basado exclusivamente en recuperación semántica hacia una arquitectura desacoplada de construcción de contexto estructurado.

---

> **Resumen ejecutivo:**  
> La versión 0.6 redefine la posición del motor RAG dentro del sistema. La recuperación semántica deja de ser el centro único de la arquitectura para convertirse en un *Context Provider* especializado. Se formalizan las especificaciones para los contratos de datos (`IntentSpec`, `Knowledge Package`), la abstracción de múltiples fuentes de conocimiento (símbolos, grafos, ADRs) y la incorporación de las capas de poda (*Context Pruner*) y formateo estructurado (*Smart Context Builder*).

---

## 1. Resumen de la evolución

La versión 0.5 logró la integración efectiva y estable del contexto RAG en los backends local (Ollama) y cloud (OpenRouter). La **Release 0.6** aborda la limitación fundamental de los sistemas RAG tradicionales aplicados al desarrollo de software: un repositorio no es solo texto, sino una red interconectada de dependencias, símbolos, decisiones arquitectónicas y restricciones.

Esta versión establece las bases para cambiar la pregunta del sistema:
* **Fase anterior (v0.5):** *¿Cómo recuperar información relevante para responder una consulta?*
* **Nueva fase (v0.6):** *¿Cómo construir un paquete de conocimiento contextualizado y estructurado para que el LLM razoné correctamente sobre el sistema?*

---

## 2. Cambios arquitectónicos principales

### Redefinición del rol del RAG
* El pipeline RAG actual no se reemplaza; se reubica como una fuente de conocimiento (*Knowledge Source*) orientada a similitud semántica.
* Se desacopla la **obtención del conocimiento** de la **presentación del contexto al LLM**.

### Formalización de los Contratos de Datos
* **`IntentSpec`:** Estructura que captura la intención del desarrollador y guía la búsqueda estratégica en las distintas fuentes.
* **`Knowledge Package`:** Contenedor unificado e independiente del modelo que agrupa toda la información recuperada antes de ser procesada para el prompt.

### Arquitectura de Context Providers
* Definición de la interfaz estándar para adaptadores de conocimiento:
  * **Vector/Embeddings Provider** (Recuperación semántica actual).
  * **Symbol & AST Provider** (Estructura de clases, métodos e interfaces).
  * **Dependency Graph Provider** (Relaciones de llamadas y componentes).
  * **Architecture & ADR Provider** (Decisiones e historial del proyecto).
  * **Constraints Provider** (Reglas y convenciones del sistema).

### Incorporación del Context Pruner & Smart Context Builder
* **`Context Pruner`:** Módulo encargado de priorizar, eliminar redundancias y ajustar la información al presupuesto de tokens de la ventana de contexto del backend seleccionado.
* **`Smart Context Builder`:** Módulo encargado de formatear el `Knowledge Package` reducido en estructuras optimizadas para el LLM (Markdown técnico, XML semántico o bloques tipo ACI).

---

## 3. Diagrama conceptual de la arquitectura v0.6

```text
               Pregunta del desarrollador
                           │
                           ▼
              Comprensión de la intención
                           │
                           ▼
                      IntentSpec
                           │
                           ▼
                  Knowledge Sources
                           │
      ┌─────────────┬──────┴──────┬─────────────┐
      ▼             ▼             ▼             ▼
 Embeddings      Símbolos     Grafo AST     ADRs / Reglas
 (RAG v0.5)     (Código)    (Dependencias)  (Estructura)
      │             │             │             │
      └─────────────┼─────────────┴─────────────┘
                    ▼
            Context Providers
                    │
                    ▼
            Knowledge Package
                    │
                    ▼
             Context Pruner (Control de tokens)
                    │
                    ▼
          Smart Context Builder (XML/Markdown)
                    │
                    ▼
          llm_backend.py (Ollama / OpenRouter)
                    │
                    ▼
             Respuesta técnica

```
---

## 4. Estado del sistema e impacto en componentes existentes

| Componente | Estado en v0.5 | Evolución en v0.6 |
| :--- | :--- | :--- |
| **`llm_backend.py`** | Consumidor directo de la búsqueda RAG. | Consumidor del prompt generado por el *Smart Context Builder*. |
| **`logger.py`** | Registra tiempos de búsqueda RAG e inferencia. | Amplía métricas para medir latencia de *Providers*, *Package Assembly* y *Pruning*. |
| **`thermal_watchdog.py`** | Supervisión continua de CPU. | Mantiene la protección del hardware durante la extracción de AST/Símbolos en local. |
| **Búsqueda Vectorial** | Núcleo del pipeline. | Se convierte en el `VectorContextProvider`. |

---

## 5. Plan de implementación incremental (Roadmap v0.6.x)

* **v0.6.1 — Definición de Interfaces Python:** Crear las clases base/contratos (`dataclasses` o `Pydantic`) para `IntentSpec`, `KnowledgePackage` y la clase abstracta `BaseContextProvider`.
* **v0.6.2 — Migración del RAG actual:** Encapsular la lógica de búsqueda vectorial de v0.5 dentro de `VectorContextProvider`.
* **v0.6.3 — Primer Provider de Estructura:** Implementar un extractor liviano de símbolos/rutas para poblar la sección de código del `KnowledgePackage`.
* **v0.6.4 — Implementación del Context Builder:** Diseñar la serialización del contexto a XML semántico/Markdown estructurado.
* **v0.6.5 — Integración del Pruner:** Añadir control de presupuesto de tokens según el modelo activo en `llm_backend.py`.

---

## 6. Resultado esperado

Al finalizar el ciclo de la versión 0.6, el proyecto contará con una plataforma capaz de responder consultas no solo basándose en trozos de texto similares, sino entendiendo la estructura, dependencias y restricciones del proyecto objetivo, garantizando respuestas de mayor precisión técnica sin comprometer la estabilidad térmica del equipo.

