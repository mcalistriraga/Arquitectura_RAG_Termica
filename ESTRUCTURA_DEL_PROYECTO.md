# Estructura del Proyecto

Este documento describe la organización general del repositorio **Arquitectura_RAG_Termica**.

La estructura separa el código fuente, la documentación técnica y los archivos principales del proyecto, facilitando el mantenimiento y la evolución de la arquitectura.

```text
Arquitectura_RAG_Termica
│
├── README.md
│   Documento principal del proyecto.
│   Descripción general, objetivos, características y enlaces
│   hacia la documentación técnica.
│
├── LICENSE
│   Licencia de distribución del proyecto.
│
├── ESTRUCTURA_DEL_PROYECTO.md
│   Mapa general de organización del repositorio.
│
└── docs
    │
    ├── 01_vision_general.md
    │      Propósito, motivación y objetivos del proyecto.
    │
    ├── 02_arquitectura_del_sistema.md
    │      Arquitectura híbrida Windows + WSL2,
    │      componentes principales y comunicación entre entornos.
    │
    ├── 03_pipeline_RAG.md
    │      Flujo documental, ingestión, generación de embeddings,
    │      recuperación semántica y generación de respuestas.
    │
    ├── 04_ollama_y_entorno.md
    │      Configuración del entorno de inteligencia artificial local,
    │      modelos utilizados y ejecución mediante Ollama.
    │
    ├── 05_supervision_y_proteccion_termica.md
    │      Sistema de monitoreo térmico, watchdog,
    │      detección de condiciones críticas y protección automática.
    │
    ├── 06_pruebas_y_validacion.md
    │      Evidencias de pruebas realizadas,
    │      validación de componentes y resultados obtenidos.
    │
    └── 07_mantenimiento_y_evolucion.md
           Mantenimiento del sistema, organización,
           mejoras futuras y posibles líneas de evolución.
```

---

## Organización conceptual

La documentación sigue un recorrido progresivo:

```text
Visión del proyecto
        |
        v
Arquitectura general
        |
        v
Pipeline RAG
        |
        v
Entorno Ollama e IA local
        |
        v
Supervisión y protección térmica
        |
        v
Pruebas realizadas
        |
        v
Mantenimiento y evolución
```

Esta organización permite comprender el sistema desde una perspectiva general hasta los detalles operativos y de evolución futura.

