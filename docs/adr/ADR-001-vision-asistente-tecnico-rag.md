# ADR-001: Definición de la visión del asistente técnico basado en RAG

## Estado

Aceptado

## Fecha aproximada

Julio 2026

## Contexto

Durante la etapa inicial del proyecto Arquitectura_RAG_Termica se evaluó la posibilidad de utilizar modelos de lenguaje locales como apoyo al desarrollo de software.

La motivación principal era disponer de un asistente técnico capaz de consultar información propia del proyecto, evitando depender exclusivamente del conocimiento general del modelo de lenguaje.

Se identificó que un modelo LLM por sí solo no posee conocimiento actualizado del código, documentación ni decisiones específicas de un proyecto particular.

Por esta razón se decidió explorar una arquitectura basada en Retrieval Augmented Generation (RAG), donde la información relevante del proyecto pudiera ser recuperada y proporcionada al modelo antes de generar una respuesta.

La visión inicial fue construir un asistente capaz de:

- consultar documentación técnica del proyecto;
- analizar código fuente disponible;
- responder preguntas relacionadas con la arquitectura;
- ayudar durante las etapas del ciclo de vida del software.

## Decisión

Se adopta como visión principal del proyecto:

> Construir un asistente técnico basado en RAG local, capaz de utilizar el conocimiento propio del proyecto para proporcionar respuestas contextualizadas al desarrollador.

La arquitectura inicial estará orientada a:

- mantener una base de conocimiento del proyecto;
- recuperar información relevante mediante búsqueda semántica;
- utilizar modelos LLM desacoplados del mecanismo de recuperación;
- permitir evolución progresiva hacia capacidades más avanzadas.

## Alternativas consideradas

### Utilizar únicamente un LLM general

Descartado.

Aunque los modelos generales poseen amplio conocimiento, no conocen:

- estructura interna del proyecto;
- decisiones específicas;
- código actualizado;
- restricciones particulares.

### Utilizar servicios externos cerrados como única solución

No adoptado inicialmente.

Se busca mantener control sobre:

- datos del proyecto;
- infraestructura;
- modelos utilizados;
- posibilidad de ejecución local.

## Consecuencias positivas

- Se establece una dirección clara para la evolución del proyecto.
- El conocimiento del proyecto pasa a ser un componente explícito de la arquitectura.
- Se permite experimentar con diferentes modelos LLM sin cambiar la visión general.
- Se mantiene la posibilidad de ejecución local.

## Consecuencias negativas

- La arquitectura requiere construir y mantener componentes adicionales.
- La calidad de las respuestas dependerá de la calidad del conocimiento recuperado.
- Será necesario resolver posteriormente problemas de indexación, contexto y mantenimiento de información.

## Notas posteriores

Esta decisión inicial permitió evolucionar posteriormente hacia:

- separación del backend LLM;
- incorporación de modelos locales;
- backend híbrido local/cloud;
- mecanismos de supervisión;
- investigación sobre construcción avanzada de contexto.

Sin embargo, esas capacidades no formaban parte del alcance inicial de esta decisión.
