# ADR-013: Orquestación multiproyecto y resolución dinámica de workspace

* **Estado:** Propuesto
* **Fecha:** 27 de agosto de 2026
* **Autor:** Manuel Calistri

---

## Contexto y problema

En la arquitectura RAG actual, el pipeline de extracción (`knowledge_filter`, `symbols_extractor`), generación vectorial (`embed.py`) y consulta (`query.py`) opera sobre un único *Target Project* activo.

Sin embargo, a medida que el sistema evoluciona para soportar múltiples bases de conocimiento (distintos proyectos de prueba o entornos de software), los scripts globales ubicados en la suite de orquestación carecen de un mecanismo estandarizado y desacoplado para determinar cuál es el espacio de trabajo (*workspace*) activo sobre el cual deben operar.

Resolver las rutas de forma estática o rígida en el código fuente introduce acoplamiento, riesgo de contaminación cruzada entre bases vectoriales y dificulta la alternancia limpia entre diferentes proyectos.

---

## Decisión de arquitectura

Se establece una **jerarquía de configuración en dos niveles** para la resolución dinámica de espacios de trabajo y políticas de conocimiento:

1. **Nivel Global (Orquestador de Contexto):**
   El directorio global de scripts contendrá un puntero de contexto activo (`active_project.conf`) que define exclusivamente la ruta al *workspace* del proyecto objetivo en ejecución.

2. **Nivel Local (Configuración del Proyecto):**
   Cada *workspace* individual mantendrá sus propios artefactos de configuración (`project.conf`, `knowledge_policy.conf`) y sus bases de datos/conocimiento locales (`knowledge/symbols/` y `knowledge/embeddings/`).

3. **Contrato de Resolución Unificada:**
   Todos los módulos del pipeline (`knowledge_filter.py`, `symbols_extractor.py`, `embed.py`, `query.py`) deberán resolver el contexto de ejecución consumiendo obligatoriamente el servicio común de carga de configuración (`config_loader.py`), garantizando que la totalidad del pipeline apunte atómicamente al mismo proyecto activo.

---

## Consecuencias

### Positivas
* **Aislamiento Total:** Cero contaminación de datos o índices vectoriales entre diferentes proyectos.
* **Conmutación Inmediata:** Permite alternar la ejecución del pipeline entre distintos proyectos cambiando únicamente la referencia del proyecto activo sin modificar el código fuente.
* **Consistencia Operativa:** Garantiza que el generador de embeddings (`embed.py`) y el orquestador RAG (`query.py`) consulten exactamente la misma fuente de la verdad.

### Negativas / Riesgos
* Requiere refactorizar la carga de rutas estáticas en `query.py` para adoptar la resolución dinámica por `config_loader.py`.

---

## Decisiones fuera del alcance de este ADR

Este ADR define el contrato de resolución de espacios de trabajo y la jerarquía de configuración multiproyecto, pero no pretende convertir las herramientas auxiliares de administración en parte del contrato arquitectónico.

Quedan fuera del alcance de este ADR:

- la creación de scripts de interfaz CLI para conmutación automática de proyectos (e.g., `set_project.py`);
- el almacenamiento simultáneo de múltiples workspaces en una única base vectorial unificada;
- la sincronización o migración de datos entre proyectos distintos;
- la gestión de permisos del sistema de archivos a nivel de workspace.

La implementación podrá evolucionar sin modificar este ADR mientras respete el contrato establecido:

**`active_project.conf` determina el workspace activo y `config_loader.py` garantiza la resolución unificada de rutas para todo el pipeline.**
