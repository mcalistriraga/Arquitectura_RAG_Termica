# Arquitectura RAG Experimental para Proyectos de Software

> Arquitectura experimental orientada a mejorar la construcción del contexto para consultas sobre proyectos de software, manteniendo desacopladas la recuperación del conocimiento, la construcción del contexto, la inferencia, la observabilidad y la supervisión térmica.

---

## 1. Descripción

**Arquitectura_RAG_Termica** es un proyecto experimental orientado al diseño y evolución de una arquitectura **RAG (Retrieval-Augmented Generation)** para consultas relacionadas con proyectos de software.

El objetivo principal no consiste únicamente en recuperar fragmentos mediante búsqueda semántica, sino en investigar cómo diferentes fuentes de conocimiento pueden recuperarse, organizarse e integrarse para construir un contexto más preciso, coherente y útil antes de la etapa de inferencia.

La arquitectura mantiene separadas las responsabilidades de:

* adquisición y preparación del conocimiento;
* recuperación semántica;
* extracción de información estructurada del código;
* construcción del contexto;
* inferencia mediante modelos de lenguaje;
* observabilidad del pipeline;
* supervisión térmica del entorno de ejecución.

Esta separación permite evolucionar cada componente de forma independiente y experimentar con nuevas estrategias sin modificar innecesariamente el núcleo del sistema.

El proyecto integra distintas áreas de conocimiento:

* Inteligencia Artificial aplicada mediante modelos de lenguaje.
* Recuperación Semántica de Información.
* Arquitecturas RAG.
* Construcción y organización del contexto para inferencia.
* Extracción heurística de información estructurada desde código fuente.
* Arquitectura de software orientada al bajo acoplamiento y alta cohesión.
* Observabilidad mediante registros, métricas y mecanismos de depuración.
* Supervisión térmica para proteger el hardware durante cargas intensivas.

Aunque inicialmente el proyecto estuvo orientado principalmente a la ejecución local de modelos mediante Ollama, la arquitectura evolucionó hacia un enfoque híbrido en el que la recuperación del conocimiento permanece desacoplada de la inferencia.

Actualmente, la inferencia puede realizarse mediante diferentes backends sin modificar la lógica principal de recuperación y construcción del contexto.

El objetivo a largo plazo es evolucionar progresivamente esta arquitectura hacia un **asistente técnico capaz de conocer y utilizar información actualizada de un proyecto de software para colaborar con el desarrollador durante su ciclo de vida**.

---

## 2. Objetivos del proyecto

Los principales objetivos son:

* Diseñar una arquitectura RAG modular y desacoplada para consultas sobre proyectos de software.
* Mejorar progresivamente la calidad del contexto entregado a los modelos de lenguaje.
* Mantener separadas la recuperación del conocimiento y la generación de respuestas.
* Integrar diferentes fuentes de conocimiento del proyecto.
* Incorporar información estructurada procedente del código fuente.
* Facilitar la evolución del pipeline mediante componentes independientes.
* Evaluar diferentes estrategias de recuperación y construcción de contexto.
* Permitir el uso de distintos modelos y proveedores de inferencia.
* Registrar métricas y eventos relevantes durante la ejecución.
* Supervisar el comportamiento térmico del hardware durante cargas intensivas.
* Mantener coherencia entre código, documentación técnica y decisiones arquitectónicas.
* Servir como plataforma experimental para estudiar arquitecturas RAG orientadas al desarrollo y mantenimiento de software.

El proyecto prioriza:

* calidad del contexto;
* estabilidad arquitectónica;
* mantenibilidad;
* observabilidad;
* trazabilidad;
* evolución incremental.

No se busca incorporar funcionalidades por anticipación, sino validar cada cambio antes de consolidarlo.

---

## 3. Principios de diseño

La evolución del proyecto se guía por los siguientes principios.

### Bajo acoplamiento

Cada componente mantiene responsabilidades claramente delimitadas y depende únicamente de la información necesaria para cumplir su función.

### Alta cohesión

Cada módulo debe concentrarse en una responsabilidad principal.

### Separación de responsabilidades

La adquisición del conocimiento, recuperación, construcción del contexto, inferencia, observabilidad y supervisión térmica se mantienen como responsabilidades independientes.

