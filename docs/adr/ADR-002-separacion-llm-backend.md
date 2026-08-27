# ADR-002 - Separación de la capa LLM Backend

## Estado

Aceptado

## Fecha aproximada

Julio 2026

## Contexto

Durante la evolución inicial de Arquitectura_RAG_Termica se implementó un pipeline RAG utilizando un modelo local ejecutado mediante Ollama.

La primera versión permitía:

- generar embeddings;
- recuperar información relevante;
- construir un contexto;
- enviar consultas al modelo local.

Sin embargo, la lógica del pipeline comenzó a depender directamente de la forma particular de comunicación con el modelo de inferencia.

Esto generaba un riesgo arquitectónico:

- dificultad para cambiar de modelo;
- dependencia directa de Ollama;
- imposibilidad de incorporar otros proveedores de inferencia;
- mezcla entre lógica RAG y comunicación con el modelo.

El proyecto busca construir un asistente técnico desacoplado, donde la gestión del conocimiento y la construcción del contexto sean independientes del motor utilizado para generar respuestas.

## Problema

¿Cómo permitir que el pipeline RAG pueda utilizar diferentes modelos o proveedores de inferencia sin modificar la lógica principal del sistema?

## Decisión

Se decide crear una capa de abstracción independiente para la comunicación con los modelos de lenguaje.

La responsabilidad de esta capa será:

- recibir una solicitud de inferencia;
- construir la comunicación específica con el proveedor;
- devolver la respuesta generada al pipeline.

La arquitectura conceptual pasa de:
