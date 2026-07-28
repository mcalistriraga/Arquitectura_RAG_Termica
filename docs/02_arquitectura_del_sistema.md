# Arquitectura del Sistema

## 1. Introducción

La arquitectura de **Arquitectura_RAG_Termica** ha evolucionado desde un sistema orientado exclusivamente a la ejecución local de modelos de lenguaje hacia una arquitectura híbrida, modular y desacoplada.

El objetivo principal es separar claramente las distintas responsabilidades del sistema para facilitar su mantenimiento, su evolución y la incorporación de nuevos componentes sin afectar al funcionamiento del pipeline principal.

Actualmente la arquitectura se organiza en dos entornos complementarios:

- **Windows**, responsable del acceso al hardware físico y de la publicación de la información térmica.
- **WSL2 Ubuntu**, responsable de la ejecución del pipeline RAG, la recuperación del conocimiento, la inferencia mediante modelos de lenguaje y la supervisión del sistema.

Uno de los cambios arquitectónicos más importantes consiste en la separación entre la **recuperación del conocimiento** y la **inferencia**, permitiendo utilizar distintos proveedores de modelos de lenguaje sin modificar el núcleo del pipeline RAG.

---

# 2. Arquitectura general

La arquitectura actual puede representarse mediante el siguiente esquema:

```text
                         EQUIPO FÍSICO

                 +-----------------------------+
                 |                             |
                 v                             v

             WINDOWS                     WSL2 Ubuntu

      LibreHardwareMonitor            Pipeline RAG
               |                           |
               v                           |
      export_temp_server.py                |
               |                           |
          HTTP / JSON                      |
               |                           |
               +------------+--------------+
                            |
                            v
                  thermal_watchdog.py
                            |
                            |
                            v
                        query.py
                            |
            Recuperación de conocimiento
                            |
             +--------------+--------------+
             |                             |
             v                             v
      embeddings.jsonl             symbols.jsonl
             |                             |
             +--------------+--------------+
                            |
                            v
                    llm_backend.py
                     /            \
                    /              \
                   v                v
             Ollama Local     OpenRouter Cloud
                            |
                            v
                      Respuesta final
```

La recuperación del conocimiento permanece completamente local.

La generación de la respuesta se delega al backend de inferencia seleccionado.

---

# 3. Distribución de componentes

## 3.1 Componentes Windows

Windows mantiene el acceso directo al hardware y proporciona la información necesaria para la supervisión térmica.

Los principales componentes son:

| Componente | Responsabilidad |
|------------|-----------------|
| LibreHardwareMonitor | Acceso a sensores físicos |
| export_temp_server.py | Publicación de la información térmica mediante HTTP |
| start_server.bat | Inicio del servicio térmico |
| stop_server.bat | Finalización del servicio térmico |

### Flujo de funcionamiento

```text
LibreHardwareMonitor
          |
          v
export_temp_server.py
          |
          v
http://IP_WINDOWS:5005/data.json
          |
          v
thermal_watchdog.py
```

El servicio HTTP constituye el mecanismo de comunicación entre Windows y WSL2 para la supervisión térmica.

---

## 3.2 Componentes WSL2 Ubuntu

En WSL2 se ejecutan todos los componentes relacionados con la inteligencia artificial y el pipeline RAG.

Los módulos principales son:

| Componente | Responsabilidad |
|------------|-----------------|
| ingest.py | Procesamiento inicial de documentos |
| chunk.py | División del contenido en fragmentos |
| embed.py | Generación de embeddings |
| symbol_extractor.py | Extracción de información estructural del código |
| query.py | Coordinación del pipeline RAG |
| llm_backend.py | Abstracción del backend de inferencia |
| logger.py | Registro y métricas del pipeline |
| thermal_watchdog.py | Supervisión térmica independiente |

Cada módulo posee una responsabilidad claramente definida y puede evolucionar de forma independiente.

---

# 4. Pipeline RAG

El flujo de consulta implementado actualmente por `query.py` es el siguiente:

```text
Usuario
    |
    v
Recepción de la consulta
    |
    v
Detección de errores C# (cuando aplica)
    |
    v
Generación del embedding de consulta
    |
    v
Búsqueda semántica
    |
    +-------------------------+
    |                         |
    v                         v
embeddings.jsonl         symbols.jsonl
    |                         |
    +------------+------------+
                 |
                 v
Construcción del contexto
                 |
                 v
llm_backend.py
      |
      +------------------------+
      |                        |
      v                        v
Ollama Local          OpenRouter Cloud
      |
      v
Respuesta
```

El pipeline mantiene completamente separadas las etapas de:

- recuperación del conocimiento;
- construcción del contexto;
- inferencia;
- observabilidad.

Esta organización reduce el acoplamiento entre componentes y facilita la incorporación de nuevos proveedores de inferencia.

---

# 5. Separación entre recuperación e inferencia

Uno de los principales objetivos alcanzados por la arquitectura actual consiste en separar completamente la recuperación del conocimiento de la generación de respuestas.

## Recuperación del conocimiento

`query.py` mantiene la responsabilidad de:

- cargar la base vectorial (`embeddings.jsonl`);
- generar el embedding de la consulta mediante `nomic-embed-text`;
- realizar la búsqueda semántica;
- recuperar el contexto arquitectónico desde `symbols.jsonl`;
- construir el contexto enviado al modelo de lenguaje.

Todo este proceso permanece completamente local.

---

## Inferencia

Una vez construido el contexto, `query.py` delega la generación de la respuesta a `llm_backend.py`.

Este módulo constituye una capa de abstracción cuya responsabilidad consiste en seleccionar el backend configurado e invocar el proveedor correspondiente.

Actualmente se encuentran implementados dos backends:

| Backend | Implementación |
|----------|----------------|
| LOCAL | Ollama |
| CLOUD | OpenRouter |

Gracias a esta separación, el pipeline RAG no necesita conocer cómo se comunica cada proveedor de inferencia.

La incorporación de nuevos servicios de generación de respuestas puede realizarse extendiendo `llm_backend.py`, manteniendo inalterado el resto de la arquitectura.

---

# 6. Observabilidad

La observabilidad del sistema se encuentra centralizada en `logger.py`.

Este componente constituye una capa independiente cuya única responsabilidad consiste en registrar cronológicamente la ejecución del pipeline y calcular métricas de rendimiento, sin intervenir en la lógica funcional del sistema.

Cada consulta realizada por el usuario genera una nueva sesión de registro en `query_log.txt`.

La información registrada incluye, entre otros datos:

- fecha y hora de ejecución;
- backend de inferencia utilizado;
- modelo de lenguaje seleccionado;
- modelo de embeddings;
- modo de operación;
- pregunta realizada por el usuario;
- secuencia de eventos del pipeline.

Además, `logger.py` calcula automáticamente las siguientes métricas:

| Métrica | Descripción |
|----------|-------------|
| EMBEDDING_TIME | Tiempo empleado en generar el embedding de la consulta |
| SEARCH_TIME | Tiempo empleado en la recuperación semántica |
| LLM_TIME | Tiempo empleado por el backend de inferencia |
| PIPELINE_TIME | Tiempo total del pipeline, desde la recepción de la consulta hasta la presentación de la respuesta |

Estas métricas permiten evaluar el comportamiento del sistema y facilitan futuras tareas de optimización y diagnóstico.

---

# 7. Supervisión térmica

La protección térmica constituye una capa completamente independiente del pipeline RAG.

Su funcionamiento no depende de `query.py` ni de `logger.py`, lo que mantiene separadas las responsabilidades relacionadas con la inteligencia artificial y la supervisión del hardware.

El componente responsable es:

```text
thermal_watchdog.py
```

Sus principales responsabilidades son:

- consultar periódicamente la temperatura del procesador;
- obtener la información publicada por Windows mediante HTTP;
- calcular un promedio móvil de temperatura;
- clasificar el estado térmico del sistema;
- registrar eventos relacionados con la supervisión;
- detener preventivamente la ejecución de `query.py` cuando se supera un umbral crítico.

El flujo general es el siguiente:

```text
LibreHardwareMonitor
          |
          v
export_temp_server.py
          |
          v
HTTP / JSON
          |
          v
thermal_watchdog.py
          |
          +----------------------+
          |                      |
          v                      v

      Estado normal      Estado crítico
          |                      |
          |                      |
          |               Finalizar query.py
          |
          v
Continuar ejecución
```

Esta arquitectura permite mantener la supervisión térmica desacoplada del pipeline RAG y facilita su evolución de manera independiente.

---

# 8. Comunicación entre Windows y WSL2

La arquitectura requiere un mecanismo de comunicación entre el entorno Windows y WSL2 para acceder a la información térmica del sistema.

Esta comunicación se realiza mediante un servicio HTTP ligero.

El flujo es el siguiente:

```text
Windows
    |
    v
export_temp_server.py
    |
    v
http://IP_WINDOWS:5005/data.json
    |
    v
WSL2
    |
    v
thermal_watchdog.py
```

Para simplificar la configuración del entorno, el servicio de Windows genera automáticamente el archivo:

```text
windows_ip.txt
```

Este archivo permite que `thermal_watchdog.py` conozca la dirección IP del equipo anfitrión.

Si dicho archivo no se encuentra disponible, el sistema dispone de un mecanismo alternativo para localizar la dirección del host Windows.

De esta forma se evita depender de una configuración manual permanente.

---

# 9. Principios de diseño

La arquitectura actual se ha construido siguiendo varios principios que orientan la evolución del proyecto.

## Separación de responsabilidades

Cada componente mantiene una responsabilidad claramente definida.

| Componente | Responsabilidad principal |
|------------|---------------------------|
| ingest.py | Procesamiento documental |
| chunk.py | División del contenido |
| embed.py | Generación de embeddings |
| symbol_extractor.py | Extracción de información estructural |
| query.py | Coordinación del pipeline RAG |
| llm_backend.py | Inferencia mediante distintos proveedores |
| logger.py | Observabilidad y métricas |
| thermal_watchdog.py | Supervisión y protección térmica |

Esta organización facilita el mantenimiento del sistema y reduce el impacto de futuras modificaciones.

---

## Bajo acoplamiento

Los componentes interactúan mediante interfaces claramente definidas.

Por ejemplo:

- `query.py` no conoce cómo se realiza la comunicación con Ollama u OpenRouter.
- `llm_backend.py` no participa en la recuperación del conocimiento.
- `logger.py` no modifica el comportamiento del pipeline.
- `thermal_watchdog.py` no forma parte de la lógica de inferencia.

Esta separación permite modificar un componente sin afectar al resto de la arquitectura.

---

## Recuperación local del conocimiento

La recuperación semántica permanece completamente local.

Actualmente el sistema utiliza:

- `embeddings.jsonl` para la recuperación documental;
- `symbols.jsonl` para incorporar contexto arquitectónico.

De esta manera, el conocimiento utilizado por el pipeline permanece bajo control del entorno local.

---

## Inferencia desacoplada

La generación de respuestas constituye una responsabilidad independiente de la recuperación del conocimiento.

La incorporación de nuevos proveedores de inferencia puede realizarse ampliando `llm_backend.py`, sin modificar el flujo principal implementado por `query.py`.

---

## Observabilidad

El registro de eventos y métricas forma parte de la arquitectura desde el propio diseño del sistema.

La información registrada permite analizar el comportamiento del pipeline y facilita futuras tareas de mantenimiento, diagnóstico y optimización.

---

# 10. Estado actual de la arquitectura

Al 24 de julio de 2026, la arquitectura implementada permite:

- ejecutar un pipeline RAG con recuperación completamente local;
- generar embeddings mediante `nomic-embed-text`;
- utilizar `embeddings.jsonl` para la recuperación semántica;
- complementar la recuperación con contexto arquitectónico obtenido desde `symbols.jsonl`;
- desacoplar la inferencia mediante `llm_backend.py`;
- seleccionar entre un backend LOCAL (Ollama) y un backend CLOUD (OpenRouter);
- registrar automáticamente métricas de ejecución mediante `logger.py`;
- supervisar continuamente el estado térmico del sistema mediante `thermal_watchdog.py`.

La arquitectura alcanzada constituye una base modular preparada para continuar evolucionando mediante la incorporación de nuevos proveedores de inferencia, mejoras en la recuperación del conocimiento y nuevas capacidades de observabilidad, manteniendo estable el núcleo del pipeline RAG.

---

# 11. Consideraciones finales

El objetivo de esta arquitectura no es únicamente ejecutar modelos de lenguaje, sino construir una base sólida sobre la cual puedan incorporarse nuevas capacidades sin comprometer la estabilidad del sistema.

La separación entre recuperación, inferencia, observabilidad y supervisión térmica representa el principal resultado arquitectónico alcanzado hasta la fecha y constituye el punto de partida para la evolución futura del proyecto.
