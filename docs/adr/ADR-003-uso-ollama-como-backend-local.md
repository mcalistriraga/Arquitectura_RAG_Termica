# ADR-003 — Uso de Ollama como backend local de inferencia LLM

## Estado

Aceptado

## Fecha aproximada

Julio 2026

## Contexto

Durante la evolución inicial del proyecto Arquitectura_RAG_Termica se identificó la necesidad de incorporar capacidades de inferencia mediante modelos de lenguaje locales.

Los objetivos principales eran:

- experimentar con modelos LLM sin depender obligatoriamente de servicios externos;
- mantener control sobre los datos del proyecto;
- permitir ejecución en hardware disponible;
- evaluar la viabilidad de una arquitectura RAG completamente local;
- desacoplar la lógica del asistente respecto al proveedor específico del modelo.

En esta etapa el proyecto se encontraba enfocado en construir una base experimental de RAG utilizando documentación y código propio como fuente de conocimiento.

Se evaluaron diferentes alternativas para ejecutar modelos locales, seleccionando Ollama por su simplicidad de integración y por ofrecer una interfaz HTTP compatible con arquitecturas desacopladas.

---

## Decisión

Se adopta **Ollama como backend local inicial de inferencia LLM**.

La comunicación con el modelo se realizará mediante una interfaz independiente, evitando que los módulos superiores del sistema dependan directamente de la implementación del motor de inferencia.

La arquitectura queda conceptualmente:

