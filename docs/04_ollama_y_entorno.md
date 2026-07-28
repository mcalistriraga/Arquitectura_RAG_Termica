# Entorno de Ejecución y Backends de Inferencia

## 1. Introducción

El proyecto utiliza un entorno de ejecución basado en **WSL2 Ubuntu**, donde se ejecutan los componentes principales del pipeline RAG y los modelos de inteligencia artificial.

La arquitectura ha sido diseñada para separar el procesamiento documental de la generación de respuestas mediante una capa de abstracción (`llm_backend.py`), permitiendo utilizar distintos proveedores de inferencia sin modificar el flujo principal de la aplicación.

Actualmente el proyecto soporta dos modalidades de inferencia:

- **Backend LOCAL**, mediante Ollama.
- **Backend CLOUD**, mediante OpenRouter.

Esta arquitectura híbrida permite ejecutar completamente el sistema en un entorno local cuando el hardware lo permite o utilizar modelos remotos cuando se requiere mayor capacidad de procesamiento.

---

# 2. Arquitectura del entorno

El entorno de ejecución está organizado en dos niveles principales: el sistema operativo anfitrión (Windows) y el entorno Linux proporcionado por WSL2.

```text
                    WINDOWS

               Hardware físico

                      │
                      ▼

                WSL2 Ubuntu

                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼

     Entorno Python             Ollama

        │
        ▼

   Pipeline RAG

        │
        ▼

     query.py

        │
        ▼

   llm_backend.py

        │
   ┌────┴─────┐
   ▼          ▼

Ollama   OpenRouter

   │          │
   └────┬─────┘
        ▼

 Respuesta final
```

El procesamiento documental y la lógica principal del pipeline se ejecutan en WSL2, mientras que la supervisión térmica utiliza servicios auxiliares que se comunican con Windows.

---

# 3. Sistema operativo

## WSL2 Ubuntu

El entorno Linux utilizado por el proyecto se ejecuta mediante:

```text
Windows Subsystem for Linux 2 (WSL2)
```

Dentro de este entorno se ejecutan los componentes principales del sistema.

Entre sus responsabilidades se encuentran:

- ejecución de los scripts Python;
- administración del entorno virtual;
- ejecución del pipeline RAG;
- comunicación con Ollama;
- acceso al backend cloud cuando se encuentra habilitado;
- gestión de los archivos generados durante la indexación documental.

Esta separación permite mantener el desarrollo de la aplicación en un entorno Linux sin perder acceso al hardware y a las herramientas disponibles en Windows.

---

# 4. Estructura del entorno

El proyecto se organiza en un directorio principal que contiene el código fuente, los archivos generados durante la indexación y el entorno virtual de Python.

En las pruebas realizadas se ha utilizado, entre otros, el directorio:

```text
/home/manuelc/rag_maui_docs_for_rag
```

Una estructura simplificada es la siguiente:

```text
rag_maui_docs_for_rag

├── scripts/
│
├── chunks/
│
├── docs/
│
├── embeddings.jsonl
│
├── symbols.jsonl
│
├── output_raw.jsonl
│
└── venv_rag/
```

La estructura puede evolucionar conforme se incorporen nuevos componentes al proyecto.

---

# 5. Entorno Python

El proyecto utiliza un entorno virtual independiente para aislar las dependencias del sistema.

Nombre del entorno:

```text
venv_rag
```

Activación:

```bash
source venv_rag/bin/activate
```

---

## Versión de Python

La implementación actual utiliza Python 3.12.x.

La versión exacta puede variar según el entorno de desarrollo, manteniéndose dentro de la serie 3.12.

---

## Bibliotecas utilizadas

Entre las dependencias empleadas por los componentes principales del proyecto se encuentran:

| Biblioteca | Propósito |
|-------------|-----------|
| requests | Comunicación HTTP con Ollama, OpenRouter y servicios auxiliares. |
| numpy | Operaciones sobre vectores y cálculo de similitud. |
| json | Lectura y escritura de archivos JSON y JSONL. |
| re | Procesamiento mediante expresiones regulares. |
| time | Control de tiempos y temporización de procesos. |
| os | Acceso a archivos y variables del sistema. |
| subprocess | Ejecución de procesos externos. |
| collections | Estructuras auxiliares utilizadas por el watchdog térmico. |

Dependiendo del componente ejecutado, pueden utilizarse bibliotecas adicionales.

---

# 6. Capa de abstracción del backend

## llm_backend.py

La comunicación con los modelos de lenguaje se encuentra centralizada en `llm_backend.py`.

Este componente actúa como una capa de abstracción entre el pipeline RAG y los distintos proveedores de inferencia disponibles.

Entre sus responsabilidades se encuentran:

- seleccionar el backend configurado;
- preparar la solicitud correspondiente;
- enviar la consulta al proveedor de inferencia;
- recibir la respuesta generada por el modelo;
- devolver un formato uniforme al resto del sistema.

Gracias a esta arquitectura, `query.py` permanece desacoplado de la implementación específica de cada backend.

```text
query.py

     │
     ▼

llm_backend.py

     │
 ┌───┴──────────┐
 ▼              ▼

LOCAL        CLOUD

(Ollama)   (OpenRouter)
```

Esta organización facilita la incorporación futura de nuevos proveedores sin modificar el flujo principal del pipeline.

---

# 7. Backend LOCAL

## Ollama

El backend local utiliza Ollama como servidor de modelos de inteligencia artificial.

Entre sus funciones principales se encuentran:

- cargar modelos LLM instalados localmente;
- generar embeddings;
- ejecutar inferencias;
- exponer una API HTTP accesible desde los scripts Python.

---

## Servicio

El servicio de Ollama se encuentra disponible, por defecto, mediante:

```text
http://localhost:11434
```

---

## API utilizadas

### Generación de texto

```text
POST /api/generate
```

Utilizada por `llm_backend.py` cuando el backend seleccionado es LOCAL.

---

### Generación de embeddings

```text
POST /api/embeddings
```

Utilizada por:

- `embed.py`;
- `query.py`;

para generar las representaciones vectoriales empleadas durante la recuperación semántica.

---

## Modelos locales utilizados

Actualmente la configuración contempla los siguientes modelos:

| Función | Modelo |
|----------|--------|
| Embeddings | `nomic-embed-text` |
| Depuración | `qwen2.5-coder:1.5b` |
| Arquitectura | `llama3.2:3b` |
| Documentación | `llama3.2:3b` |

La selección del modelo depende del modo de operación elegido por el usuario y de la configuración del backend.

# 8. Backend CLOUD

## OpenRouter

El backend cloud permite delegar la generación de respuestas a modelos de lenguaje disponibles a través de OpenRouter.

Su utilización resulta especialmente útil cuando el hardware local no dispone de la capacidad suficiente para ejecutar modelos de mayor tamaño o cuando se desea evaluar distintos modelos remotos manteniendo el mismo pipeline RAG.

La comunicación con OpenRouter se realiza exclusivamente mediante `llm_backend.py`, manteniendo desacoplado el resto de la aplicación.

---

## Autenticación

El acceso al servicio requiere una clave de API (API Key), que se carga desde el entorno de ejecución.

La gestión de las credenciales se mantiene separada del código fuente, evitando su incorporación al repositorio.

---

## Modelos remotos

El backend cloud permite utilizar diferentes modelos compatibles con OpenRouter.

La selección del modelo depende de la configuración activa en la sesión y puede modificarse sin alterar el funcionamiento del pipeline RAG.

---

# 9. Comunicación con los backends

El flujo general de una consulta es independiente del proveedor de inferencia.

```text
query.py

     │
     ▼

Preparación de la consulta

     │
     ▼

llm_backend.py

     │
 ┌───┴──────────┐
 ▼              ▼

LOCAL        CLOUD

Ollama     OpenRouter

     │
     ▼

Respuesta del modelo

     │
     ▼

query.py

     │
     ▼

Usuario
```

Esta arquitectura permite cambiar de backend sin modificar la lógica principal de `query.py`.

---

# 10. Ejecución del entorno

## Activar el entorno virtual

```bash
source venv_rag/bin/activate
```

---

## Verificar Ollama

Cuando se utilice el backend LOCAL, es posible comprobar los modelos instalados mediante:

```bash
ollama list
```

---

## Iniciar el servicio Ollama

Si el servicio no se encuentra en ejecución:

```bash
ollama serve
```

---

## Ejecutar una consulta

Con el entorno preparado:

```bash
python3 query.py
```

Durante el inicio de la aplicación, el usuario puede seleccionar el modo de operación y el backend configurado para la sesión.

---

# 11. Consideraciones de hardware

El proyecto fue diseñado considerando equipos con recursos limitados, donde la ejecución de modelos LLM puede representar una carga significativa para el procesador.

Entre las características del entorno utilizado durante el desarrollo se encuentran:

- ejecución principalmente sobre CPU;
- memoria limitada;
- ausencia de una GPU dedicada para aceleración de IA;
- necesidad de controlar la temperatura durante tareas intensivas.

Estas limitaciones motivaron varias decisiones de diseño, entre ellas:

- utilización de modelos relativamente ligeros para la ejecución local;
- separación entre recuperación documental e inferencia;
- incorporación de un backend cloud para ejecutar modelos remotos cuando resulte conveniente;
- implementación de un mecanismo independiente de supervisión térmica.

---

# 12. Integración con la supervisión térmica

La supervisión térmica forma parte de la arquitectura general del proyecto, aunque se ejecuta de manera independiente del pipeline principal.

Su funcionamiento puede resumirse de la siguiente forma:

```text
Windows

      │
      ▼

export_temp_server.py

      │
      ▼

thermal_watchdog.py

      │
      ▼

Monitoreo continuo

      │
      ▼

Acciones de protección
```

Cuando la temperatura supera los umbrales configurados, el watchdog puede registrar el evento y detener el proceso de consulta para proteger el equipo.

La comunicación entre Windows y WSL2 se realiza mediante un servicio HTTP basado en Flask.

---

# 13. Estado actual del entorno

Actualmente el entorno de ejecución permite:

- ejecutar el pipeline RAG sobre WSL2;
- generar embeddings mediante Ollama;
- utilizar inferencia local mediante Ollama;
- utilizar inferencia remota mediante OpenRouter;
- seleccionar distintos modelos según el modo de operación;
- registrar la actividad de las consultas;
- supervisar las condiciones térmicas del equipo mediante procesos desacoplados.

La arquitectura mantiene una separación clara entre el procesamiento documental, la inferencia y la supervisión del sistema.

---

# 14. Evolución prevista

Entre las posibles líneas de evolución del entorno se encuentran:

- incorporación de aceleración mediante GPU;
- soporte para nuevos proveedores de inferencia;
- gestión automática de modelos locales;
- optimización del consumo de recursos;
- incorporación de métricas de rendimiento;
- integración con herramientas de observabilidad y monitorización.

Estas funcionalidades representan posibles mejoras futuras y no forman parte de la implementación actual.

---

# 15. Resumen

La arquitectura de ejecución del proyecto combina:

```text
Windows
        │
        ▼
WSL2 Ubuntu
        │
        ▼
Python
        │
        ▼
Pipeline RAG
        │
        ▼
llm_backend.py
     ┌──┴──┐
     ▼     ▼
 Ollama  OpenRouter
```

Esta organización proporciona una plataforma experimental para el desarrollo y evaluación de soluciones RAG, permitiendo utilizar tanto recursos locales como servicios de inferencia remotos, manteniendo una arquitectura modular, extensible y coherente con el estado actual del proyecto.