### Evolución incremental

Las nuevas capacidades se incorporan mediante cambios pequeños y controlados.

El enfoque general es:

```text
Caso real
    ↓
Reproducción mínima
    ↓
Cambio mínimo
    ↓
Prueba de regresión
    ↓
Validación
    ↓
Consolidación
```

### Sin cambios especulativos

No se incorporan mecanismos complejos únicamente porque puedan resultar útiles en el futuro.

Antes de introducir nuevas capas o componentes se busca obtener evidencia mediante pruebas y comportamiento real del sistema.

### Observabilidad

El comportamiento del pipeline debe poder analizarse mediante:

* registros cronológicos;
* métricas de tiempo;
* eventos;
* información de depuración;
* pruebas documentadas.

### Documentación como parte del desarrollo

Las decisiones arquitectónicas relevantes deben conservar su contexto y justificación mediante documentación y, cuando corresponda, mediante **Architecture Decision Records (ADR)**.

---

## 4. Arquitectura general

El sistema se distribuye entre dos entornos principales:

```text
                    EQUIPO FÍSICO

┌─────────────────────────┬─────────────────────────────┐
│         Windows         │         WSL2 Ubuntu         │
│                         │                             │
│ LibreHardwareMonitor    │ Pipeline RAG                │
│                         │                             │
│ export_temp_server.py   │ ingest.py                   │
│                         │ chunk.py                    │
│                         │ embed.py                    │
│                         │ symbols_extractor.py        │
│                         │ query.py                    │
│                         │ llm_backend.py              │
│                         │ logger.py                   │
│                         │ thermal_watchdog.py         │
└────────────┬────────────┴─────────────────────────────┘
             │
             │ HTTP + JSON
             ▼
      Supervisión térmica
```

Cada entorno mantiene responsabilidades diferenciadas.

---

## 5. Entorno Windows

El entorno Windows concentra los componentes relacionados con la adquisición de información del hardware.

### Responsabilidades principales

* acceso a los sensores físicos;
* ejecución de LibreHardwareMonitor;
* publicación de información térmica;
* comunicación con el entorno WSL2;
* suministro de datos para la supervisión térmica.

El flujo simplificado es:

```text
LibreHardwareMonitor
        │
        ▼
export_temp_server.py
        │
        ▼
HTTP + JSON
        │
        ▼
WSL2 / thermal_watchdog.py
```

El pipeline RAG no interactúa directamente con los sensores físicos.

La información térmica se obtiene mediante un servicio desacoplado que actúa como puente entre Windows y WSL2.

---

## 6. Entorno WSL2 Ubuntu

El entorno WSL2 concentra los componentes relacionados con el procesamiento del conocimiento y la ejecución del pipeline RAG.

Entre sus responsabilidades se encuentran:

* procesamiento documental;
* fragmentación de contenido;
* generación de embeddings;
* extracción de símbolos estructurados;
* recuperación semántica;
* construcción del contexto;
* coordinación del proceso de consulta;
* selección del backend de inferencia;
* registro de eventos y métricas;
* supervisión térmica.

Una representación simplificada es:

```text
Fuentes de conocimiento
        │
        ▼
Procesamiento / ingestión
        │
        ├───────────────────────┐
        ▼                       ▼
   Recuperación textual    Extracción de símbolos
        │                       │
        ▼                       ▼
  embeddings.jsonl       índice estructurado
        │                       │
        └───────────┬───────────┘
                    ▼
                 query.py
                    │
                    ▼
              llm_backend.py
                    │
            ┌───────┴────────┐
            ▼                ▼
          LOCAL            CLOUD
         Ollama         OpenRouter
                    │
                    ▼
                 Respuesta
```

Los componentes de observabilidad y supervisión permanecen desacoplados del flujo funcional principal.

---

## 7. Pipeline RAG

El pipeline está diseñado para separar claramente:

1. la recuperación del conocimiento;
2. la organización y construcción del contexto;
3. la inferencia.

El flujo general de una consulta puede representarse de la siguiente manera:

```text
Usuario
   │
   ▼
Recepción de la consulta
   │
   ▼
Generación del embedding
   │
   ▼
Recuperación de conocimiento
   │
   ├──────────────────────────┐
   │                          │
   ▼                          ▼
Búsqueda semántica      Información estructurada
   │                          │
   └──────────────┬───────────┘
                  ▼
       Construcción del contexto
                  │
                  ▼
       Construcción del prompt
                  │
                  ▼
           llm_backend.py
                  │
          ┌───────┴───────┐
          ▼               ▼
        LOCAL           CLOUD
       Ollama       OpenRouter
                  │
                  ▼
               Respuesta
```

La arquitectura permite que nuevas fuentes de conocimiento puedan incorporarse progresivamente sin acoplarlas directamente a un proveedor de inferencia.

---

## 8. Knowledge Sources y conocimiento estructurado

La arquitectura evoluciona hacia un modelo en el que diferentes tipos de conocimiento pueden constituir fuentes independientes.

Entre las capacidades desarrolladas se encuentra la extracción de información estructurada desde código C#.

El componente principal es:

```text
symbols_extractor.py
        │
        ▼
parsers/
        │
        └── csharp_parser.py
```

El parser C# utiliza un enfoque heurístico ligero en Python, sin incorporar dependencias externas ni utilizar un AST basado en Roslyn.

Su objetivo es extraer información estructurada de entidades como:

* `class`;
* `interface`;
* `struct`;
* `record`;
* `record class`;
* `record struct`;
* `enum`.

También permite obtener información sobre:

* namespace;
* modificadores;
* herencia;
* interfaces implementadas;
* métodos;
* parámetros;
* propiedades.

La salida mantiene un contrato estructurado destinado a preservar la información necesaria para su utilización posterior como fuente de conocimiento.

El desarrollo de este componente sigue una metodología estricta de validación mediante casos reproducibles y pruebas de regresión.

La versión candidata **v2.1.4** del parser superó la batería sintética de validación disponible antes de su consolidación.

---

## 9. Separación entre recuperación e inferencia

Uno de los principios fundamentales de la arquitectura consiste en desacoplar completamente la recuperación del conocimiento de la generación de respuestas.

La responsabilidad general de los componentes es:

```text
Fuentes de conocimiento
        │
        ▼
Recuperación y organización
        │
        ▼
Construcción del contexto
        │
        ▼
query.py
        │
        ▼
llm_backend.py
        │
        ├── LOCAL
        │      └── Ollama
        │
        └── CLOUD
               └── OpenRouter
```

Esta organización permite que:

* `query.py` no dependa directamente de un proveedor específico;
* la recuperación permanezca independiente del modelo utilizado;
* `llm_backend.py` no necesite conocer cómo fue construido el contexto;
* nuevos proveedores puedan incorporarse sin modificar el núcleo de recuperación.

Actualmente, la arquitectura contempla dos modalidades principales de inferencia:

* **LOCAL**, mediante Ollama;
* **CLOUD**, mediante OpenRouter.

---

## 10. Supervisión térmica

El proyecto incorpora un sistema independiente de supervisión térmica destinado a proteger el hardware durante la ejecución de cargas intensivas.

El flujo simplificado es:

```text
LibreHardwareMonitor
        │
        ▼
export_temp_server.py
        │
        ▼
HTTP + JSON
        │
        ▼
thermal_watchdog.py
        │
        ▼
Evaluación térmica
        │
        ├── Normal
        ├── Advertencia
        └── Crítico
                 │
                 ▼
       Protección preventiva
```

Entre sus funciones se encuentran:

* lectura periódica de temperatura;
* cálculo de promedio móvil;
* clasificación del estado térmico;
* registro de eventos;
* aplicación de límites configurados;
* detención preventiva de procesos cuando corresponde;
* recuperación del estado normal cuando las condiciones lo permiten.

La supervisión térmica permanece desacoplada del backend de inferencia.

---

## 11. Observabilidad del sistema

La arquitectura incorpora mecanismos de observabilidad destinados a analizar el comportamiento del pipeline sin introducir responsabilidades adicionales en los módulos funcionales.

El módulo principal es:

```text
logger.py
```

Entre la información registrada se encuentran eventos relacionados con las distintas etapas del pipeline.

También se contemplan métricas como:

