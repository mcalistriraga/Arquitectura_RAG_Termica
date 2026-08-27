# ADR-005 — Incorporación de supervisión térmica del pipeline

## Estado

Aceptado

## Fecha aproximada

Julio 2026

## Contexto

Durante las pruebas de ejecución local del sistema RAG utilizando Ollama y procesos de generación de embeddings, se observó que las cargas de procesamiento podían elevar significativamente la utilización del CPU.

El entorno objetivo del proyecto utiliza hardware limitado, sin aceleración dedicada para modelos de inteligencia artificial, por lo que tareas como:

- generación de embeddings;
- inferencia local;
- procesamiento intensivo de documentos;

pueden provocar incrementos importantes de temperatura y consumo.

Inicialmente el proyecto estaba enfocado exclusivamente en la funcionalidad RAG, pero las pruebas demostraron que la operación continua del sistema requería mecanismos de observabilidad y protección.

---

## Problema identificado

El pipeline podía ejecutar operaciones intensivas sin conocer el estado térmico del equipo.

Esto generaba riesgos:

- degradación del rendimiento por temperatura;
- inestabilidad del sistema;
- interrupciones inesperadas;
- posible daño por operación prolongada bajo alta carga.

Era necesario incorporar una capa externa de supervisión sin contaminar la lógica principal del RAG.

---

## Decisión

Se incorpora una arquitectura de supervisión térmica independiente del pipeline principal.

La supervisión se implementa como un componente externo encargado de:

- obtener métricas térmicas del sistema;
- analizar tendencias de temperatura;
- registrar eventos;
- tomar acciones preventivas cuando sea necesario.

La arquitectura conceptual queda:

