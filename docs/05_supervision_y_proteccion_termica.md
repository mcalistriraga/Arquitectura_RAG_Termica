# 05 — Supervisión y Protección Térmica

**Fecha:** 26 de agosto de 2026
**Versión:** 0.5.1
**Estado:** Consolidado / Documentación oficial
**Módulo:** Infraestructura / Protección Térmica & Telemetría
**Propósito:** Especificar la arquitectura de supervisión térmica desacoplada entre Windows y WSL2 Ubuntu, el servicio HTTP en Flask (`export_temp_server.py`), el watchdog preventivo (`thermal_watchdog.py`) y sus políticas de interrupción.

---

> **Resumen ejecutivo:**  
> La ejecución intensiva de embeddings (`embed.py`) e inferencia local en WSL2 genera cargas sostenidas en el procesador del equipo anfitrión. Para prevenir sobrecalentamiento e inestabilidad del hardware sin degradar la lógica RAG, **Arquitectura_RAG_Termica** implementa un subsistema de supervisión térmica completamente desacoplado. Un servicio Flask en Windows (`export_temp_server.py`) expone la telemetría de `LibreHardwareMonitor` en el puerto `5005`, la cual es consumida en WSL2 por `thermal_watchdog.py`. Este calcula un promedio móvil y ejecuta detenciones preventivas atómicas (`pkill -f query.py` / `embed.py`) al alcanzar umbrales críticos.

---

## 1. Introducción

La ejecución del pipeline RAG puede generar una carga elevada sobre el procesador, especialmente durante tareas como:

* generación de embeddings y reconciliación vectorial (`embed.py`);
* extracción determinista de símbolos de código fuente (`symbols_extractor.py`);
* recuperación semántica y cálculo de similitud coseno (`query.py`);
* inferencia mediante modelos LLM ejecutados localmente en Ollama.

Con el objetivo de proteger el hardware utilizado durante el desarrollo, el proyecto incorpora una arquitectura de supervisión térmica completamente desacoplada del pipeline principal.

Esta arquitectura permite:

* obtener información real de los sensores del equipo;
* supervisar continuamente la temperatura del procesador;
* detectar condiciones térmicas críticas;
* registrar eventos relevantes del sistema en `thermal_watchdog_log.txt`;
* ejecutar acciones automáticas de protección cuando sea necesario.

La supervisión térmica constituye un subsistema independiente del pipeline RAG y mantiene el mismo funcionamiento independientemente del backend de inferencia seleccionado (LOCAL o CLOUD). De esta forma, la protección del hardware permanece activa tanto cuando la generación de respuestas se realiza mediante Ollama como cuando se utiliza OpenRouter.

---

## 2. Arquitectura de supervisión distribuida

La arquitectura térmica se encuentra estrictamente separada de la lógica de recuperación del conocimiento y de la generación de respuestas:

```text
                                HARDWARE FÍSICO (Windows Anfitrión)
                                                │
                                                ▼
                                      LibreHardwareMonitor
                                                │
                                                ▼
                                      export_temp_server.py
                       Ruta: E:\Developer\Tools\LibreHardwareMonitor\python
                                                │
                                                │ HTTP / JSON (:5005/data.json)
                                                ▼
                                     WSL2 Ubuntu (Terminal Linux)
                       Ruta: ~/rag_maui_docs_for_rag/scripts/thermal_watchdog.py
                                                │
                                       ┌────────┴────────┐
                                       ▼                 ▼
                                 Estado Normal     Estado Crítico
                                       │                 │
                                       ▼                 ▼
                                 Continúa RAG     Detiene query.py /
                                                  embed.py (pkill)
```

El watchdog se ejecuta como un proceso independiente en WSL2 y no forma parte del pipeline de código invocado por `query.py` o `embed.py`.

---

## 3. Componentes en el entorno Windows

### 3.1 LibreHardwareMonitor
LibreHardwareMonitor constituye la fuente primaria de información térmica utilizada por el sistema.

Responsabilidades:
* acceder a los sensores físicos del equipo;
* obtener la temperatura en tiempo real del procesador;
* publicar la información bruta mediante un servicio JSON interno (`http://localhost:8085/data.json`).

El pipeline en WSL2 no consulta directamente este endpoint complejo para evitar acoplamiento con la estructura interna del JSON de LibreHardwareMonitor.

---

## 4. Servicio `export_temp_server.py` (Windows)

### Ubicación exacta en disco:
```text
E:\Developer\Tools\LibreHardwareMonitor\python
```

### Objetivo
`export_temp_server.py` actúa como un microservicio adaptador entre LibreHardwareMonitor y WSL2.

```text
LibreHardwareMonitor (8085) ──> export_temp_server.py (Flask 5005) ──> /data.json ──> WSL2
```

### Responsabilidades
* consultar periódicamente el JSON completo de LibreHardwareMonitor;
* aislar el sensor correspondiente a la temperatura del procesador;
* convertir el valor a una carga JSON simplificada;
* publicar un servicio HTTP ligero mediante Flask en el puerto `5005`;
* escribir automáticamente el archivo `windows_ip.txt` con la IP anfitriona.

### Sensor procesado (Configuración típica)
La implementación obtiene la temperatura desde el árbol de sensores de la placa base/CPU:

```text
Nuvoton NCT6776F / Core Temperature
    └── Temperatures
            └── Temperature #1 (CPU Core Temp)
```

### Endpoint publicado
```text
http://IP_WINDOWS:5005/data.json
```

Ejemplo de respuesta JSON simplificada:
```json
{
    "id": 0,
    "Text": "CPU Temperature",
    "Value": 48.5,
    "Min": 38.0,
    "Max": 72.0
}
```

---

## 5. Descubrimiento automático de la IP de Windows

La dirección IP del host Windows puede variar entre reinicios o interfaces de red. Para evitar la modificación manual de scripts en WSL2, el sistema implementa un esquema de descubrimiento dinámico:

1. **Escritura Automática (Windows):** `export_temp_server.py` detecta la IP local de Windows y la escribe en:
   ```text
   E:\Developer\Tools\LibreHardwareMonitor\python\windows_ip.txt
   ```
   *(Ejemplo de contenido: `192.168.1.37`)*.

2. **Lectura y Fallback (WSL2):** Al iniciar `thermal_watchdog.py`:
   * intenta leer la IP desde el archivo compartido o variable de entorno;
   * si no está disponible, resuelve automáticamente la dirección mediante el gateway por defecto de WSL2 (`ip route | grep default`).

---

## 6. Thermal Watchdog (`thermal_watchdog.py` en WSL2)

### Ubicación exacta en disco:
```text
/home/manuelc/rag_maui_docs_for_rag/scripts/thermal_watchdog.py
```

### Objetivo
`thermal_watchdog.py` es el daemon en WSL2 responsable de supervisar continuamente la temperatura y aplicar acciones atómicas de protección.

Es completamente independiente de:
* `query.py` y `embed.py`;
* `logger.py`;
* `llm_backend.py`;
* Ollama local y OpenRouter cloud.

### Algoritmo de Promedio Móvil
Para evitar falsas interrupciones provocadas por picos térmicos instantáneos de corta duración, el watchdog utiliza una ventana de lectura móvil:

```python
WINDOW_SIZE = 5
```

Cada nueva lectura HTTP actualiza la cola circular y evalúa la media ponderada antes de modificar el estado térmico.

---

## 7. Umbrales térmicos y niveles de riesgo

La configuración vigente en `thermal_watchdog.py` establece las siguientes fronteras de operación:

| Parámetro | Valor Ponderado | Acción del Sistema |
| :--- | :---: | :--- |
| **`TEMP_NORMAL`** | $< 58.0\ ^\circ\text{C}$ | Operación normal. El pipeline RAG y los scripts de embeddings ejecutan sin restricción. |
| **`TEMP_WARNING`** | $\ge 58.0\ ^\circ\text{C}$ | Estado de advertencia. Se intensifica la frecuencia de muestreo y se registra la tendencia. |
| **`TEMP_CRITICAL`** | $\ge 62.0\ ^\circ\text{C}$ | **Estado crítico.** Se activa el protocolo de interrupción atómica sobre los procesos en WSL2. |
| **`TEMP_HARD_LIMIT`** | $\ge 70.0\ ^\circ\text{C}$ | **Límite duro.** Interrupción de emergencia inmediata de todo el entorno RAG en WSL2. |
| **`TEMP_RECOVERY`** | $< 58.0\ ^\circ\text{C}$ | Restablecimiento del estado. Se permite el reinicio de tareas tras verificar enfriamiento sostenido. |

---

## 8. Estados y acciones de protección

```text
[ NORMAL ]  ──( Temp >= 58°C )──>  [ WARNING ]  ──( Temp >= 62°C )──>  [ CRITICAL / HARD_LIMIT ]
    ▲                                                                               │
    │                                                                               ▼
    └─────────────────────── ( Temp < 58°C Sostenido ) ───────────────── Exec: pkill -f query.py
```

### Protocolo de Interrupción Atómica
Cuando el estado alcanza `CRITICAL` o `HARD_LIMIT`, el watchdog no solicita un apagado suave que pueda demorar durante un bucle de inferencia; en su lugar ejecuta:

```bash
pkill -f query.py
pkill -f embed.py
```

Esta acción libera inmediatamente el uso del CPU en WSL2, permitiendo que el sistema disipe calor antes de que intervenga el *thermal throttling* del hardware anfitrión.

---

## 9. Registro de auditoría térmica (`thermal_watchdog_log.txt`)

Todos los eventos térmicos, cambios de estado y ejecuciones de interrupción se registran de forma independiente en:

```text
thermal_watchdog_log.txt
```

*(Nota: Este archivo de log está excluido del control de versiones mediante `.gitignore`).*

Ejemplo de registro de evento crítico:

```text
============================================================
THERMAL WATCHDOG EVENT
Fecha: 2026-08-26 15:42:10
Estado: TEMP_CRITICAL
Temperatura Instantánea: 63.8 °C
Promedio Móvil (N=5): 62.4 °C
Endpoint Consultado: http://192.168.1.37:5005/data.json
Acción Ejecutada: pkill -f query.py (Proceso detenido preventivamente)
============================================================
```

---

## 10. Principios de diseño aplicados

1. **Separación de Responsabilidades:** `export_temp_server.py` extrae telemetría; `thermal_watchdog.py` evalúa métricas; `query.py` procesa RAG.
2. **Total Desacoplamiento:** Ningún script de RAG (`query.py`, `embed.py`, `llm_backend.py`) importa o depende de librerías térmicas.
3. **Resiliencia Operativa:** Si el servidor térmico en Windows no está activo, `thermal_watchdog.py` emite una advertencia en log sin bloquear la ejecución manual del usuario, permitiendo el uso bajo supervisión personal.
4. **Independencia del Backend:** Protege el CPU anfitrión por igual, ya sea que la inferencia se ejecute localmente con Ollama (`llama3.2:3b`) o mediante API cloud con OpenRouter.

---

## 11. Estado actual del subsistema térmico

Al **26 de agosto de 2026**, la protección térmica ofrece:
* **Microservicio en Windows:** `export_temp_server.py` operativo en `E:\Developer\Tools\LibreHardwareMonitor\python` expuesto en puerto `5005`.
* **Descubrimiento de IP:** Sincronización automática a través de `windows_ip.txt` (`192.168.1.37`).
* **Daemon en WSL2:** `thermal_watchdog.py` ubicado en `~/rag_maui_docs_for_rag/scripts/` con promediado de 5 muestras y límites de 58°C (Warning) / 62°C (Critical) / 70°C (Hard Limit).
* **Pruebas de Aborto Validadas:** Verificación de interrupción atómica (`pkill`) registrada en la suite de pruebas del proyecto (`2026-07-20_prueba02_backend_local_qwen2.5_abort_termico.md`).

