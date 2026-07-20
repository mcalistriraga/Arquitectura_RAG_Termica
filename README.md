# Arquitectura RAG Local con Supervisión Térmica

## Descripción

Este proyecto implementa una arquitectura experimental para ejecutar modelos de lenguaje locales (**LLM**) mediante **RAG (Retrieval Augmented Generation)**, incorporando mecanismos de supervisión térmica y protección automática para operar de forma segura en hardware con recursos limitados.

La propuesta integra:

* procesamiento documental local,
* generación de embeddings,
* recuperación semántica de información,
* modelos LLM ejecutados localmente mediante Ollama,
* monitoreo del hardware,
* protección automática ante condiciones térmicas críticas.

El objetivo principal es explorar cómo construir una solución de inteligencia artificial local manteniendo control sobre los datos, los modelos y los recursos del equipo.

---

# Características principales

## Inteligencia artificial local

* Ejecución de modelos LLM sin depender de servicios externos.
* Generación de embeddings mediante modelos locales.
* Consultas sobre una base documental propia.
* Recuperación semántica de información relevante.

---

## Arquitectura RAG

El flujo principal es:

```text
Documentos
    |
    v
Procesamiento e ingestión
    |
    v
Generación de embeddings
    |
    v
Base vectorial local
    |
    v
Consulta usuario
    |
    v
Recuperación de contexto
    |
    v
Modelo LLM local
    |
    v
Respuesta
```

---

## Supervisión térmica

Debido a las limitaciones del hardware utilizado, se incorporó una capa de protección:

```text
LibreHardwareMonitor
        |
        v
export_temp_server.py
        |
        v
thermal_watchdog.py
        |
        v
Protección de procesos RAG
```

Funciones:

* lectura de temperatura del CPU,
* monitoreo continuo,
* promedio móvil,
* detección de condiciones críticas,
* registro de eventos,
* detención preventiva de procesos.

---

# Arquitectura general

El sistema utiliza una arquitectura híbrida:

```text
                 EQUIPO FÍSICO

                      |
          +-----------+-----------+
          |                       |
          v                       v


      WINDOWS                  WSL2 UBUNTU

LibreHardwareMonitor              Ollama
          |                       |
          v                       v

export_temp_server.py        Modelos LLM
          |
          |
      HTTP JSON
          |
          v

thermal_watchdog.py

          |
          v

      query.py

          |
          v

       RAG LOCAL
```

---

# Entornos utilizados

## Windows

Responsabilidades:

* acceso al hardware,
* lectura de sensores,
* publicación de temperatura.

Componentes:

* LibreHardwareMonitor.
* export_temp_server.py.

Ubicación:

```text
E:\Developer\Tools\LibreHardwareMonitor\python
```

---

## WSL2 Ubuntu

Responsabilidades:

* ejecución de inteligencia artificial,
* procesamiento RAG,
* supervisión térmica.

Componentes:

* Ollama.
* Scripts Python.
* Thermal Watchdog.

Ubicación:

```text
/home/manuelc/rag_maui_docs_for_rag/scripts
```

---

# Tecnologías principales

| Área                | Tecnología           |
| ------------------- | -------------------- |
| Sistema IA          | WSL2 Ubuntu          |
| Sistema hardware    | Windows              |
| LLM                 | Ollama               |
| Modelo principal    | llama3.2:3b          |
| Modelo código       | qwen2.5-coder:1.5b   |
| Embeddings          | nomic-embed-text     |
| Lenguaje            | Python               |
| API monitoreo       | Flask                |
| Hardware monitoring | LibreHardwareMonitor |
| Arquitectura IA     | RAG                  |

---

# Componentes principales

| Componente            | Función                             |
| --------------------- | ----------------------------------- |
| ingest.py             | Lectura y estructuración documental |
| embed.py              | Generación de embeddings            |
| query.py              | Motor de consulta RAG               |
| logger.py             | Registro de ejecución y diagnóstico |
| thermal_watchdog.py   | Supervisión térmica                 |
| export_temp_server.py | API térmica Windows                 |

---

# Documentación

La documentación completa se encuentra en:

```text
docs/
```

Documentos disponibles:

| Documento                                                                             | Descripción                      |
| ------------------------------------------------------------------------------------- | -------------------------------- |
| [01_vision_general.md](docs/01_vision_general.md)                                     | Objetivo y contexto del proyecto |
| [02_arquitectura_del_sistema.md](docs/02_arquitectura_del_sistema.md)                 | Diseño general de la solución    |
| [03_pipeline_RAG.md](docs/03_pipeline_RAG.md)                                         | Flujo de procesamiento RAG       |
| [04_ollama_y_entorno.md](docs/04_ollama_y_entorno.md)                                 | Modelos y entorno local          |
| [05_supervision_y_proteccion_termica.md](docs/05_supervision_y_proteccion_termica.md) | Protección térmica               |
| [06_pruebas_y_validacion.md](docs/06_pruebas_y_validacion.md)                         | Pruebas realizadas               |
| [07_mantenimiento_y_evolucion.md](docs/07_mantenimiento_y_evolucion.md)               | Mantenimiento y mejoras futuras  |

---

# Estado actual

Actualmente el sistema permite:

✅ Ejecutar modelos LLM localmente.
✅ Consultar información documental mediante RAG.
✅ Generar embeddings locales.
✅ Supervisar temperatura del CPU.
✅ Registrar eventos térmicos.
✅ Proteger procesos ante sobretemperatura.

---

# Motivación

Este proyecto nace como una experiencia práctica de integración entre:

* inteligencia artificial local,
* administración de sistemas,
* automatización,
* monitoreo de hardware.

El objetivo no es únicamente obtener respuestas mediante IA, sino construir una arquitectura controlada, observable y adaptable para escenarios donde los recursos computacionales son limitados.

---

# Posibles evoluciones

Entre las mejoras futuras consideradas:

* supervisión avanzada de CPU y memoria,
* selección dinámica de modelos,
* panel de monitoreo,
* métricas de rendimiento,
* automatización del ciclo completo RAG.

---

# Licencia

Este proyecto se distribuye bajo licencia MIT.

El código desarrollado en este repositorio está disponible para uso,
modificación y distribución conforme a los términos de dicha licencia.

Los modelos de inteligencia artificial, herramientas externas y librerías
utilizadas mantienen sus propias licencias:
- Ollama
- llama3.2:3b
- qwen2.5-coder
- nomic-embed-text
- LibreHardwareMonitor
- dependencias Python

