# ADR-011 — Evolución de logger.py hacia servicio común de observabilidad

## Estado

Aceptado

## Fecha aproximada

Agosto 2026

---

# Contexto

Durante la evolución de Arquitectura_RAG_Termica se identificó que
el mecanismo de registro implementado inicialmente en `logger.py`
fue diseñado específicamente alrededor del flujo de consultas
definido en `query.py`.

La primera versión del componente permitió registrar:

- inicio de consultas;
- selección de modo;
- backend utilizado;
- modelo de lenguaje;
- métricas del pipeline RAG.

Este diseño fue suficiente durante las primeras etapas del proyecto,
pero introduce un acoplamiento entre el sistema de observabilidad
y la lógica específica del pipeline de inferencia.

Con la incorporación de nuevos componentes como:

- `knowledge_filter.py`;
- futuros extractores;
- proveedores de conocimiento;
- generadores de embeddings;
- herramientas de análisis arquitectónico;

se requiere que el mecanismo de registro pueda ser utilizado por
cualquier módulo del sistema sin duplicar lógica.

---

# Problema identificado

Actualmente `logger.py` conoce conceptos específicos del dominio RAG,
por ejemplo:

- preguntas realizadas por usuarios;
- modelos IA;
- backend de inferencia;
- tiempos de embedding;
- búsqueda semántica;
- generación de respuestas.

Esto provoca:

- dependencia directa respecto a `query.py`;
- dificultad para reutilizarlo desde otros módulos;
- necesidad de crear mecanismos de registro diferentes;
- dispersión de código de diagnóstico.

La observabilidad debe ser una capacidad transversal de la arquitectura,
no una funcionalidad exclusiva del proceso de consulta.

---

# Decisión

Se evoluciona `logger.py` hacia un componente genérico de
observabilidad utilizado por todos los módulos del sistema.

El logger dejará de representar únicamente sesiones de consulta
y pasará a proporcionar servicios generales de:

- registro de eventos;
- información de diagnóstico;
- trazabilidad de ejecución;
- medición temporal;
- generación de archivos de log independientes por componente.

---

# Nueva responsabilidad arquitectónica

`logger.py` será responsable únicamente de:

- crear registros de ejecución;
- almacenar mensajes;
- manejar niveles de información;
- proporcionar marcas temporales;
- facilitar diagnóstico técnico.

No será responsable de:

- conocer el flujo RAG;
- interpretar consultas;
- conocer modelos IA;
- administrar embeddings;
- decidir qué información registrar.

---

# Nuevo modelo conceptual

