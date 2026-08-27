# Hoja de Ruta Arquitectónica

**Proyecto:** Arquitectura_RAG_Termica

**Documento:** 09_hoja_de_ruta_arquitectura.md

**Versión:** 1.0

**Fecha:** Julio 2026

---

# Objetivo

Este documento describe la evolución prevista de la arquitectura del proyecto.

No constituye un plan rígido de desarrollo, sino una guía para orientar la incorporación progresiva de nuevas capacidades, procurando mantener la estabilidad de la arquitectura y la coherencia entre implementación, documentación y objetivos del proyecto.

Cada nueva funcionalidad deberá aportar un beneficio verificable antes de incorporarse al pipeline principal.

---

# Filosofía de evolución

Desde su inicio, el proyecto ha evolucionado mediante pequeños cambios controlados.

Cada etapa ha resuelto un problema concreto antes de avanzar hacia el siguiente.

Esta filosofía continuará guiando el desarrollo futuro.

Los principios fundamentales son:

- evolución incremental;
- bajo acoplamiento;
- alta cohesión;
- observabilidad del sistema;
- documentación sincronizada con la implementación;
- incorporación de complejidad únicamente cuando resulte necesaria.

---

# Estado actual

Actualmente la arquitectura dispone de:

- recuperación semántica mediante embeddings;
- contexto arquitectónico mediante `symbols.jsonl`;
- integración efectiva del contexto RAG en el prompt;
- backend híbrido desacoplado (LOCAL / CLOUD);
- observabilidad mediante `logger.py`;
- supervisión térmica independiente;
- documentación técnica organizada.

El **Release 0.5** consolidó el objetivo principal de esta etapa:

> El conocimiento recuperado por el pipeline participa activamente en la generación de respuestas del modelo.

---

# Evolución prevista

La evolución del proyecto continuará mejorando progresivamente la calidad del contexto entregado al modelo de lenguaje.

En lugar de aumentar rápidamente la complejidad del sistema, cada nueva etapa se apoyará sobre la anterior.

```text
Calidad del contexto
          │
          ▼
Calidad de las respuestas
          │
          ▼
Asistente técnico cada vez más consciente del proyecto
```

---

# Hoja de ruta inmediata

## Release 0.6

### Objetivo

Incrementar la calidad del contexto recuperado antes de incorporar nuevas fuentes de información.

Las líneas principales de trabajo serán:

### 1. Observabilidad de la recuperación

Analizar con mayor detalle el comportamiento del proceso de recuperación.

Ejemplos:

- similitud de cada chunk;
- ranking obtenido;
- archivos recuperados;
- tamaño del contexto;
- distribución de resultados.

El objetivo es comprender cómo recupera actualmente el pipeline antes de modificarlo.

---

### 2. Mejora del ranking

Evaluar estrategias para incrementar la relevancia de los resultados recuperados.

Entre ellas:

- ajuste de `TOP_K`;
- revisión del umbral de similitud;
- reducción de duplicados;
- diversidad de archivos recuperados;
- priorización de resultados relevantes.

---

### 3. Construcción del contexto

Mejorar la organización del contexto enviado al modelo.

No se pretende recuperar mayor cantidad de información, sino estructurar mejor la ya disponible.

---

## 4. Visión a largo plazo

La meta final de **Arquitectura_RAG_Termica** es consolidar un asistente técnico de desarrollo especializado, capaz de razonar sobre la arquitectura de software en hardware limitado de manera segura, predecible y térmicamente responsable[cite: 10].

Aunque el caso de prueba actual se centra en .NET MAUI y C#, **la arquitectura fue diseñada para ser extensible a múltiples lenguajes y formatos**[cite: 10]. El subsistema de extracción (KS2) evolucionará incorporando de forma modular nuevos parsers[cite: 10]:
* **Corto/Mediano plazo:** Parsers para lenguajes de marcado y diseño como **CSS** y XAML[cite: 10].
* **Largo plazo:** Parsers para lenguajes de propósito general como **Java**, **C++**, **Python**, **JavaScript** o **SQL**[cite: 10].

Esta capacidad políglota permitirá al sistema analizar proyectos con *stacks* tecnológicos híbridos, manteniendo el principio de bajo acoplamiento mediante cargadores dinámicos de módulos[cite: 10]. El sistema continuará priorizando la inteligencia en la **fase de construcción del contexto**, manteniendo el layer de inferencia (`llm_backend.py`) como una pieza 100% intercambiable e independiente[cite: 10].

---

### 5. Métricas de recuperación

Ampliar la observabilidad mediante nuevas métricas relacionadas con la calidad del contexto.

Por ejemplo:

- número de chunks utilizados;
- similitud media;
- cantidad de documentos representados;
- tamaño aproximado del contexto;
- relación entre recuperación e inferencia.

---

### 6. Evaluación de modelos

Comparar distintos modelos de inferencia utilizando exactamente el mismo contexto recuperado.

Esto permitirá evaluar objetivamente el comportamiento de cada backend sin modificar el pipeline.

---

# Evolución posterior

Una vez consolidado el Release 0.6 podrán estudiarse nuevas capacidades.

Entre ellas:

- clasificación automática de consultas;
- nuevas fuentes de contexto;
- recuperación basada en dependencias;
- historial de decisiones arquitectónicas;
- proveedores adicionales de conocimiento;
- mejoras avanzadas en la construcción del contexto.

Estas capacidades se incorporarán únicamente cuando exista una necesidad demostrable y puedan mantenerse desacopladas del resto del sistema.

---

# Visión a largo plazo

La arquitectura persigue la construcción de un asistente técnico especializado capaz de comprender progresivamente un proyecto de software.

La inteligencia del sistema deberá concentrarse principalmente en la construcción del contexto, mientras que el backend de inferencia permanecerá completamente desacoplado y sustituible.

El objetivo final no consiste en construir un generador automático de código, sino un asistente capaz de comprender la arquitectura, la documentación y el conocimiento acumulado del proyecto para colaborar de manera efectiva durante todo su ciclo de vida.

---

# Principio de evolución

La incorporación de nuevas ideas deberá responder siempre a una necesidad real observada durante el desarrollo.

La complejidad no constituye un objetivo del proyecto.

Cada nuevo componente deberá justificar claramente el beneficio que aporta a la calidad de las respuestas, a la mantenibilidad de la arquitectura o a la comprensión del proyecto.

La evolución continuará realizándose mediante pequeños cambios verificables, preservando en todo momento la estabilidad del sistema y la coherencia entre código, documentación y arquitectura.
