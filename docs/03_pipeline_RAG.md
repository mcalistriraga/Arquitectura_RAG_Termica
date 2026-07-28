# Pipeline RAG

## 1. Introducción

El pipeline **RAG (Retrieval-Augmented Generation)** implementado en este proyecto constituye el núcleo funcional del asistente técnico desarrollado en **Arquitectura_RAG_Termica**.

Su propósito consiste en recuperar conocimiento desde una base documental local, construir un contexto de trabajo y delegar la generación de respuestas a un backend de inferencia desacoplado.

Actualmente el pipeline implementa las siguientes etapas principales:

- ingestión documental;
- extracción de información estructural;
- generación de embeddings;
- recuperación semántica;
- construcción del contexto;
- construcción del prompt;
- inferencia mediante un modelo de lenguaje (LLM);
- observabilidad del pipeline.

La arquitectura fue diseñada para ejecutarse sobre hardware de recursos limitados, separando claramente el procesamiento documental, la recuperación del conocimiento, la inferencia y la supervisión térmica.

Actualmente el proyecto soporta dos modalidades de inferencia:

- **Backend LOCAL**, utilizando Ollama.
- **Backend CLOUD**, utilizando OpenRouter.

Esta separación permite mantener exactamente el mismo pipeline RAG independientemente del proveedor encargado de generar la respuesta.

Es importante distinguir entre dos conceptos:

- **el asistente técnico**, implementado por Arquitectura_RAG_Termica;
- **la base de conocimiento activa**, formada por la documentación y el código fuente del proyecto que se desea analizar.

En el estado actual del desarrollo, dicha base de conocimiento corresponde a una aplicación desarrollada con .NET MAUI, utilizada como caso de uso para validar el funcionamiento del asistente.

---

# 2. Arquitectura general del pipeline

El flujo principal implementado actualmente es el siguiente:

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

      Construcción del contexto

                     │
                     ▼

      Construcción del prompt

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

La supervisión térmica continúa ejecutándose de forma independiente mediante procesos auxiliares, sin formar parte del flujo funcional del pipeline.

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

La arquitectura del asistente no depende de una ubicación específica; únicamente requiere una colección documental compatible con el proceso de ingestión.

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
| ViewModel | ViewModel |
| View / XAML | UI |
| Service / API | Service |
| Otros archivos | Model |

Esta clasificación constituye un apoyo para la organización documental y no representa una validación formal de la arquitectura del proyecto analizado.

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

Cada registro generado conserva la información necesaria para la recuperación posterior, incluyendo:

- archivo de origen;
- clasificación documental;
- contenido textual;
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
| `embeddings.jsonl` | Almacena los embeddings documentales y el contenido recuperado por el pipeline RAG. |
| `symbols.jsonl` | Almacena información estructural extraída del código mediante `symbol_extractor.py`. |

Cada archivo mantiene una función específica dentro del proceso de recuperación de información.

Actualmente no se utiliza una base vectorial dedicada (por ejemplo, FAISS, Chroma o Milvus), ya que el tamaño del conjunto documental permite trabajar eficientemente mediante archivos locales.

Esta decisión simplifica el despliegue, facilita la inspección manual de los datos generados y permite comprender con mayor facilidad el funcionamiento interno del pipeline durante las etapas de desarrollo y validación.

---

# 6. Motor de consultas

## 6.1 query.py

`query.py` constituye el punto de entrada para las consultas realizadas por el usuario.

Entre sus responsabilidades principales se encuentran:

- recibir la consulta del usuario;
- gestionar la sesión de trabajo;
- generar el embedding de la pregunta;
- recuperar los documentos más similares;
- recuperar información estructural cuando corresponda;
- construir el contexto que será enviado al modelo de lenguaje;
- construir el prompt final;
- seleccionar el modo de operación;
- delegar la generación de la respuesta al backend LLM configurado;
- registrar la ejecución mediante `logger.py`.

La comunicación con el modelo de lenguaje no se realiza directamente desde `query.py`, sino a través de la capa de abstracción implementada en `llm_backend.py`, lo que permite utilizar distintos proveedores de inferencia sin modificar el flujo principal del pipeline.

En la versión actual, el contenido recuperado desde `embeddings.jsonl` vuelve a incorporarse explícitamente al contexto enviado al modelo de lenguaje, permitiendo que la recuperación semántica participe activamente en la generación de respuestas.

# 8. Recuperación semántica

Durante una consulta, `query.py` genera el embedding asociado a la pregunta del usuario y lo compara con los embeddings previamente almacenados en `embeddings.jsonl`.

El proceso implementado puede resumirse de la siguiente forma:

```text
Pregunta del usuario

        │
        ▼

Embedding de la consulta

        │
        ▼

Comparación mediante similitud coseno

        │
        ▼

embeddings.jsonl

        │
        ▼

Selección de los mejores resultados

        │
        ▼

Construcción del contexto enviado al LLM
```

La implementación actual utiliza similitud coseno para comparar los vectores.

La configuración vigente del código incluye:

```python
TOP_K = 1
SIM_THRESHOLD = 0.25
```

Estos parámetros determinan el número máximo de fragmentos recuperados y el umbral mínimo de similitud aceptado.

A diferencia de versiones anteriores del proyecto, los fragmentos recuperados ya no se utilizan únicamente para fines de depuración. Actualmente forman parte del contexto enviado al modelo de lenguaje, permitiendo que las respuestas se fundamenten en el contenido de la base de conocimiento local.

Durante el desarrollo puede habilitarse una bandera de depuración (`DEBUG_CHUNKS`) que muestra por consola y registra en `query_log.txt` los fragmentos recuperados, facilitando la validación del proceso de búsqueda semántica sin afectar el funcionamiento normal del pipeline.

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

Los modelos configurados actualmente son:

| Función | Modelo |
|----------|--------|
| Embeddings | `nomic-embed-text` |
| Depuración | `qwen2.5-coder:1.5b` |
| Arquitectura | `llama3.2:3b` |
| Documentación | `llama3.2:3b` |

---

## Backend CLOUD

El backend cloud utiliza OpenRouter como proveedor de inferencia remota.

La selección del backend se realiza desde la configuración de la sesión, manteniendo exactamente el mismo pipeline de recuperación documental.

De esta forma, independientemente del proveedor utilizado para la inferencia, la recuperación del conocimiento continúa realizándose localmente.

---

# 10. Registro y observabilidad

El pipeline incorpora mecanismos de observabilidad desacoplados mediante `logger.py`.

Cada consulta genera una sesión independiente de registro en:

```text
query_log.txt
```

Durante la ejecución se registran, entre otros, los siguientes eventos:

```text
INPUT_RECEIVED
EMBEDDING_START
EMBEDDING_OK
SEARCH_START
SEARCH_DONE
LLM_START
LLM_DONE
ANSWER_PRINTED
```

Además de la secuencia cronológica de eventos, el sistema calcula automáticamente métricas de rendimiento como:

- EMBEDDING_TIME
- SEARCH_TIME
- LLM_TIME
- PIPELINE_TIME

`logger.py` incorpora también una función genérica `log_debug()` destinada exclusivamente al desarrollo y diagnóstico.

Esta función permite registrar información adicional —como los fragmentos recuperados por la búsqueda semántica— sin modificar el flujo principal del pipeline ni la lógica funcional de `query.py`.

---

# 11. Supervisión térmica

El pipeline incorpora un mecanismo independiente de supervisión térmica implementado mediante `thermal_watchdog.py`.

Este componente consulta periódicamente la temperatura del procesador utilizando la información publicada por `export_temp_server.py`.

Cuando se alcanzan determinados umbrales configurados, el watchdog puede ejecutar acciones preventivas, incluyendo la finalización del proceso de consulta para proteger el hardware frente a condiciones de sobretemperatura.

Al encontrarse completamente desacoplado del pipeline RAG, este mecanismo puede evolucionar independientemente del resto del sistema.

---

# 12. Flujo general de una consulta

El siguiente esquema resume el procesamiento realizado durante una consulta.

```text
Usuario

   │
   ▼

Pregunta

   │
   ▼

Embedding de la consulta

   │
   ▼

Recuperación semántica

   │
   ▼

Construcción del contexto

   │
   ▼

Selección del backend

   │
   ▼

Inferencia del LLM

   │
   ▼

Respuesta

   │
   ▼

Registro de métricas
```

Este flujo permanece invariable independientemente del backend de inferencia utilizado.

---

# 13. Capacidades implementadas

En su estado actual, el pipeline permite:

- procesar documentación técnica local;
- generar embeddings mediante `nomic-embed-text`;
- realizar recuperación semántica sobre documentos indexados;
- incorporar al contexto los fragmentos recuperados mediante RAG;
- complementar dicho contexto con información arquitectónica procedente de `symbols.jsonl`;
- utilizar distintos modos especializados de operación;
- seleccionar entre backend local y backend cloud;
- registrar automáticamente cada consulta;
- calcular métricas del pipeline;
- registrar información adicional de depuración mediante `log_debug()`;
- supervisar continuamente las condiciones térmicas del sistema mediante procesos independientes.

---

# 14. Evolución prevista

Entre las principales líneas de evolución del proyecto se encuentran:

- incorporación de una base vectorial especializada;
- optimización de las estrategias de fragmentación (chunking);
- incorporación de recuperación híbrida (texto + vectores);
- ampliación del soporte para nuevos modelos LLM;
- incorporación de memoria conversacional;
- mejora de las métricas de observabilidad;
- automatización del proceso de construcción de bases de conocimiento;
- soporte para múltiples proyectos mediante bases documentales intercambiables.

Estas funcionalidades representan posibles evoluciones del proyecto y no forman parte de la implementación actual.

---

# 15. Estado actual

El pipeline RAG implementado constituye actualmente el núcleo operativo del asistente técnico.

Dispone de:

- ingestión documental;
- generación de embeddings;
- recuperación semántica;
- incorporación efectiva del contexto recuperado al prompt enviado al LLM;
- extracción de símbolos arquitectónicos;
- selección de modos especializados;
- abstracción del backend de inferencia;
- soporte para ejecución local y cloud;
- observabilidad mediante `logger.py`;
- registro opcional de información de depuración;
- supervisión térmica completamente desacoplada.

La arquitectura continúa evolucionando de forma incremental, manteniendo como principio fundamental la separación de responsabilidades y la coherencia entre la documentación técnica y el comportamiento real del código fuente.
