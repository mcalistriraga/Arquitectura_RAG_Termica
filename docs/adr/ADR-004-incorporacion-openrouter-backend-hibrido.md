# ADR-004 — Incorporación de backend híbrido mediante OpenRouter

## Estado

Aceptado

## Fecha aproximada

Julio 2026

## Contexto

Después de validar el funcionamiento inicial de la arquitectura RAG utilizando Ollama como backend local, se identificó una nueva necesidad:

Los modelos locales permiten mantener independencia y privacidad, pero presentan limitaciones relacionadas con:

- capacidad de razonamiento;
- tamaño de contexto disponible;
- velocidad de respuesta;
- recursos computacionales del hardware disponible.

El proyecto busca evolucionar hacia un asistente técnico capaz de acompañar el ciclo de vida completo del software, por lo que era necesario evaluar modelos con mayores capacidades sin abandonar la arquitectura local existente.

La solución no debía reemplazar el backend local, sino permitir coexistencia entre diferentes proveedores de inferencia.

---

## Decisión

Se incorpora una arquitectura de backend híbrido mediante una capa de abstracción común.

El sistema permitirá seleccionar entre:

- **LOCAL:** ejecución mediante Ollama.
- **CLOUD:** ejecución mediante proveedores externos compatibles con API, inicialmente mediante OpenRouter.

La arquitectura conceptual queda:

