# Ollama y Entorno de Ejecución Local

## 1. Introducción

El proyecto utiliza un entorno de inteligencia artificial completamente local basado en **WSL2 Ubuntu + Ollama**, permitiendo ejecutar modelos de lenguaje y modelos de embeddings directamente en el equipo.

Esta arquitectura evita depender de servicios externos y mantiene:

* control de los datos,
* privacidad de la información,
* independencia de conexión,
* capacidad de experimentación con modelos locales.

El entorno está diseñado para funcionar en hardware limitado, utilizando modelos ligeros y mecanismos de control térmico.

---

# 2. Arquitectura del entorno IA

El entorno de ejecución está compuesto por:

```text
                 WINDOWS

              Hardware físico
                    |
                    |
                    v

              WSL2 Ubuntu

                    |
        +-----------+-----------+
        |                       |
        v                       v

      Python                 Ollama

        |                       |
        |                       |
        v                       v

     Pipeline RAG          Modelos IA

        |
        |
        v

     query.py
```

---

# 3. Sistema operativo

## WSL2 Ubuntu

El entorno Linux utilizado para inteligencia artificial se ejecuta mediante:

```text
Windows Subsystem for Linux 2
```

Responsabilidades:

* ejecución de scripts Python,
* administración del entorno virtual,
* ejecución del pipeline RAG,
* comunicación con Ollama.

---

# 4. Ubicación del proyecto

El entorno principal del RAG se encuentra en:

```text
/home/manuelc/rag_maui_docs_for_rag
```

Estructura principal:

```text
rag_maui_docs_for_rag

├── scripts
│
├── embeddings.jsonl
│
├── symbols.jsonl
│
├── documentos
│
└── venv_rag
```

---

# 5. Entorno Python

El proyecto utiliza un entorno virtual independiente:

```text
venv_rag
```

Activación:

```bash
source venv_rag/bin/activate
```

---

## Versión utilizada

Python:

```text
Python 3.12.x
```

---

## Librerías principales

El entorno incluye:

| Librería | Uso |
|-|-|
| requests | comunicación HTTP con Ollama y servicios externos |
| numpy | cálculo de similitud vectorial |
| json | manejo de archivos JSONL |
| re | detección de patrones y errores |
| time | control de tiempos y retardos |

---

# 6. Ollama

## Descripción

Ollama funciona como servidor local de modelos de inteligencia artificial.

Responsabilidades:

* cargar modelos LLM,
* ejecutar inferencias,
* generar embeddings,
* exponer una API HTTP local.

---

## Servicio Ollama

Endpoint principal:

```text
http://localhost:11434
```

---

## API utilizadas

### Generación de texto

```text
POST /api/generate
```

Utilizada por:

```text
query.py
```

para enviar preguntas al modelo LLM.

---

### Generación de embeddings

```text
POST /api/embeddings
```

Utilizada por:

```text
embed.py
query.py
```

para crear representaciones vectoriales.

---

# 7. Modelos instalados

La arquitectura utiliza modelos especializados según la tarea.

---

## nomic-embed-text

Uso:

```text
Generación de embeddings
```

Responsabilidad:

Transformar documentos y consultas en vectores semánticos.

Utilizado por:

```text
embed.py
query.py
```

---

## qwen2.5-coder:1.5b

Uso:

```text
Modo DEPURACIÓN
```

Orientado a:

* análisis de código,
* errores C#,
* problemas MAUI,
* propuestas de corrección.

---

## llama3.2:3b

Uso:

```text
Modo ARQUITECTURA
Modo DOCUMENTACIÓN
```

Orientado a:

* análisis conceptual,
* explicación de sistemas,
* generación documental.

---

# 8. Comunicación con Ollama

El flujo de una consulta es:

```text
query.py

    |
    |
    v

API Ollama

    |
    |
    v

Modelo seleccionado

    |
    |
    v

Respuesta generada
```

---

# 9. Ejecución del entorno

## Verificar Ollama

Ejemplo:

```bash
ollama list
```

Debe mostrar los modelos disponibles.

---

## Ejecutar Ollama

El servicio debe estar activo:

```bash
ollama serve
```

---

## Ejecutar consulta RAG

Dentro del entorno virtual:

```bash
python3 query.py
```

---

# 10. Consideraciones de hardware

El entorno fue diseñado considerando las limitaciones del equipo utilizado.

Características relevantes:

* ejecución únicamente con CPU,
* memoria limitada,
* ausencia de GPU dedicada para IA,
* necesidad de controlar temperatura durante cargas prolongadas.

Por esta razón:

* se utilizan modelos pequeños,
* se controla la carga durante generación de embeddings,
* se incorpora supervisión térmica externa.

---

# 11. Integración con la arquitectura térmica

Aunque Ollama no controla directamente el hardware, su carga puede aumentar el consumo del procesador.

La relación es:

```text
Ollama

   |
   v

Carga CPU

   |
   v

Temperatura

   |
   v

thermal_watchdog.py
```

El sistema térmico funciona como una capa externa de protección.

---

# 12. Estado actual del entorno

Actualmente el entorno permite:

* ejecutar modelos LLM locales,
* generar embeddings,
* realizar consultas RAG,
* cambiar modelos según necesidad,
* operar sin conexión externa,
* integrarse con mecanismos de protección térmica.

---

# 13. Posibles mejoras futuras

La evolución del entorno puede incluir:

* incorporación de GPU NVIDIA,
* modelos de mayor tamaño,
* cuantización avanzada,
* administración automática de modelos,
* métricas de rendimiento,
* integración con herramientas de observabilidad.

---

# 14. Resumen

La combinación:

```text
WSL2
 +
Python
 +
Ollama
 +
Modelos locales
 +
Pipeline RAG
```

proporciona una plataforma experimental completa para desarrollar soluciones de inteligencia artificial local manteniendo control sobre datos, modelos y recursos del equipo.
