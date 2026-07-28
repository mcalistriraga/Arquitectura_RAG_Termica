# Supervisión y Protección Térmica

## 1. Introducción

La ejecución del pipeline RAG puede generar una carga elevada sobre el procesador, especialmente durante tareas como:

- generación de embeddings;
- recuperación semántica;
- construcción del contexto de trabajo;
- inferencia mediante modelos LLM ejecutados localmente.

Con el objetivo de proteger el hardware utilizado durante el desarrollo, el proyecto incorpora una arquitectura de supervisión térmica completamente desacoplada del pipeline principal.

Esta arquitectura permite:

- obtener información real de los sensores del equipo;
- supervisar continuamente la temperatura del procesador;
- detectar condiciones térmicas críticas;
- registrar eventos relevantes del sistema;
- ejecutar acciones automáticas de protección cuando sea necesario.

La supervisión térmica constituye un subsistema independiente del pipeline RAG y mantiene el mismo funcionamiento independientemente del backend de inferencia seleccionado (LOCAL o CLOUD). De esta forma, la protección del hardware permanece activa tanto cuando la generación de respuestas se realiza mediante Ollama como cuando se utiliza OpenRouter.

---

# 2. Arquitectura de supervisión

La arquitectura térmica se encuentra separada de la lógica de recuperación del conocimiento y de la generación de respuestas.

El flujo completo es el siguiente:

```text
                 HARDWARE FÍSICO

                       │
                       ▼

          LibreHardwareMonitor

                       │
                       ▼

          export_temp_server.py

                       │
                 HTTP / JSON
                       │
                       ▼

                 WSL2 Ubuntu

                       │
                       ▼

          thermal_watchdog.py

                       │
              +--------+--------+
              │                 │
              ▼                 ▼

          Estado normal   Estado crítico

              │                 │
              ▼                 ▼

        Continúa RAG     Detiene query.py
```

El watchdog se ejecuta como un proceso independiente y no forma parte del pipeline implementado por `query.py`.

---

# 3. Componente Windows

## 3.1 LibreHardwareMonitor

LibreHardwareMonitor constituye la fuente primaria de información térmica utilizada por el sistema.

Responsabilidades:

- acceder a los sensores físicos del equipo;
- obtener la temperatura del procesador;
- publicar la información mediante un servicio JSON.

Endpoint original:

```text
http://localhost:8085/data.json
```

El proyecto no consulta directamente este endpoint desde WSL2. En su lugar, utiliza un servicio intermedio que simplifica la información publicada y facilita la comunicación entre ambos entornos.

---

# 4. Servicio export_temp_server.py

## Ubicación

```text
E:\Developer\Tools\LibreHardwareMonitor\python
```

---

## Objetivo

`export_temp_server.py` actúa como una capa de adaptación entre LibreHardwareMonitor y WSL2.

Su función puede representarse mediante el siguiente flujo:

```text
LibreHardwareMonitor
        │
        ▼

JSON completo de sensores

        │
        ▼

export_temp_server.py

        │
        ▼

JSON simplificado

        │
        ▼

Servicio HTTP para WSL2
```

De esta manera, los componentes del pipeline RAG no necesitan conocer la estructura interna del JSON generado por LibreHardwareMonitor.

---

## Responsabilidades

El servicio realiza las siguientes tareas:

- consultar periódicamente el JSON generado por LibreHardwareMonitor;
- localizar el sensor correspondiente a la temperatura del procesador;
- convertir el valor a un formato numérico uniforme;
- publicar un servicio HTTP mediante Flask;
- generar automáticamente la información de conexión utilizada desde WSL2.

---

## Sensor utilizado

La implementación actual obtiene la temperatura desde el árbol de sensores:

```text
Nuvoton NCT6776F

    │
    └── Temperatures

            │
            └── Temperature #1
```

