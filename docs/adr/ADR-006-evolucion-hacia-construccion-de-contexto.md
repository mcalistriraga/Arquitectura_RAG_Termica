# ADR-006 — Evolución hacia construcción de contexto

## Estado

Aceptado

## Fecha aproximada

Julio 2026

## Contexto

Durante la evolución del sistema RAG se comprobó que la recuperación basada únicamente en embeddings era útil para localizar información relacionada, pero insuficiente para responder consultas complejas sobre un proyecto de software.

Las consultas de un desarrollador normalmente requieren información de diferentes dimensiones:

- código fuente relacionado;
- arquitectura del sistema;
- dependencias entre componentes;
- decisiones tomadas anteriormente;
- restricciones conocidas;
- documentación técnica.

Un sistema RAG tradicional recupera principalmente información por similitud semántica, pero no representa completamente la estructura ni la historia del software.

---

## Problema identificado

El enfoque inicial podía responder preguntas como:

> "¿Dónde aparece este concepto dentro de la documentación?"

pero tenía dificultades con preguntas como:

> "¿Qué impacto tendría modificar este módulo?"

o:

> "¿Por qué este componente fue diseñado de esta manera?"

Estas preguntas requieren conocimiento estructurado del sistema.

El problema principal dejó de ser únicamente la recuperación de información y pasó a ser la construcción de un contexto adecuado para el modelo de lenguaje.

---

## Decisión

Se decide evolucionar la arquitectura desde un modelo:

