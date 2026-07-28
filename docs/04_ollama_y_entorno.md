# Entorno de Ejecución y Backends de Inferencia

## 1. Introducción

El proyecto utiliza un entorno de ejecución basado en **WSL2 Ubuntu**, donde se ejecutan los componentes principales del pipeline RAG y los modelos de inteligencia artificial.

La arquitectura ha sido diseñada para separar claramente la **recuperación del conocimiento**, la **generación de respuestas**, la **observabilidad** y la **supervisión térmica**, permitiendo que cada componente evolucione de forma independiente.

Actualmente la recuperación documental permanece completamente local, mientras que la inferencia puede realizarse mediante distintos proveedores utilizando una capa de abstracción implementada en `llm_backend.py`.

Actualmente el proyecto soporta dos modalidades de inferencia:

- **Backend LOCAL**, mediante Ollama.
- **Backend CLOUD**, mediante OpenRouter.

Esta arquitectura híbrida permite ejecutar completamente el sistema en un entorno local cuando el hardware lo permite o utilizar modelos remotos cuando se requiere mayor capacidad de procesamiento, sin modificar el flujo principal del pipeline.

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
        ├─────────────── Recuperación local
        │
        ▼
 Construcción del contexto
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

El procesamiento documental, la recuperación semántica y la construcción del contexto se ejecutan íntegramente en WSL2.

La supervisión térmica utiliza servicios auxiliares ejecutados en Windows y se comunica con WSL2 mediante HTTP.

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

Durante el desarrollo se ha utilizado, entre otros, el directorio:

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

La estructura puede evolucionar conforme se incorporen nuevos componentes al proyecto o nuevas bases de conocimiento.

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
| numpy | Operaciones sobre vectores y cálculo de similitud coseno. |
| json | Lectura y escritura de archivos JSON y JSONL. |
| re | Procesamiento mediante expresiones regulares. |
| time | Medición de tiempos y temporización. |
| os | Acceso a archivos y variables del sistema. |
| subprocess | Ejecución de procesos externos. |
| collections | Estructuras auxiliares utilizadas por el watchdog térmico. |

Dependiendo del componente ejecutado, pueden utilizarse bibliotecas adicionales.

---

# 6. Capa de abstracción del backend

## llm_backend.py

La comunicación con los modelos de lenguaje se encuentra centralizada en `llm_backend.py`.

Este componente constituye una capa de abstracción cuya única responsabilidad es realizar la inferencia mediante el proveedor configurado.

Entre sus responsabilidades se encuentran:

- seleccionar el backend configurado;
- preparar la solicitud de inferencia;
- enviar la consulta al proveedor correspondiente;
- recibir la respuesta generada por el modelo;
- devolver un formato uniforme a `query.py`.

La recuperación del conocimiento, la construcción del contexto y la selección de documentos relevantes permanecen completamente bajo la responsabilidad de `query.py`.

```text
query.py

     │
     ▼

Contexto construido

     │
     ▼

llm_backend.py

     │
 ┌───┴──────────┐
 ▼              ▼

LOCAL        CLOUD

(Ollama)   (OpenRouter)
```

Esta organización facilita la incorporación futura de nuevos proveedores sin modificar el resto del pipeline.

---

# 7. Backend LOCAL

## Ollama

El backend local utiliza Ollama como servidor de modelos de inteligencia artificial.

Entre sus funciones principales se encuentran:

- cargar modelos LLM instalados localmente;
- generar embeddings;
- ejecutar inferencias;
- exponer una API HTTP accesible desde los scripts Python.

# 8. Backend CLOUD

## OpenRouter

El backend cloud permite delegar la generación de respuestas a modelos de lenguaje disponibles a través de OpenRouter.

Su utilización resulta especialmente útil cuando el hardware local no dispone de la capacidad suficiente para ejecutar modelos de mayor tamaño o cuando se desea evaluar distintos modelos remotos manteniendo el mismo pipeline RAG.

La comunicación con OpenRouter se realiza exclusivamente mediante `llm_backend.py`, manteniendo completamente desacoplado el resto del sistema.

La recuperación del conocimiento continúa realizándose localmente en `query.py`, por lo que el backend cloud únicamente recibe el contexto ya construido y genera la respuesta correspondiente.

---

## Autenticación

El acceso al servicio requiere una clave de API (API Key), que se carga desde el entorno de ejecución mediante variables de entorno.

La gestión de las credenciales permanece separada del código fuente, evitando su incorporación al repositorio.

Esta organización facilita la sustitución del proveedor de inferencia sin modificar el resto del pipeline.

---

## Modelos remotos

