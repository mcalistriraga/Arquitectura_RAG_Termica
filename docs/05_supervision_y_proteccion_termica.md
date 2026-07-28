# Supervisión y Protección Térmica

## 1. Introducción

La ejecución del pipeline RAG puede generar una carga elevada sobre el procesador, especialmente durante tareas como:

- generación de embeddings;
- recuperación semántica;
- inferencia mediante modelos LLM ejecutados localmente.

Con el objetivo de proteger el hardware utilizado durante el desarrollo, el proyecto incorpora una arquitectura de supervisión térmica desacoplada del pipeline principal.

Esta arquitectura permite:

- obtener información real de los sensores del equipo;
- supervisar continuamente la temperatura del procesador;
- detectar condiciones térmicas críticas;
- registrar eventos relevantes;
- ejecutar acciones de protección cuando sea necesario.

La supervisión térmica funciona como un subsistema independiente del pipeline RAG y mantiene el mismo funcionamiento independientemente del backend de inferencia seleccionado (LOCAL o CLOUD).

---

# 2. Arquitectura de supervisión

El flujo completo es:

```text
                 HARDWARE FÍSICO

                       |
                       v

          LibreHardwareMonitor

                       |
                       v

          export_temp_server.py

                       |
                       |
                HTTP JSON
                       |
                       v

                 WSL2 Ubuntu

                       |
                       v

          thermal_watchdog.py

                       |
              +--------+--------+
              |                 |
              v                 v

          Estado normal     Estado crítico

              |                 |
              v                 v

        Continúa RAG       Detiene query.py
```

---

# 3. Componente Windows

## 3.1 LibreHardwareMonitor

LibreHardwareMonitor es la fuente primaria de información térmica.

Responsabilidades:

* acceder a sensores físicos,
* leer temperatura del procesador,
* publicar información mediante JSON.

Endpoint original:

```text
http://localhost:8085/data.json
```

---

# 4. Servicio export_temp_server.py

## Ubicación

```text
E:\Developer\Tools\LibreHardwareMonitor\python
```

---

## Objetivo

Este servicio actúa como una capa de adaptación entre LibreHardwareMonitor y WSL2.

Su función es:

```text
LibreHardwareMonitor
        |
        v
JSON complejo de sensores
        |
        v
export_temp_server.py
        |
        v
JSON simplificado
```

---

## Responsabilidades

El servicio:

* consulta el JSON generado por LibreHardwareMonitor,
* localiza el sensor correcto de temperatura,
* convierte el valor a formato numérico,
* publica una API Flask,
* genera información de conexión para WSL.

---

## Sensor utilizado

La búsqueda está orientada al árbol:

```text
Nuvoton NCT6776F

    |
    +-- Temperatures

            |
            +-- Temperature #1
```

---

## Endpoint publicado

El servicio genera:

```text
http://IP_WINDOWS:5005/data.json
```

Ejemplo:

```json
{
    "id":0,
    "Text":"CPU Temperature",
    "Value":45.0,
    "Min":0,
    "Max":100
}
```

---

# 5. Descubrimiento de IP Windows

Debido a que la dirección IP del equipo Windows puede cambiar, se implementó un mecanismo automático.

Archivo generado:

```text
windows_ip.txt
```

Ubicación:

```text
E:\Developer\Tools\LibreHardwareMonitor\python
```

Contenido ejemplo:

```text
192.168.1.36
```

---

## Uso desde WSL

El watchdog primero intenta leer:

```text
windows_ip.txt
```

Si existe:

```text
IP Windows detectada desde archivo
```

Si no existe:

utiliza como respaldo el gateway de WSL.

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

Es el componente encargado de supervisar continuamente la temperatura del CPU y proteger los procesos de inteligencia artificial.

---

## Funciones principales

### Lectura térmica

Consulta:

```text
http://IP_WINDOWS:5005/data.json
```

mediante:

```python
requests.get()
```

---

### Promedio móvil

El sistema utiliza una ventana de temperatura:

```python
WINDOW_SIZE = 5
```

Esto evita tomar decisiones basadas en un pico instantáneo.

---

# 7. Umbrales térmicos

Configuración actual:

| Parámetro | Valor |
|-|-|
| TEMP_WARNING | 58 °C |
| TEMP_CRITICAL | 62 °C |
| TEMP_HARD_LIMIT | 70 °C |
| TEMP_RECOVERY | 58 °C |

---

# 8. Estados térmicos

## NORMAL

Condición:

```text
Temperatura dentro del rango seguro
```

Acción:

```text
Continúa ejecución RAG
```

---

## WARNING

Condición:

```text
Promedio móvil >= 58 °C
```

Acción:

```text
Mantener supervisión
```

---

## CRITICAL

Condición:

```text
Temperatura >= 62 °C
```

Acciones:

* registrar evento,
* activar bloqueo,
* detener proceso RAG.

---

## HARD LIMIT

Condición:

```text
Temperatura >= 70 °C
```

Acción:

Protección inmediata.

---

# 9. Integración con el pipeline RAG

La supervisión térmica funciona de forma desacoplada respecto al pipeline principal. 
Mientras query.py ejecuta el procesamiento RAG y logger.py registra la actividad de 
la consulta, thermal_watchdog.py supervisa continuamente la temperatura del sistema 
y puede ejecutar acciones de protección cuando se alcanzan los umbrales 
configurados.

```text
                 query.py

                /       \

               v         v

        logger.py   Ejecución RAG

                         │

                         ▼

              thermal_watchdog.py
                   (proceso independiente)

                         │

                         ▼

            Protección del sistema
```

Durante la consulta se verifican puntos críticos:

```text
Inicio embedding

        |
        v

Búsqueda semántica

        |
        v

Ejecución LLM
```

Antes de operaciones intensivas se valida la temperatura.

---

# 10. Logger térmico y de ejecución

## logger.py

Además de registrar tiempos del pipeline RAG, incorpora información térmica.

Registra:

* inicio de sesión,
* modo seleccionado,
* pasos ejecutados,
* temperatura,
* eventos de aborto.

Ejemplo:

```text
[12.532s]
STEP=LLM_START
MODE=ARCH
TEMP=61.5
ABORT=False
```

---

# 11. Detención automática

Cuando se alcanza una condición crítica:

```text
thermal_watchdog.py

        |
        v

pkill -f query.py
```

Resultado:

```text
Proceso RAG detenido
```

---

# 12. Registro de eventos críticos

El watchdog genera:

```text
thermal_watchdog_log.txt
```

Incluye:

* fecha,
* motivo,
* temperatura actual,
* promedio móvil,
* endpoint utilizado,
* acción ejecutada.

Ejemplo:

```text
THERMAL WATCHDOG EVENT

Fecha:
2026-07-14 14:30:00

Motivo:
TEMP_CRITICAL

Temperatura:
63.5 °C

Acción:
pkill -f query.py
```

---

# 13. Recuperación

Después de una condición crítica:

El sistema espera:

```text
Temperatura < 58 °C
```

y:

```text
Promedio móvil < TEMP_WARNING
```

Cuando se cumplen ambas condiciones:

```text
Sistema recuperado
watchdog desbloqueado
```

---

# 14. Filosofía de diseño

La arquitectura de supervisión térmica fue diseñada siguiendo principios de modularidad y bajo acoplamiento, manteniendo separadas las responsabilidades de adquisición de datos, supervisión y ejecución del pipeline RAG.

## Separación de responsabilidades

Cada componente cumple una función específica dentro del sistema:

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
query.py
        │
        ▼
Pipeline RAG
```

Esta organización facilita el mantenimiento del sistema y permite modificar cualquiera de los componentes sin afectar significativamente al resto de la arquitectura.

---

## Desacoplamiento

La supervisión térmica se ejecuta como un proceso independiente del pipeline RAG.

Esta decisión permite mantener separadas las responsabilidades de:

- adquisición de datos del hardware;
- supervisión térmica;
- procesamiento documental;
- generación de respuestas mediante modelos LLM.

Como consecuencia, el pipeline principal no necesita incorporar lógica específica relacionada con sensores, controladores de hardware o mecanismos de protección térmica.

---

## Bajo acoplamiento

El pipeline RAG no necesita conocer detalles de implementación relacionados con:

- sensores físicos;
- fabricantes del hardware;
- chips de monitorización;
- LibreHardwareMonitor;
- mecanismos de adquisición de temperatura.

La única interacción entre ambos subsistemas consiste en la aplicación de acciones de protección cuando el watchdog detecta condiciones térmicas críticas.

Esta separación favorece la reutilización de los componentes y permite sustituir el mecanismo de adquisición de datos térmicos sin modificar el funcionamiento del pipeline RAG.


---
# 15. Estado actual

Actualmente el sistema proporciona:

- monitoreo térmico continuo mediante LibreHardwareMonitor;
- comunicación entre Windows y WSL2 mediante un servicio HTTP basado en Flask;
- supervisión independiente mediante `thermal_watchdog.py`;
- registro detallado de eventos durante la ejecución del pipeline;
- protección automática frente a condiciones de sobretemperatura.

La supervisión térmica constituye un componente desacoplado de la arquitectura y protege la ejecución del pipeline independientemente del backend de inferencia utilizado (LOCAL mediante Ollama o CLOUD mediante OpenRouter).

