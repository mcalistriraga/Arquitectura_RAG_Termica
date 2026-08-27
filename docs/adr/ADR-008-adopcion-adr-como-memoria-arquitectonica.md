# ADR-008 — Adopción de ADR como memoria arquitectónica del proyecto

## Estado

Aceptado

## Fecha aproximada

Julio 2026

## Contexto

Durante la evolución del proyecto Arquitectura_RAG_Termica se identificó que el conocimiento necesario para comprender un sistema de software no está contenido únicamente en su código fuente.

Existen decisiones arquitectónicas que explican:

- por qué una tecnología fue seleccionada;
- por qué una alternativa fue descartada;
- qué restricciones deben mantenerse;
- qué principios deben respetarse durante la evolución.

Inicialmente estas decisiones fueron registradas de manera distribuida mediante documentación técnica, conversaciones de diseño y cambios en el código.

Esta información resulta valiosa para la futura construcción de un asistente técnico con conocimiento profundo del ciclo de vida del proyecto.

---

## Problema identificado

Sin un mecanismo formal de registro histórico, con el tiempo pueden perderse decisiones importantes.

Ejemplos:

- ¿Por qué se separó `llm_backend.py` del pipeline RAG?
- ¿Por qué se incorporó supervisión térmica?
- ¿Por qué se decidió mantener Ollama como backend local?
- ¿Por qué evolucionar hacia construcción de contexto?

La documentación tradicional describe el estado actual, pero no siempre conserva la razón detrás de las decisiones.

---

## Decisión

Se adopta el uso de Architecture Decision Records (ADR) como mecanismo formal para registrar decisiones arquitectónicas relevantes del proyecto.

Se crea la estructura:

