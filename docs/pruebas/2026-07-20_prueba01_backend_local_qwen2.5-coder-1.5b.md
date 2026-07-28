# Prueba de ejecución RAG local - qwen2.5-coder:1.5b

**Fecha de ejecución:** 2026-07-20  
**Tipo de prueba:** Validación extremo a extremo del pipeline RAG local  
**Proyecto:** Arquitectura RAG local con supervisión térmica  

---

## Objetivo de la prueba

Validar el funcionamiento completo del pipeline RAG local utilizando un modelo LLM ligero, con la finalidad de comprobar que el sistema puede completar una consulta desde la entrada del usuario hasta la generación de una respuesta.

Esta prueba busca separar los problemas asociados al pipeline RAG de las limitaciones de hardware durante la ejecución de modelos de mayor tamaño.

---

## Configuración utilizada

### Modelo LLM
* **Modelo:** `qwen2.5-coder:1.5b`
* **Modelo de embeddings:** `nomic-embed-text`

### Recursos cargados
| Recurso | Cantidad |
| :--- | :--- |
| Embeddings disponibles | 466 |
| Símbolos arquitectónicos | 80 |

---

## Flujo validado

La ejecución comprobó las siguientes etapas:

```text
Usuario
   |
   v
query.py
   |
   +--> Generación embedding de consulta
   |
   +--> Búsqueda semántica
   |
   +--> Construcción de contexto
   |
   +--> Consulta al modelo LLM mediante Ollama
   |
   v
Respuesta generada
```

---

## Resultados obtenidos

### Tiempos de ejecución

| Etapa | Tiempo |
| :--- | :--- |
| Generación embedding consulta | 4.15 s |
| Búsqueda semántica | 0.05 s |
| Inferencia LLM | 49.15 s |

### Resultado de la prueba
✅ **Prueba completada correctamente**

El sistema logró:
* Cargar la base de conocimiento vectorial.
* Cargar la información arquitectónica desde `symbols.jsonl`.
* Generar el embedding de la consulta.
* Ejecutar la búsqueda semántica.
* Ejecutar la inferencia del modelo LLM mediante Ollama.
* Generar una respuesta al usuario.

---

## Observaciones técnicas

La prueba confirma que el pipeline RAG puede ejecutarse correctamente con un modelo LLM ligero en el hardware disponible.

El análisis de tiempos muestra que:
* La generación de embeddings tiene un costo reducido.
* La búsqueda semántica es prácticamente inmediata.
* La mayor carga computacional corresponde a la inferencia del modelo LLM.

**Distribución aproximada del tiempo:**
* **Embedding:** ~4 s
* **Search:** ~0.05 s
* **LLM:** ~49 s

---

## Análisis del cuello de botella

La medición obtenida permite identificar el comportamiento de cada etapa:

```text
Pipeline RAG

Carga de datos
      |
      v
Generación embedding
      |
      |  ~4 segundos
      v
Búsqueda semántica
      |
      |  ~0.05 segundos
      v
Inferencia LLM
      |
      |  ~49 segundos
      v
Respuesta final
```

La etapa dominante corresponde al procesamiento del modelo generativo LLM. Esto indica que la limitación observada **no** está relacionada con:
* Carga de embeddings
* Búsqueda vectorial
* Procesamiento Python
* Estructura general del pipeline RAG

El principal factor limitante corresponde a la capacidad de inferencia del modelo utilizado sobre el hardware disponible.

---

## Conclusión

Esta ejecución establece una línea base funcional del sistema RAG local. La arquitectura actual permite:
* Utilizar modelos locales pequeños en hardware limitado.
* Validar el pipeline completo.
* Medir el impacto de diferentes modelos LLM.
* Comparar futuras alternativas de ejecución local o remota.

La prueba confirma que el desacoplamiento entre `query.py` y `thermal_watchdog.py` permite evaluar el rendimiento del pipeline sin mezclar la lógica de consulta con la protección térmica del hardware.

El cuello de botella identificado corresponde principalmente a la etapa de generación de respuesta del modelo LLM.

---

## Próximas evaluaciones

Como continuación de esta prueba se pueden realizar comparaciones con:
* Modelos LLM locales de mayor tamaño.
* Optimizaciones de configuración.
* Ejecución híbrida local/nube.
* Selección dinámica del modelo según disponibilidad de recursos.
* Evaluación del impacto de modelos especializados en código fuente.

---

## Registro de prueba

| Parámetro | Estado |
| :--- | :--- |
| **Estado final** | **FINALIZADA CORRECTAMENTE** |
| **Pipeline RAG** | OK |
| **Modelo local** | OK |
| **Respuesta generada** | OK |
| **Limitación principal** | Tiempo de inferencia LLM |
