# Estructura del Proyecto

Este documento describe la organización general del repositorio **Arquitectura_RAG_Termica** y el propósito de los principales archivos y directorios que lo componen.

La estructura del proyecto separa la documentación general, la documentación técnica, las pruebas de validación y los archivos auxiliares con el objetivo de facilitar el mantenimiento, la evolución de la arquitectura y la consulta de la información.

---

# Organización del repositorio

```text
Arquitectura_RAG_Termica
│
├── README.md
│   Documento principal del proyecto.
│   Presenta la visión general, los objetivos, la arquitectura,
│   los componentes principales y el estado actual del sistema.
│
├── LICENSE
│   Licencia de distribución del proyecto.
│
├── ESTRUCTURA_DEL_PROYECTO.md
│   Descripción de la organización del repositorio y de la
│   documentación disponible.
│
├── docs/
│   │
│   ├── 01_vision_general.md
│   │      Contexto, motivación y objetivos del proyecto.
│   │
│   ├── 02_arquitectura_del_sistema.md
│   │      Arquitectura general del sistema, organización de los
│   │      componentes y comunicación entre los distintos entornos
│   │      de ejecución.
│   │
│   ├── 03_pipeline_RAG.md
│   │      Flujo del pipeline RAG, recuperación semántica,
│   │      construcción del contexto y organización del proceso
│   │      de consulta.
│   │
│   ├── 04_ollama_y_entorno.md
│   │      Configuración del entorno de ejecución, instalación
│   │      de Ollama, modelos utilizados y organización del
│   │      entorno RAG.
│   │
│   ├── 05_supervision_y_proteccion_termica.md
│   │      Arquitectura de supervisión térmica, comunicación
│   │      Windows–WSL2, watchdog y mecanismos de protección.
│   │
│   ├── 06_pruebas_y_validacion.md
│   │      Estrategia de pruebas, validación funcional de los
│   │      componentes y resultados obtenidos durante el desarrollo.
│   │
│   ├── 07_mantenimiento_y_evolucion.md
│   │      Organización del mantenimiento del sistema, operación,
│   │      copias de seguridad y líneas de evolución previstas.
│   │
│   └── 08_backend_hibrido.md
│          Arquitectura del backend de inferencia, abstracción
│          mediante llm_backend.py y soporte para proveedores
│          LOCAL y CLOUD.
│
└── tests/
    │
    ├── README.md
    │      Descripción de las pruebas realizadas durante el
    │      desarrollo del proyecto.
    │
    ├── 2026-07-20_prueba01_backend_local_qwen2.5-coder-1.5b.md
    │      Validación inicial del backend LOCAL utilizando
    │      Ollama y el modelo qwen2.5-coder:1.5b.
    │
    ├── 2026-07-20_prueba02_backend_local_qwen2.5_abort_termico.md
    │      Validación de la protección térmica durante la
    │      ejecución del backend LOCAL.
    │
    ├── 2026-07-21_prueba03_backend_hibrido_local_cloud.md
    │      Validación de la arquitectura híbrida mediante la
    │      utilización de los backends LOCAL y CLOUD.
    │
    └── 2026-07-28_prueba04_integracion_final.md
           Validación integrada de la versión actual del sistema,
           incluyendo el pipeline RAG, la capa de inferencia,
           el registro de eventos y la supervisión térmica.
```
---

# Organización de la documentación

La documentación ha sido organizada de forma progresiva para facilitar la comprensión del proyecto.

Se recomienda seguir el siguiente orden de lectura:

```text
README.md
      │
      ▼
Visión general del proyecto
      │
      ▼
Arquitectura del sistema
      │
      ▼
Pipeline RAG
      │
      ▼
Entorno de ejecución e inferencia
      │
      ▼
Supervisión térmica
      │
      ▼
Pruebas y validación
      │
      ▼
Mantenimiento y evolución
      │
      ▼
Backend de inferencia
```

Este recorrido permite comprender primero los objetivos generales del proyecto y, posteriormente, profundizar en cada uno de sus componentes, decisiones de diseño y evolución arquitectónica.

---

# Carpeta de pruebas

El repositorio incorpora una carpeta específica para conservar evidencia de las pruebas realizadas durante el desarrollo.

```text
pruebas/
│
├── README.md
│      Descripción de la organización y alcance de las pruebas.
│
├── 2026-07-20_prueba01_backend_local_qwen2.5-coder-1.5b.md
│      Validación inicial del backend LOCAL utilizando
│      qwen2.5-coder:1.5b.
│
├── 2026-07-20_prueba02_backend_local_qwen2.5_abort_termico.md
│      Validación del mecanismo de protección térmica
│      durante la ejecución del backend LOCAL.
│
├── 2026-07-21_prueba03_backend_hibrido_local_cloud.md
│      Validación de la arquitectura híbrida mediante
│      la selección de los backends LOCAL y CLOUD.
│
└── 2026-07-28_prueba04_integracion_final.md
       Prueba de integración del pipeline RAG,
       supervisión térmica, registro de eventos
       y capa de abstracción del backend de inferencia.
```

Los documentos de esta carpeta constituyen evidencia histórica del proceso de desarrollo y complementan la información resumida en `docs/06_pruebas_y_validacion.md`.

---

# Alcance de este documento

Este documento describe únicamente la organización del repositorio y de la documentación.

La descripción detallada de la arquitectura, del pipeline RAG, de la supervisión térmica, del backend de inferencia y de los distintos componentes del sistema se encuentra en el directorio `docs/`, mientras que `README.md` constituye la presentación general del proyecto.

---

# Objetivo

La documentación del proyecto ha sido estructurada para favorecer:

- una navegación sencilla por el repositorio;
- la separación entre información general, documentación técnica y evidencias de pruebas;
- el mantenimiento de la arquitectura a largo plazo;
- la incorporación progresiva de nuevas funcionalidades sin perder coherencia documental;
- la trazabilidad entre la implementación, las pruebas realizadas y la documentación técnica correspondiente.
