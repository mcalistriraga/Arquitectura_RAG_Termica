# ADR-007 — Knowledge Package como capa intermedia de contexto

## Estado

Propuesto / En evolución

## Fecha aproximada

Julio 2026

## Contexto

Durante la evolución hacia una arquitectura de construcción inteligente de contexto (ADR-006), se identificó la necesidad de separar las etapas de recuperación de información y generación del prompt final.

En un RAG tradicional, los resultados recuperados suelen pasar directamente al modelo de lenguaje.

Este enfoque presenta limitaciones:

- mezcla información de diferentes fuentes sin una estructura común;
- dificulta aplicar reglas de prioridad;
- complica controlar el tamaño del contexto;
- acopla la recuperación de conocimiento con un modelo específico.

La arquitectura propuesta requiere integrar diferentes fuentes:

- embeddings;
- símbolos del código;
- dependencias;
- documentación;
- decisiones arquitectónicas;
- restricciones del proyecto.

Estas fuentes tienen naturalezas diferentes y requieren una representación intermedia común.

---

# Problema identificado

Sin una capa intermedia, el flujo sería:

