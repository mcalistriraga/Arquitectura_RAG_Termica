# Pipeline RAG Local

## 1. Introducción

El pipeline RAG (Retrieval Augmented Generation) implementado permite consultar información propia almacenada localmente mediante una arquitectura basada en:

* procesamiento documental,
* generación de embeddings,
* recuperación semántica,
* construcción de contexto,
* generación de respuestas mediante modelos LLM locales ejecutados con Ollama.

El objetivo principal es disponer de un asistente técnico local capaz de responder preguntas utilizando una base documental propia, evitando depender de servicios externos.

La implementación está orientada inicialmente al análisis del proyecto **MauiAppGestorMovil**, aunque la arquitectura permite incorporar otros conjuntos documentales.

---

# 2. Arquitectura general del Pipeline RAG

El flujo completo es:

```text
                 DOCUMENTOS LOCALES

                        |
                        v

                 ingest.py

          Lectura y clasificación
          de archivos del proyecto

                        |
                        v

              output_raw.jsonl

                        |
                        v

                 embed.py

          Generación de embeddings
          mediante nomic-embed-text

                        |
                        v

              embeddings.jsonl

                        |
                        v

                 query.py

          Consulta del usuario

                        |
                        v

          Embedding de la pregunta

                        |
                        v

              Búsqueda semántica

                        |
                        v

              Contexto recuperado

                        |
                        v

                 Ollama LLM

                        |
                        v

                   Respuesta
```

---

# 3. Componentes del Pipeline

## 3.1 ingest.py

### Objetivo

Realizar la extracción inicial de información desde los documentos fuente.

Su responsabilidad es leer los archivos del proyecto y generar una estructura intermedia que permita posteriormente crear embeddings.

---

## Ubicación de entrada

Actualmente:

```text
/home/manuelc/rag_maui_docs
```

---

## Extensiones procesadas

El proceso considera:

```text
.cs
.xaml
.md
.json
```

---

## Clasificación automática

Durante la ingestión cada archivo recibe una clasificación basada en su ubicación.

Ejemplo:

| Ruta detectada | Capa asignada |
|---|---|
| ViewModel | ViewModel |
| View o XAML | UI |
| Service o API | Service |
| Otros archivos | Model |

---

## Salida generada

Archivo:

```text
output_raw.jsonl
```

Ejemplo de estructura:

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

Es el componente encargado de transformar el contenido documental en representaciones vectoriales.

Utiliza el modelo:

```text
nomic-embed-text
```

ejecutado mediante:

```text
Ollama
```

---

## Flujo

```text
output_raw.jsonl

        |
        v

Lectura documento

        |
        v

Preparación del contexto

        |
        v

Ollama Embeddings API

        |
        v

Vector semántico

        |
        v

embeddings.jsonl
```

---

## Información almacenada

Cada registro conserva:

* archivo origen,
* capa arquitectónica,
* contenido original,
* embedding generado.

Ejemplo:

```json
{
 "file":"AgregarProducto.xaml",
 "layer":"UI",
 "content":"...",
 "embedding":[0.0123,0.0456,...]
}
```

---

# 5. Base vectorial documental

Actualmente la persistencia utiliza un archivo JSONL:

```text
embeddings.jsonl
```

Cada línea representa un documento con su vector asociado.

Ventajas de este enfoque:

* simplicidad,
* fácil inspección,
* portable,
* adecuado para pruebas locales.

Para el tamaño actual del proyecto no se requiere todavía una base vectorial externa.

---

# 6. Motor de consultas

## 6.1 query.py

Es el componente principal de interacción con el usuario.

Responsabilidades:

* recibir preguntas,
* generar embeddings de consulta,
* realizar búsqueda semántica,
* construir contexto,
* seleccionar modelo LLM,
* generar respuesta.

---

# 7. Modos de operación IA

Al iniciar `query.py` el usuario selecciona el modo de trabajo:

```text
=== MODO IA LOCAL ===

1. DEPURACIÓN
2. ARQUITECTURA
3. DOCUMENTACIÓN
```

---

## Modo 1 - DEPURACIÓN

Modelo:

```text
qwen2.5-coder:1.5b
```

Orientado a:

* errores de compilación,
* análisis C#,
* problemas MAUI,
* revisión de código.

Funciones especiales:

* detección de códigos `CSxxxx`,
* extracción del archivo involucrado,
* búsqueda enfocada.

---

## Modo 2 - ARQUITECTURA

Modelo:

```text
llama3.2:3b
```

Orientado a:

* análisis general del sistema,
* decisiones arquitectónicas,
* relaciones entre componentes.

---

## Modo 3 - DOCUMENTACIÓN

Modelo:

```text
llama3.2:3b
```

Orientado a:

* explicación funcional,
* generación de documentación,
* descripción de componentes.

---

# 8. Recuperación semántica

El proceso utiliza similitud coseno:

```text
Embedding pregunta

        +

Embeddings documentos


        |

        v


Ranking por similitud

        |

        v

TOP_K resultados
```

Configuración actual:

```python
TOP_K = 1
SIM_THRESHOLD = 0.25
```

---

# 9. Integración con Ollama

La arquitectura utiliza Ollama como servidor local de modelos.

Endpoint:

```text
http://localhost:11434
```

---

## Modelos utilizados

| Función | Modelo |
|-|-|
| Embeddings | nomic-embed-text |
| Código / Debug | qwen2.5-coder:1.5b |
| Arquitectura | llama3.2:3b |
| Documentación | llama3.2:3b |

---

# 10. Control térmico integrado

El pipeline incorpora supervisión térmica mediante:

```text
logger.py
```

y:

```text
thermal_watchdog.py
```

---

Durante la ejecución:

```text
query.py

   |
   v

logger.py

   |
   v

Consulta temperatura CPU

   |
   v

Control de seguridad
```

---

Se registran eventos como:

```text
SESSION_START
MODE_SELECTED
INPUT_RECEIVED
EMBEDDING_START
SEARCH_START
LLM_START
LLM_DONE
```

---

# 11. Flujo completo de una consulta

Ejemplo:

```text
Usuario pregunta:

"¿Por qué falla la navegación hacia SeleccionarCategoriaProducto?"
```

---

Proceso:

```text
Pregunta usuario

        |
        v

Generar embedding

        |
        v

Buscar documentos similares

        |
        v

Recuperar contexto MAUI

        |
        v

Construir prompt

        |
        v

Enviar a Ollama

        |
        v

Respuesta técnica
```

---

# 12. Características actuales

El pipeline implementado permite:

* ejecutar RAG completamente local,
* trabajar sin conexión externa,
* consultar documentación propia,
* analizar código fuente,
* seleccionar modelos según objetivo,
* supervisar consumo térmico,
* detener procesos ante condiciones críticas.

---

# 13. Evolución futura

Posibles mejoras:

* incorporar una base vectorial dedicada,
* aumentar la estrategia de chunking,
* incorporar búsqueda híbrida (texto + vector),
* agregar memoria conversacional,
* integrar análisis automático de arquitectura,
* incorporar métricas de rendimiento del pipeline.

---

# 14. Estado actual

Actualmente el pipeline RAG se encuentra operativo con:

* generación de embeddings funcional,
* consultas mediante Ollama,
* selección de modos IA,
* recuperación documental,
* integración con supervisión térmica.

La implementación representa una arquitectura RAG experimental completa ejecutándose localmente sobre hardware limitado.
