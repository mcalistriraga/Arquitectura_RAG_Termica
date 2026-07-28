# Arquitectura del Sistema

## 1. Introducción

La arquitectura de **Arquitectura_RAG_Termica** ha evolucionado desde un sistema orientado exclusivamente a la ejecución local de modelos de lenguaje hacia una arquitectura híbrida, modular y desacoplada, diseñada para servir como plataforma de construcción de asistentes técnicos especializados.

El objetivo principal es separar claramente las distintas responsabilidades del sistema para facilitar su mantenimiento, su evolución y la incorporación de nuevos componentes sin afectar al funcionamiento del pipeline principal.

Actualmente la arquitectura distingue dos niveles claramente diferenciados:

- **La plataforma asistente**, implementada por el proyecto Arquitectura_RAG_Termica.
- **El proyecto técnico asistido**, cuya documentación y código fuente constituyen la base de conocimiento activa utilizada por el pipeline RAG.

En el estado actual del proyecto, la base de conocimiento corresponde a una aplicación desarrollada con **.NET MAUI**. Sin embargo, la arquitectura ha sido diseñada para que dicha base pueda sustituirse posteriormente por la documentación o el código fuente de cualquier otro proyecto, sin modificar el funcionamiento interno del asistente.

La arquitectura continúa organizándose en dos entornos complementarios:

- **Windows**, responsable del acceso al hardware físico y de la publicación de la información térmica.
- **WSL2 Ubuntu**, responsable de la ejecución del pipeline RAG, la recuperación del conocimiento, la inferencia mediante modelos de lenguaje y la supervisión del sistema.

Uno de los principios arquitectónicos más importantes consiste en la separación entre:

- recuperación del conocimiento;
- construcción del contexto;
- generación de respuestas;
- observabilidad;
- supervisión térmica.

Esta separación permite incorporar nuevos modelos, nuevos proveedores de inferencia y nuevas bases documentales sin modificar el núcleo del pipeline.

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
             Recuperación del conocimiento
                            |
             +--------------+--------------+
             |                             |
             v                             v
      embeddings.jsonl             symbols.jsonl
             |                             |
             +--------------+--------------+
                            |
                            v
                 Construcción del contexto
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

El contexto construido a partir de la búsqueda semántica constituye la principal fuente de información enviada al modelo de lenguaje.

La generación de la respuesta se delega completamente al backend de inferencia seleccionado.

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
| logger.py | Observabilidad y métricas del pipeline |
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
Construcción del prompt
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

- recepción de la consulta;
- recuperación del conocimiento;
- construcción del contexto;
- construcción del prompt;
- inferencia;
- observabilidad.

En la versión actual, el contenido recuperado desde `embeddings.jsonl` vuelve a incorporarse explícitamente al contexto enviado al modelo de lenguaje.

De esta forma, la recuperación semántica deja de constituir únicamente un mecanismo de búsqueda y pasa a formar parte activa de la generación de respuestas.

Asimismo, `query.py` incorpora mecanismos opcionales de depuración controlados mediante banderas de configuración, permitiendo visualizar y registrar los fragmentos recuperados durante la búsqueda semántica sin modificar la lógica principal del pipeline.

---

# 5. Separación entre recuperación e inferencia

Uno de los principales objetivos alcanzados por la arquitectura actual consiste en separar completamente la recuperación del conocimiento de la generación de respuestas.

## Recuperación del conocimiento

`query.py` mantiene la responsabilidad de:

- cargar la base vectorial (`embeddings.jsonl`);
- generar el embedding de la consulta mediante `nomic-embed-text`;
- realizar la búsqueda semántica;
- recuperar contexto arquitectónico desde `symbols.jsonl`;
- reconstruir el contexto que será enviado al modelo de lenguaje.

Todo este proceso permanece completamente local.

La base documental utilizada por el pipeline no forma parte de la arquitectura del asistente, sino del proyecto técnico que se desea analizar.

En el estado actual del desarrollo, dicha base corresponde a una aplicación .NET MAUI utilizada como caso de uso para validar el funcionamiento del asistente técnico.

## Inferencia

Una vez construido el contexto, `query.py` delega completamente la generación de la respuesta a `llm_backend.py`.

Este módulo constituye una capa de abstracción cuya responsabilidad consiste en seleccionar el backend configurado e invocar el proveedor correspondiente.

Actualmente se encuentran implementados dos backends:

| Backend | Implementación |
|----------|----------------|
| LOCAL | Ollama |
| CLOUD | OpenRouter |

Gracias a esta separación, el pipeline RAG no necesita conocer cómo se comunica cada proveedor de inferencia.

La incorporación de nuevos servicios de generación de respuestas puede realizarse ampliando `llm_backend.py`, manteniendo inalterado el resto de la arquitectura.

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
| PIPELINE_TIME | Tiempo total del pipeline desde la recepción de la consulta hasta la presentación de la respuesta |

Como complemento a las métricas automáticas, `logger.py` incorpora la función genérica `log_debug()`, que permite registrar información adicional de depuración desde cualquier módulo del proyecto.

Esta funcionalidad facilita el análisis temporal del sistema sin alterar el comportamiento normal del pipeline y resulta especialmente útil durante el desarrollo y la validación de nuevas funcionalidades.

Por ejemplo, `query.py` puede registrar opcionalmente los fragmentos recuperados durante la búsqueda semántica cuando la bandera `DEBUG_CHUNKS` se encuentra habilitada.

La activación de este mecanismo es completamente opcional y no modifica la ejecución normal del sistema.

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

Esta arquitectura permite mantener la supervisión térmica completamente desacoplada del pipeline RAG y facilita su evolución de manera independiente.

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

Si dicho archivo no se encuentra disponible, el sistema dispone de un mecanismo alternativo para localizar automáticamente la dirección del host Windows.

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
| query.py | Coordinación completa del pipeline RAG |
| llm_backend.py | Abstracción del backend de inferencia |
| logger.py | Observabilidad y métricas |
| thermal_watchdog.py | Supervisión y protección térmica |

Esta organización facilita el mantenimiento del sistema y reduce el impacto de futuras modificaciones.

---

## Bajo acoplamiento

Los componentes interactúan mediante interfaces claramente definidas.

Por ejemplo:

- `query.py` no conoce cómo se realiza la comunicación con Ollama u OpenRouter.
- `llm_backend.py` no participa en la recuperación del conocimiento.
- `logger.py` no modifica el comportamiento funcional del pipeline.
- `thermal_watchdog.py` no forma parte de la lógica de inferencia.

Esta separación permite modificar un componente sin afectar al resto de la arquitectura.

---

## Recuperación local del conocimiento

La recuperación semántica permanece completamente local.

Actualmente el sistema utiliza:

- `embeddings.jsonl` para la recuperación documental;
- `symbols.jsonl` para incorporar información estructural del código cuando corresponde.

La base documental representa el conocimiento del proyecto técnico asistido y puede sustituirse por la documentación o el código fuente de otro proyecto sin modificar la arquitectura del asistente.

---

## Inferencia desacoplada

La generación de respuestas constituye una responsabilidad independiente de la recuperación del conocimiento.

La incorporación de nuevos proveedores de inferencia puede realizarse ampliando `llm_backend.py`, sin modificar el flujo principal implementado por `query.py`.

---

## Observabilidad integrada

La observabilidad forma parte del diseño arquitectónico desde el inicio del proyecto.

El registro cronológico de eventos, las métricas automáticas y los mecanismos opcionales de depuración permiten comprender el comportamiento interno del pipeline durante las distintas fases de desarrollo, validación y mantenimiento.

---

# 10. Estado actual de la arquitectura

En el estado actual del proyecto, la arquitectura implementada permite:

- ejecutar un pipeline RAG con recuperación completamente local;
- generar embeddings mediante `nomic-embed-text`;
- recuperar información semántica desde `embeddings.jsonl`;
- complementar el contexto mediante `symbols.jsonl`;
- reconstruir el contexto enviado al modelo de lenguaje;
- desacoplar completamente la inferencia mediante `llm_backend.py`;
- seleccionar dinámicamente entre un backend LOCAL (Ollama) y un backend CLOUD (OpenRouter);
- registrar automáticamente métricas de ejecución mediante `logger.py`;
- registrar información adicional de depuración mediante `log_debug()`;
- habilitar o deshabilitar mecanismos de diagnóstico mediante banderas de configuración como `DEBUG_CHUNKS`;
- supervisar continuamente el estado térmico del sistema mediante `thermal_watchdog.py`.

Actualmente, la base de conocimiento activa corresponde a un proyecto desarrollado con .NET MAUI, utilizado como caso de uso para validar el funcionamiento del asistente técnico.

La arquitectura ha sido diseñada para permitir sustituir dicha base documental por la correspondiente a cualquier otro proyecto, manteniendo inalterado el funcionamiento del pipeline.

---

# 11. Consideraciones finales

El objetivo de esta arquitectura no es únicamente ejecutar modelos de lenguaje, sino construir una plataforma reutilizable para el desarrollo de asistentes técnicos especializados.

La separación entre recuperación del conocimiento, construcción del contexto, inferencia, observabilidad y supervisión térmica constituye el principal resultado arquitectónico alcanzado hasta la fecha.

Esta organización permite que el asistente evolucione independientemente del proyecto técnico analizado, facilitando su reutilización con diferentes aplicaciones mediante el simple reemplazo de la base de conocimiento.

En consecuencia, la arquitectura distingue claramente entre:

- el **asistente técnico**, responsable de ejecutar el pipeline RAG y coordinar sus componentes; y
- el **proyecto asistido**, cuya documentación y código fuente constituyen el conocimiento utilizado para responder las consultas del usuario.

Esta separación constituye la base para la evolución futura del sistema hacia un asistente técnico reutilizable, capaz de adaptarse a distintos proyectos de software sin requerir cambios en su arquitectura interna.