El backend cloud permite utilizar distintos modelos compatibles con OpenRouter.

La selección del modelo depende de la configuración activa en la sesión y puede modificarse sin alterar el funcionamiento general del pipeline RAG.

Gracias a la capa de abstracción implementada en `llm_backend.py`, el resto del sistema permanece independiente del proveedor de inferencia utilizado.

---

# 9. Comunicación con los backends

El flujo general de una consulta es independiente del proveedor de inferencia.

```text
query.py

     │
     ▼

Recuperación del conocimiento

     │
     ▼

Construcción del contexto

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

Esta arquitectura permite cambiar de backend sin modificar la lógica principal de `query.py`, manteniendo completamente desacopladas la recuperación del conocimiento y la inferencia.

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

Durante el inicio de la aplicación, el usuario selecciona el modo de operación.

La configuración de la sesión determina automáticamente:

- modo de trabajo;
- backend de inferencia;
- modelo de lenguaje;
- modelo de embeddings.

Una vez inicializada la sesión, `query.py` coordina el resto del pipeline hasta obtener la respuesta del modelo.

---

# 11. Observabilidad

La observabilidad del pipeline se encuentra centralizada en `logger.py`.

Este componente registra una sesión independiente para cada consulta realizada mediante `query.py`.

Entre la información registrada se encuentra:

- fecha y hora de ejecución;
- backend utilizado;
- modelo seleccionado;
- modelo de embeddings;
- modo de operación;
- pregunta realizada;
- secuencia cronológica de eventos del pipeline.

Además, calcula automáticamente las métricas:

- EMBEDDING_TIME;
- SEARCH_TIME;
- LLM_TIME;
- PIPELINE_TIME.

Durante el desarrollo también puede registrarse información adicional mediante la función genérica:

```text
log_debug()
```

Esta función permite almacenar información de diagnóstico —como los fragmentos recuperados durante la búsqueda semántica— sin modificar el comportamiento funcional del pipeline.

---

# 12. Integración con la supervisión térmica

La supervisión térmica forma parte de la arquitectura general del proyecto, aunque se ejecuta completamente desacoplada del pipeline principal.

Su funcionamiento puede resumirse de la siguiente forma:

```text
Windows

      │
      ▼

LibreHardwareMonitor

      │
      ▼

export_temp_server.py

      │
      ▼

HTTP / JSON

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

Cuando la temperatura supera los umbrales configurados, `thermal_watchdog.py` puede registrar el evento y finalizar preventivamente la ejecución de `query.py` para proteger el hardware.

La comunicación entre Windows y WSL2 se realiza mediante un servicio HTTP ligero implementado con Flask.

---

# 13. Estado actual del entorno

Actualmente el entorno de ejecución permite:

- ejecutar el pipeline RAG sobre WSL2;
- generar embeddings mediante Ollama;
- recuperar conocimiento desde `embeddings.jsonl`;
- complementar el contexto mediante `symbols.jsonl`;
- incorporar el contexto recuperado al prompt enviado al LLM;
- utilizar inferencia local mediante Ollama;
- utilizar inferencia remota mediante OpenRouter;
- seleccionar distintos modelos según el modo de operación;
- registrar automáticamente la actividad de cada consulta;
- calcular métricas del pipeline;
- registrar información adicional de depuración mediante `log_debug()`;
- supervisar las condiciones térmicas del equipo mediante procesos desacoplados.

La arquitectura mantiene una separación clara entre recuperación del conocimiento, inferencia, observabilidad y supervisión térmica.

---

# 14. Evolución prevista

Entre las posibles líneas de evolución del entorno se encuentran:

- incorporación de aceleración mediante GPU;
- soporte para nuevos proveedores de inferencia;
- gestión automática de modelos locales;
- optimización del consumo de recursos;
- ampliación de las capacidades de observabilidad;
- automatización de la construcción de nuevas bases de conocimiento;
- soporte para múltiples proyectos mediante repositorios documentales intercambiables.

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
Recuperación local
        │
        ▼
Construcción del contexto
        │
        ▼
llm_backend.py
     ┌──┴──┐
     ▼     ▼
 Ollama  OpenRouter
```

Esta organización proporciona una plataforma experimental para el desarrollo y evaluación de asistentes técnicos basados en RAG, permitiendo mantener la recuperación del conocimiento bajo control local mientras la inferencia puede realizarse tanto mediante recursos locales como servicios remotos.

La separación entre recuperación, inferencia, observabilidad y supervisión térmica constituye uno de los principales principios arquitectónicos alcanzados por el proyecto y facilita su evolución hacia futuras versiones del asistente técnico.
