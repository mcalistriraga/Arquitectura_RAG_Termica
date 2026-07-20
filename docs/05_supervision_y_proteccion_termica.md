# Supervisión y Protección Térmica

## 1. Introducción

La ejecución local de modelos de inteligencia artificial puede generar una carga elevada sobre el procesador, especialmente durante:

* generación de embeddings,
* inferencia mediante modelos LLM,
* consultas prolongadas mediante RAG.

Debido a que el proyecto se ejecuta sobre hardware limitado y sin aceleración GPU dedicada, se incorporó una arquitectura de supervisión térmica independiente que permite:

* obtener información real del hardware,
* monitorear la temperatura del CPU,
* detectar condiciones críticas,
* registrar eventos,
* detener procesos cuando existe riesgo térmico.

La supervisión térmica funciona como una capa externa de protección del sistema RAG.

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

# 9. Integración con query.py

La protección térmica está integrada mediante:

```text
query.py

    |
    v

logger.py

    |
    v

thermal_watchdog.py
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

La protección térmica fue diseñada bajo los siguientes principios:

## Separación de responsabilidades

```text
LibreHardwareMonitor
        |
        v
Adquisición hardware


export_temp_server.py
        |
        v
Adaptación


thermal_watchdog.py
        |
        v
Decisión


query.py
        |
        v
Aplicación IA
```

---

## Bajo acoplamiento

El pipeline RAG no necesita conocer:

* sensores,
* fabricantes,
* chips,
* LibreHardwareMonitor.

Solo recibe una señal externa de seguridad.

---

# 15. Estado actual

Actualmente el sistema permite:

* monitoreo térmico en tiempo real,
* comunicación Windows-WSL,
* detección de temperatura crítica,
* registro de eventos,
* protección automática del proceso RAG.

Esta capa convierte una ejecución experimental de IA local en un sistema más seguro y controlado para hardware limitado.

