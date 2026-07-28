# Pipeline RAG

## 1. Introducción

El pipeline **RAG (Retrieval-Augmented Generation)** implementado en este proyecto permite consultar información técnica almacenada localmente mediante una secuencia de procesamiento compuesta por:

- ingestión documental,
- extracción de símbolos arquitectónicos,
- generación de embeddings,
- recuperación semántica,
- construcción del contexto de consulta,
- inferencia mediante un modelo de lenguaje (LLM).

La arquitectura fue diseñada para ejecutarse principalmente sobre hardware de recursos limitados, separando el procesamiento documental de la inferencia y permitiendo seleccionar distintos backends LLM mediante una capa de abstracción.

Actualmente el proyecto soporta dos modalidades de inferencia:

- **Backend LOCAL**, utilizando Ollama.
- **Backend CLOUD**, utilizando OpenRouter.

Esta separación permite mantener el mismo flujo RAG independientemente del proveedor encargado de generar la respuesta.

---

# 2. Arquitectura general del pipeline

El flujo principal implementado es el siguiente:

```text
                 DOCUMENTOS

                     │
                     ▼

                 ingest.py

     Lectura y clasificación documental

                     │
                     ▼

              output_raw.jsonl

                     │
                     ├──────────────┐
                     ▼              ▼

               embed.py      symbol_extractor.py

                     │              │
                     ▼              ▼

          embeddings.jsonl   symbols.jsonl

                     │
                     ▼

                 query.py

                     │
                     ▼

        Embedding de la consulta

                     │
                     ▼

       Recuperación semántica (RAG)

                     │
                     ▼

      Construcción del contexto de trabajo

                     │
                     ▼

              llm_backend.py

          ┌────────────┴────────────┐
          ▼                         ▼

   Backend LOCAL             Backend CLOUD
      Ollama                  OpenRouter

          └────────────┬────────────┘
                       ▼

                 Respuesta final
```

La supervisión térmica se ejecuta de forma independiente mediante procesos auxiliares, sin formar parte del flujo principal de procesamiento del pipeline.

---

# 3. Componentes del pipeline

## 3.1 ingest.py

### Objetivo

`ingest.py` constituye la primera etapa del pipeline y tiene como responsabilidad leer los documentos de origen, clasificarlos y generar una representación estructurada que posteriormente será utilizada para crear embeddings.

El archivo generado sirve como punto de partida para el resto del proceso de indexación documental.

---

## Ubicación de entrada

La versión actual trabaja con un directorio documental definido durante la configuración del entorno.

En las pruebas realizadas se ha utilizado, entre otros, el directorio:

```text
/home/manuelc/rag_maui_docs
```

La ubicación puede modificarse según las necesidades del proyecto.

---

## Tipos de archivos procesados

Actualmente el proceso contempla, entre otros, documentos con extensiones como:

```text
.cs
.xaml
.md
.json
```

La lista exacta de extensiones depende de la configuración implementada en el script.

---

## Clasificación documental

Durante la ingestión cada archivo recibe información descriptiva que posteriormente facilita su recuperación.

Dependiendo de la ubicación o del tipo de archivo, pueden identificarse componentes como:

| Ubicación detectada | Clasificación utilizada |
|---------------------|-------------------------|
| ViewModel           | ViewModel               |
| View / XAML         | UI                      |
| Service / API       | Service                 |
| Otros archivos      | Model                   |

Esta clasificación constituye un apoyo para la organización documental y no representa una validación formal de la arquitectura del proyecto.

---

## Salida generada

Como resultado del proceso se genera el archivo:

```text
output_raw.jsonl
```

Cada línea contiene un registro independiente con información del documento procesado.

Ejemplo simplificado:

```json
{
  "file": "GestionDeProductosViewModel.cs",
  "layer": "ViewModel",
  "content": "..."
}
```

---

# 4. Generación de embeddings

## 4.1 embed.py

`embed.py` transforma el contenido textual de cada documento en una representación vectorial que posteriormente será utilizada durante la recuperación semántica.

En la implementación actual se emplea el modelo de embeddings:

```text
nomic-embed-text
```

ejecutado mediante Ollama.

---

## Flujo de procesamiento

```text
output_raw.jsonl

        │
        ▼

Lectura del documento

        │
        ▼

Solicitud del embedding

        │
        ▼

Modelo nomic-embed-text

        │
        ▼

Vector semántico

        │
        ▼

embeddings.jsonl
```

---

## Información almacenada

Cada registro generado conserva información necesaria para la recuperación posterior, incluyendo:

- archivo de origen,
- clasificación documental,
- contenido textual,
- embedding correspondiente.

Ejemplo simplificado:

```json
{
  "file": "AgregarProducto.xaml",
  "layer": "UI",
  "content": "...",
  "embedding": [0.0123, 0.0456, ...]
}
```

---

# 5. Índices documentales

La implementación actual utiliza archivos JSONL como mecanismo de persistencia de la información procesada.

Los principales índices son:

| Archivo | Propósito |
|----------|-----------|
| `embeddings.jsonl` | Almacena los embeddings documentales. |
| `symbols.jsonl` | Almacena información estructurada extraída del código mediante `symbol_extractor.py`. |

Cada archivo mantiene una función específica dentro del proceso de recuperación de información.

Actualmente no se utiliza una base vectorial dedicada (por ejemplo, FAISS, Chroma o Milvus), ya que el tamaño del conjunto documental permite trabajar eficientemente mediante archivos locales.

Esta decisión simplifica el despliegue y facilita la inspección manual de los datos generados durante las pruebas.

---

# 6. Motor de consultas

## 6.1 query.py

`query.py` constituye el punto de entrada para las consultas del usuario.

Entre sus responsabilidades principales se encuentran:

- recibir la consulta del usuario;
- generar el embedding de la pregunta;
- recuperar los documentos más similares;
- preparar la información necesaria para la inferencia;
- seleccionar el modo de operación;
- delegar la generación de la respuesta al backend LLM configurado;
- registrar la ejecución mediante `logger.py`.

La comunicación con el modelo de lenguaje no se realiza directamente desde `query.py`, sino a través de la capa de abstracción implementada en `llm_backend.py`, lo que permite utilizar distintos proveedores de inferencia sin modificar el flujo principal del pipeline.

---
# 7. Modos de operación

Al iniciar `query.py`, el usuario selecciona el modo de trabajo que determina el modelo y el tipo de asistencia esperada.

Ejemplo del menú:

```text
=== MODO IA ===

1. DEPURACIÓN
2. ARQUITECTURA
3. DOCUMENTACIÓN
```

Cada modo configura automáticamente el modelo LLM y el prompt base correspondiente.

---

## Modo 1 — DEPURACIÓN

Modelo configurado actualmente:

```text
qwen2.5-coder:1.5b
```

Orientado principalmente a:

- análisis de errores de compilación;
- revisión de código C#;
- resolución de problemas relacionados con .NET MAUI;
- asistencia durante tareas de desarrollo.

Entre las funcionalidades implementadas se incluyen mecanismos para identificar códigos de error de compilación y realizar búsquedas documentales más específicas cuando corresponde.

---

## Modo 2 — ARQUITECTURA

Modelo configurado actualmente:

```text
llama3.2:3b
```

Orientado al análisis de:

- arquitectura del sistema;
- relaciones entre componentes;
- organización del proyecto;
- estructura del código.

---

## Modo 3 — DOCUMENTACIÓN

Modelo configurado actualmente:

```text
llama3.2:3b
```

Orientado principalmente a:

- explicación del funcionamiento del proyecto;
- generación y revisión de documentación técnica;
- descripción de componentes y procesos.

---

# 8. Recuperación semántica

Durante una consulta, el sistema genera el embedding asociado a la pregunta y lo compara con los embeddings almacenados.

El proceso puede resumirse como:

```text
Pregunta del usuario

        │
        ▼

Embedding de la consulta

        │
        ▼

Comparación con

embeddings.jsonl

        │
        ▼

Cálculo de similitud

        │
        ▼

Selección de resultados
```

La implementación actual utiliza similitud coseno para comparar los vectores.

La configuración observada en el código incluye:

```python
TOP_K = 1
SIM_THRESHOLD = 0.25
```

Estos parámetros determinan el número máximo de resultados recuperados y el umbral mínimo de similitud aceptado.

> **Nota:** La recuperación documental forma parte del pipeline implementado. El modo exacto en que dicha información recuperada participa en la construcción final del prompt continúa en evaluación y se documentará con mayor detalle cuando esa integración sea revisada específicamente.

---

# 9. Backends de inferencia

La generación de respuestas se realiza mediante la capa de abstracción implementada en `llm_backend.py`.

Actualmente existen dos backends disponibles.

## Backend LOCAL

Utiliza Ollama como servidor de inferencia local.

Endpoint habitual:

```text
http://localhost:11434
```

Los modelos utilizados actualmente son:

| Función | Modelo |
|----------|--------|
| Embeddings | `nomic-embed-text` |
| Depuración | `qwen2.5-coder:1.5b` |
| Arquitectura | `llama3.2:3b` |
| Documentación | `llama3.2:3b` |

---

## Backend CLOUD

El backend cloud utiliza OpenRouter como proveedor de inferencia remota.

La selección del backend se realiza desde la configuración de la sesión, manteniendo el mismo flujo general de procesamiento del pipeline.

Gracias a esta abstracción, el resto del sistema permanece independiente del proveedor utilizado para generar la respuesta.

---

# 10. Registro y supervisión térmica

El pipeline incorpora mecanismos auxiliares para registrar la ejecución de las consultas y supervisar el estado térmico del equipo.

Estos componentes funcionan de manera desacoplada respecto al procesamiento principal.

## logger.py

Registra información relevante de cada consulta, incluyendo eventos como:

```text
SESSION_START
MODE_SELECTED
INPUT_RECEIVED
EMBEDDING_START
EMBEDDING_OK
SEARCH_START
SEARCH_DONE
LLM_START
LLM_DONE
SESSION_END
```

Estos registros facilitan el seguimiento del funcionamiento del sistema y el análisis posterior de incidencias.

---

## thermal_watchdog.py

Supervisa periódicamente la temperatura del procesador utilizando la información proporcionada por `export_temp_server.py`.

Cuando se alcanzan determinados umbrales configurados, el watchdog puede ejecutar acciones de protección, incluyendo la finalización del proceso de consulta para evitar condiciones de sobretemperatura.

La descripción detallada de este mecanismo se presenta en el documento dedicado a la supervisión térmica.

---

# 11. Flujo general de una consulta

El siguiente esquema resume el procesamiento realizado durante una consulta.

```text
Usuario

   │
   ▼

Pregunta

   │
   ▼

Generación del embedding

   │
   ▼

Recuperación semántica

   │
   ▼

Preparación del contexto

   │
   ▼

Selección del backend

   │
   ▼

Inferencia del LLM

   │
   ▼

Respuesta
```

Este flujo representa la secuencia general implementada por el sistema, independientemente del backend seleccionado.

---

# 12. Capacidades implementadas

En su estado actual, el pipeline permite:

- procesar documentación técnica local;
- generar embeddings mediante `nomic-embed-text`;
- realizar recuperación semántica sobre los documentos indexados;
- utilizar distintos modos de operación especializados;
- seleccionar entre backend local y backend cloud;
- registrar la ejecución de cada consulta;
- supervisar las condiciones térmicas del sistema mediante procesos independientes.

---

# 13. Evolución prevista

Entre las posibles líneas de evolución del proyecto se encuentran:

- incorporación de una base vectorial especializada;
- optimización de las estrategias de fragmentación (chunking);
- incorporación de recuperación híbrida (texto + vectores);
- ampliación del soporte para nuevos modelos LLM;
- incorporación de memoria conversacional;
- métricas de rendimiento del pipeline;
- mejoras en la integración del contexto recuperado durante la generación de respuestas.

Las funcionalidades anteriores representan posibles evoluciones del proyecto y no forman parte de la implementación actual.

---

# 14. Estado actual

El pipeline RAG implementado proporciona una plataforma experimental para el análisis de documentación técnica y código fuente mediante modelos de lenguaje.

Actualmente dispone de:

- ingestión documental;
- generación de embeddings;
- recuperación semántica;
- extracción de símbolos arquitectónicos;
- selección de modos especializados;
- abstracción del backend de inferencia;
- soporte para ejecución local y cloud;
- registro de consultas;
- supervisión térmica desacoplada.

La arquitectura continúa evolucionando de forma incremental, priorizando la coherencia entre la documentación y el comportamiento real del código fuente.