* `EMBEDDING_TIME`;
* `SEARCH_TIME`;
* `LLM_TIME`;
* `PIPELINE_TIME`.

La observabilidad permite:

* diagnosticar incidencias;
* analizar el rendimiento;
* comparar ejecuciones;
* validar cambios;
* identificar cuellos de botella;
* conservar evidencia del comportamiento real del sistema.

La información de depuración y las métricas permanecen separadas de la lógica principal de recuperación e inferencia.

---

## 12. Componentes principales

| Componente                 | Responsabilidad principal                                                            |
| -------------------------- | ------------------------------------------------------------------------------------ |
| `ingest.py`                | Procesamiento e ingestión de conocimiento documental.                                |
| `chunk.py`                 | Fragmentación de contenido para su posterior procesamiento.                          |
| `embed.py`                 | Generación de embeddings.                                                            |
| `symbols_extractor.py`     | Coordinación de la extracción estructurada de símbolos.                              |
| `parsers/csharp_parser.py` | Parser heurístico de código C#.                                                      |
| `query.py`                 | Coordinación del proceso de consulta y construcción del contexto.                    |
| `llm_backend.py`           | Abstracción de los proveedores de inferencia.                                        |
| `config_loader.py`         | Carga centralizada de configuración.                                                 |
| `knowledge_filter.py`      | Aplicación de políticas y filtros relacionados con la construcción del conocimiento. |
| `logger.py`                | Registro de eventos, métricas y observabilidad.                                      |
| `thermal_watchdog.py`      | Supervisión térmica y protección preventiva.                                         |
| `export_temp_server.py`    | Publicación de información térmica desde Windows hacia WSL2.                         |

---

## 13. Organización del repositorio

La estructura general del repositorio separa:

* documentación;
* decisiones arquitectónicas;
* pruebas;
* código relacionado con Windows;
* código ejecutado en WSL2.

```text
Arquitectura_RAG_Termica/
│
├── README.md
├── LICENSE
├── ESTRUCTURA_DEL_PROYECTO.md
├── docs/
└── source/
```

La descripción detallada de la organización se encuentra en:

```text
ESTRUCTURA_DEL_PROYECTO.md
```

La documentación técnica y arquitectónica se encuentra en:

```text
docs/
```

El código fuente documentado y organizado por entorno se encuentra en:

```text
source/
```

---

## 14. Tecnologías utilizadas

| Área                      | Tecnología           |
| ------------------------- | -------------------- |
| Lenguaje principal        | Python               |
| Sistema anfitrión         | Windows 10           |
| Entorno de ejecución      | WSL2 Ubuntu          |
| Proyecto analizado        | .NET MAUI / C#       |
| Recuperación RAG          | Embeddings locales   |
| Modelo de embeddings      | `nomic-embed-text`   |
| Inferencia LOCAL          | Ollama               |
| Inferencia CLOUD          | OpenRouter           |
| Supervisión térmica       | LibreHardwareMonitor |
| Servicio de monitoreo     | Flask                |
| Comunicación Windows–WSL2 | HTTP + JSON          |
| Control de versiones      | Git / GitHub         |

---

## 15. Estado actual del proyecto

El proyecto se encuentra en una etapa de evolución incremental.

Entre las capacidades actualmente desarrolladas se encuentran:

* arquitectura RAG modular;
* recuperación semántica local;
* generación local de embeddings;
* separación entre recuperación e inferencia;
* backend LOCAL mediante Ollama;
* backend CLOUD mediante OpenRouter;
* construcción progresiva de mecanismos para enriquecer el contexto;
* extracción estructurada de símbolos desde código C#;
* contrato definido para la representación de símbolos;
* pruebas sintéticas de regresión para el parser C#;
* registro cronológico de eventos;
* métricas del pipeline;
* mecanismos de depuración;
* supervisión térmica desacoplada;
* protección preventiva frente a condiciones térmicas críticas;
* documentación técnica organizada;
* registro de decisiones arquitectónicas mediante ADR;
* conservación de evidencias históricas de pruebas.

El trabajo actual se orienta a consolidar los componentes desarrollados antes de continuar incorporando nuevas capas de complejidad.

---

## 16. Documentación

La documentación técnica del proyecto se encuentra organizada en documentos independientes.

| Documento                                | Contenido                                           |
| ---------------------------------------- | --------------------------------------------------- |
| `01_vision_general.md`                   | Contexto, motivación y objetivos del proyecto.      |
| `02_arquitectura_del_sistema.md`         | Arquitectura general y organización de componentes. |
| `03_pipeline_RAG.md`                     | Flujo del pipeline y construcción del contexto.     |
| `04_ollama_y_entorno.md`                 | Configuración del entorno y modelos utilizados.     |
| `05_supervision_y_proteccion_termica.md` | Supervisión térmica y mecanismos de protección.     |
| `06_pruebas_y_validacion.md`             | Estrategia y evidencias de validación.              |
| `07_mantenimiento_y_evolucion.md`        | Mantenimiento y evolución prevista.                 |
| `08_backend_hibrido.md`                  | Desacoplamiento entre recuperación e inferencia.    |
| `09_hoja_de_ruta_arquitectura.md`        | Evolución progresiva de la arquitectura.            |
| `docs/adr/`                              | Registro de decisiones arquitectónicas.             |
| `docs/pruebas/`                          | Evidencia histórica de pruebas realizadas.          |

La estructura detallada de estos documentos puede consultarse en:

```text
ESTRUCTURA_DEL_PROYECTO.md
```

---

## 17. Evolución prevista

La evolución del proyecto continuará mediante incrementos controlados.

El principio general será:

```text
Medir comportamiento real
        ↓
Identificar una limitación concreta
        ↓
Reproducir el problema
        ↓
Aplicar el cambio mínimo necesario
        ↓
Validar mediante pruebas
        ↓
Documentar y consolidar
```

Entre las posibles líneas futuras se encuentran:

* mejora de la calidad de recuperación;
* evaluación del ranking de resultados;
* enriquecimiento progresivo del contexto;
* incorporación controlada de nuevas Knowledge Sources;
* establecimiento de relaciones entre componentes;
* análisis de dependencias;
* incorporación de información temporal;
* evaluación comparativa de modelos;
* métricas de calidad del contexto;
* evolución progresiva hacia un asistente técnico especializado en el proyecto.

Estas capacidades deberán incorporarse únicamente cuando exista una necesidad concreta y evidencia de que aportan valor al sistema.

---

## 18. Filosofía del proyecto

Este proyecto no busca únicamente implementar un pipeline RAG funcional.

Su propósito es estudiar cómo construir una arquitectura capaz de evolucionar de manera:

* modular;
* documentada;
* observable;
* mantenible;
* trazable;
* incremental.

El objetivo central es mejorar progresivamente la forma en que el conocimiento de un proyecto de software puede ser:

```text
Adquirido
    ↓
Procesado
    ↓
Recuperado
    ↓
Organizado
    ↓
Integrado en contexto
    ↓
Utilizado por un modelo de lenguaje
```

La arquitectura debe permitir experimentar con estas etapas sin comprometer innecesariamente la estabilidad del sistema.

La documentación, las pruebas y las decisiones arquitectónicas forman parte del desarrollo y deben evolucionar de forma coordinada con la implementación.

---

## 19. Licencia

Este proyecto se distribuye bajo la licencia **MIT**.

Las herramientas, bibliotecas, modelos y servicios utilizados durante su desarrollo mantienen sus respectivas licencias y condiciones de uso.

---

## 20. Visión a largo plazo

La visión del proyecto es evolucionar desde un pipeline experimental de recuperación y construcción de contexto hacia un asistente técnico capaz de colaborar con el desarrollador durante el ciclo de vida del software.

Para ello, la arquitectura deberá avanzar progresivamente hacia una base de conocimiento capaz de mantener sincronizada información procedente de:

* documentación;
* código fuente;
* símbolos y estructuras del proyecto;
* decisiones arquitectónicas;
* relaciones entre componentes;
* restricciones conocidas;
* cambios relevantes en la evolución del sistema.

La incorporación de estas capacidades deberá preservar los principios fundamentales del proyecto:

> **medir antes de complejizar, desacoplar responsabilidades, validar cada cambio y mantener la coherencia entre implementación, pruebas, documentación y decisiones arquitectónicas.**