La ubicación exacta del sensor puede variar dependiendo del hardware, aunque el diseño del sistema permite adaptar fácilmente este componente sin modificar el resto de la arquitectura.

---

## Endpoint publicado

El servicio expone el siguiente endpoint:

```text
http://IP_WINDOWS:5005/data.json
```

Ejemplo de respuesta:

```json
{
    "id": 0,
    "Text": "CPU Temperature",
    "Value": 45.0,
    "Min": 0,
    "Max": 100
}
```

Este formato simplificado facilita el consumo de la información desde `thermal_watchdog.py`.

---

# 5. Descubrimiento automático de la IP de Windows

La dirección IP del host Windows puede cambiar entre reinicios o sesiones de trabajo.

Para evitar configuraciones manuales repetitivas, el sistema implementa un mecanismo de descubrimiento automático.

Archivo generado:

```text
windows_ip.txt
```

Ubicación:

```text
E:\Developer\Tools\LibreHardwareMonitor\python
```

Ejemplo:

```text
192.168.1.36
```

---

## Uso desde WSL2

Durante su inicialización, `thermal_watchdog.py` intenta localizar la dirección IP del equipo Windows siguiendo este orden:

1. Leer el archivo:

```text
windows_ip.txt
```

2. Si el archivo existe:

```text
IP Windows detectada desde archivo.
```

3. Si el archivo no existe:

- utilizar automáticamente el gateway de WSL2 como mecanismo alternativo.

Este procedimiento evita depender de configuraciones manuales y mejora la portabilidad del entorno.

---

# 6. Thermal Watchdog

## Archivo

```text
thermal_watchdog.py
```

---

## Ubicación

```text
/home/manuelc/rag_maui_docs_for_rag/scripts
```

---

## Objetivo

`thermal_watchdog.py` es el componente responsable de supervisar continuamente la temperatura del procesador y proteger la ejecución del sistema frente a condiciones de sobretemperatura.

Su funcionamiento es completamente independiente de:

- `query.py`;
- `logger.py`;
- `llm_backend.py`;
- Ollama;
- OpenRouter.

Gracias a esta separación, cualquier modificación del pipeline RAG puede realizarse sin afectar la lógica de supervisión térmica.

---

## Funciones principales

Entre sus responsabilidades se encuentran:

- consultar periódicamente la temperatura del procesador;
- calcular un promedio móvil;
- clasificar el estado térmico del sistema;
- registrar eventos relevantes;
- ejecutar acciones preventivas cuando se superan los umbrales configurados.

---

### Lectura térmica

La información se obtiene consultando:

```text
http://IP_WINDOWS:5005/data.json
```

mediante:

```python
requests.get()
```

---

### Promedio móvil

Para evitar decisiones basadas en picos instantáneos de temperatura, el watchdog utiliza una ventana móvil:

```python
WINDOW_SIZE = 5
```

Cada nueva lectura actualiza el promedio utilizado para clasificar el estado térmico del sistema.

---

# 7. Umbrales térmicos

Configuración actual:

| Parámetro | Valor |
|-----------|------:|
| TEMP_WARNING | 58 °C |
| TEMP_CRITICAL | 62 °C |
| TEMP_HARD_LIMIT | 70 °C |
| TEMP_RECOVERY | 58 °C |

Estos valores permiten distinguir diferentes niveles de riesgo y aplicar acciones progresivas de protección.

---

# 8. Estados térmicos

## NORMAL

Condición:

```text
Temperatura dentro del rango seguro.
```

Acción:

```text
El pipeline continúa ejecutándose normalmente.
```

---

## WARNING

Condición:

```text
Promedio móvil >= TEMP_WARNING
```

Acción:

```text
Mantener la supervisión y continuar monitoreando la evolución de la temperatura.
```

---

## CRITICAL

Condición:

```text
Temperatura >= TEMP_CRITICAL
```

Acciones:

- registrar el evento crítico;
- activar el estado de protección;
- finalizar la ejecución de `query.py` para evitar un incremento adicional de temperatura.

---

## HARD LIMIT

Condición:

```text
Temperatura >= TEMP_HARD_LIMIT
```

Acción:

```text
Aplicar protección inmediata independientemente del estado previo del sistema.
```
---
# 9. Integración con el pipeline RAG

La supervisión térmica constituye una capa completamente independiente del pipeline RAG.

Mientras `query.py` coordina la recuperación del conocimiento, construye el contexto y delega la inferencia al backend configurado, `logger.py` registra cronológicamente la ejecución y `thermal_watchdog.py` supervisa continuamente el estado térmico del equipo.

Esta separación mantiene desacopladas las responsabilidades de:

- recuperación del conocimiento;
- generación de respuestas;
- observabilidad del sistema;
- protección del hardware.

La arquitectura puede resumirse de la siguiente manera:

```text
                    query.py
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼

 Recuperación RAG   logger.py    llm_backend.py
                                        │
                               LOCAL / CLOUD
                                        │
                                        ▼
                                 Respuesta LLM


          thermal_watchdog.py
        (proceso independiente)

                  │
                  ▼

      Supervisión continua del hardware

                  │
                  ▼

      Protección preventiva del sistema
```

`thermal_watchdog.py` no participa en la lógica funcional del pipeline y tampoco necesita conocer el backend de inferencia seleccionado.

Su única responsabilidad consiste en supervisar las condiciones térmicas del sistema y ejecutar acciones preventivas cuando sea necesario.

Esta característica permite proteger tanto las consultas ejecutadas mediante Ollama como aquellas que utilizan OpenRouter u otros proveedores que puedan incorporarse en el futuro.

---

# 10. Observabilidad y registro de la ejecución

## logger.py

El mecanismo de observabilidad del proyecto se encuentra centralizado en `logger.py`.

Su responsabilidad consiste en registrar cronológicamente la ejecución de cada consulta y calcular automáticamente las métricas de rendimiento del pipeline, sin modificar el comportamiento funcional del sistema.

Entre la información registrada se encuentran:

- inicio y finalización de la sesión;
- modo de operación seleccionado;
- backend de inferencia utilizado;
- modelo de lenguaje empleado;
- secuencia de eventos del pipeline;
- métricas automáticas de rendimiento.

Las métricas actualmente calculadas son:

| Métrica | Descripción |
|----------|-------------|
| EMBEDDING_TIME | Tiempo de generación del embedding de la consulta. |
| SEARCH_TIME | Tiempo empleado por la recuperación semántica. |
| LLM_TIME | Tiempo consumido por el backend de inferencia. |
| PIPELINE_TIME | Tiempo total del pipeline desde la recepción de la consulta hasta la presentación de la respuesta. |

Durante tareas de desarrollo también es posible registrar información adicional de depuración, como los *chunks* recuperados por la búsqueda semántica, mediante funciones específicas del logger.

Esta información de depuración es opcional y no modifica el funcionamiento del pipeline RAG.

---

# 11. Detención automática

Cuando el watchdog detecta una condición térmica crítica, ejecuta automáticamente el mecanismo de protección configurado.

En la implementación actual la acción consiste en finalizar la ejecución del proceso:

```text
query.py
```

mediante:

```text
pkill -f query.py
```

Como resultado:

```text
Proceso RAG detenido preventivamente.
```

La lógica de protección permanece completamente desacoplada de `query.py`, por lo que el pipeline no necesita implementar verificaciones térmicas internas.

---

# 12. Registro de eventos críticos

Los eventos relacionados con la supervisión térmica se almacenan en:

```text
thermal_watchdog_log.txt
```

Entre la información registrada se incluye:

- fecha y hora del evento;
- motivo de la activación;
- temperatura instantánea;
- promedio móvil;
- endpoint utilizado;
- acción ejecutada.

Ejemplo simplificado:

```text
THERMAL WATCHDOG EVENT

Fecha:
2026-07-28 14:30:00

Motivo:
TEMP_CRITICAL

Temperatura:
63.5 °C

Promedio:
61.9 °C

Acción:
pkill -f query.py
```

Este registro facilita el análisis posterior de eventos relacionados con la protección térmica del sistema.

---

# 13. Recuperación

Después de una condición crítica, el watchdog permanece supervisando la temperatura del procesador.

La recuperación se considera completada cuando se cumplen simultáneamente las siguientes condiciones:

```text
Temperatura < TEMP_RECOVERY
```

y

```text
Promedio móvil < TEMP_WARNING
```

Cuando ambas condiciones se satisfacen, el sistema abandona el estado de protección y continúa con la supervisión normal.

Este mecanismo evita reanudar inmediatamente la ejecución mientras la temperatura aún presenta una tendencia elevada.

---

# 14. Filosofía de diseño

La arquitectura de supervisión térmica fue diseñada siguiendo principios de modularidad, bajo acoplamiento y separación de responsabilidades.

## Separación de responsabilidades

Cada componente mantiene una función claramente definida dentro del sistema:

```text
LibreHardwareMonitor
        │
        ▼
Adquisición de datos
del hardware

        │
        ▼
export_temp_server.py
        │
        ▼
Adaptación y publicación
mediante HTTP (Flask)

        │
        ▼
thermal_watchdog.py
        │
        ▼
Supervisión y toma
de decisiones

        │
        ▼
Protección preventiva
del pipeline RAG
```

Esta organización facilita el mantenimiento del sistema y permite evolucionar cualquiera de los componentes sin afectar significativamente al resto de la arquitectura.

---

## Desacoplamiento

La supervisión térmica se ejecuta como un proceso completamente independiente del pipeline RAG.

Esta decisión mantiene separadas las responsabilidades relacionadas con:

- adquisición de datos del hardware;
- supervisión térmica;
- recuperación del conocimiento;
- inferencia mediante modelos de lenguaje;
- observabilidad del sistema.

Como consecuencia, `query.py`, `llm_backend.py` y `logger.py` permanecen libres de lógica específica relacionada con sensores o mecanismos de protección térmica.

---

## Bajo acoplamiento

El pipeline principal no necesita conocer detalles de implementación relacionados con:

- sensores físicos;
- fabricantes del hardware;
- chips de monitorización;
- LibreHardwareMonitor;
- mecanismos de adquisición de temperatura.

La única interacción entre ambos subsistemas consiste en la acción preventiva ejecutada por `thermal_watchdog.py` cuando se detectan condiciones térmicas críticas.

Esta arquitectura facilita la reutilización de los componentes y permite sustituir el mecanismo de adquisición de datos térmicos sin modificar el funcionamiento del pipeline RAG.

---

# 15. Estado actual

Al 28 de julio de 2026, el sistema proporciona:

- monitoreo continuo de la temperatura mediante LibreHardwareMonitor;
- comunicación entre Windows y WSL2 mediante un servicio HTTP basado en Flask;
- detección automática de la dirección IP del host Windows;
- supervisión independiente mediante `thermal_watchdog.py`;
- protección automática frente a condiciones de sobretemperatura;
- integración completamente desacoplada respecto al pipeline RAG;
- compatibilidad con los backends de inferencia LOCAL (Ollama) y CLOUD (OpenRouter);
- registro independiente de eventos térmicos y métricas de ejecución.

La arquitectura alcanzada permite proteger el hardware durante la ejecución del sistema sin interferir con la recuperación del conocimiento, la construcción del contexto ni la generación de respuestas.

La supervisión térmica continúa evolucionando de forma independiente del resto del proyecto, manteniendo como objetivo principal preservar la estabilidad del entorno de ejecución y facilitar futuras mejoras sin comprometer el diseño modular de la arquitectura.
