# Estructura del Proyecto

Este documento describe la organización general del repositorio **Arquitectura_RAG_Termica** y el propósito de los principales documentos que lo componen.

La estructura del proyecto separa la documentación general, la documentación técnica y los archivos auxiliares con el objetivo de facilitar el mantenimiento, la evolución de la arquitectura y la consulta de la información.

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
└── docs/
    │
    ├── 01_vision_general.md
    │      Contexto, motivación y objetivos del proyecto.
    │
    ├── 02_arquitectura_del_sistema.md
    │      Arquitectura general del sistema, organización de los
    │      componentes y comunicación entre los distintos entornos
    │      de ejecución.
    │
    ├── 03_pipeline_RAG.md
    │      Flujo del pipeline RAG, recuperación semántica,
    │      construcción del contexto y organización del proceso
    │      de consulta.
    │
    ├── 04_ollama_y_entorno.md
    │      Configuración del entorno de inferencia, modelos
    │      utilizados y organización del entorno de ejecución.
    │
    ├── 05_supervision_y_proteccion_termica.md
    │      Supervisión térmica, monitoreo del hardware,
    │      watchdog y mecanismos de protección preventiva.
    │
    ├── 06_pruebas_y_validacion.md
    │      Pruebas realizadas, validación funcional y resultados
    │      obtenidos durante el desarrollo.
    │
    └── 07_mantenimiento_y_evolucion.md
           Organización del mantenimiento del proyecto,
           evolución de la arquitectura y posibles líneas
           de desarrollo futuro.
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
```

Este recorrido permite comprender primero los objetivos generales del proyecto y, posteriormente, profundizar en cada uno de sus componentes y decisiones de diseño.

---

# Alcance de este documento

Este documento describe únicamente la organización del repositorio y de la documentación.

La descripción detallada de la arquitectura, del pipeline RAG y de los distintos componentes del sistema se encuentra en el directorio `docs/`, mientras que `README.md` constituye la principal presentación del proyecto.

---

# Objetivo

La documentación del proyecto ha sido estructurada para favorecer:

- una navegación sencilla por el repositorio;
- la separación entre información general y documentación técnica;
- el mantenimiento de la arquitectura a largo plazo;
- la incorporación progresiva de nuevas funcionalidades sin perder coherencia documental.
