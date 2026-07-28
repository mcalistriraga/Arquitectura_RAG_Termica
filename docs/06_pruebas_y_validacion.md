# Pruebas y Validación del Sistema

## 1. Introducción

Durante el desarrollo del proyecto se realizaron pruebas progresivas para validar cada uno de los componentes que forman la arquitectura del sistema.

La estrategia seguida consistió en verificar cada componente de manera independiente antes de integrarlo con el resto del pipeline.

```text
Hardware

    │
    ▼

LibreHardwareMonitor

    │
    ▼

export_temp_server.py

    │
    ▼

thermal_watchdog.py

    │
    ▼

query.py

    │
    ▼

llm_backend.py

    │
    ▼

Backend de inferencia

(LOCAL o CLOUD)
```

Este enfoque permitió aislar posibles incidencias, facilitar el proceso de depuración y validar progresivamente el funcionamiento del sistema sobre un equipo con recursos limitados.

La mayor parte de las pruebas de integración se realizaron utilizando el backend **LOCAL (Ollama)**, ya que fue el primer entorno de inferencia implementado durante el desarrollo del proyecto.

---

# 2. Entorno de pruebas

## Hardware utilizado

Las pruebas fueron realizadas sobre el equipo principal de desarrollo.

Características relevantes:

```text
CPU:
AMD FX-6300 Six-Core

RAM:
16 GB

GPU:
Sin aceleración dedicada para IA

Sistema operativo:
Windows 10 Pro

Entorno IA:
WSL2 Ubuntu
```

---

## Software utilizado

| Componente | Tecnología |
|------------|------------|
| Monitorización del hardware | LibreHardwareMonitor |
| Servicio de adaptación térmica | Flask + Python |
| Pipeline RAG | Python |
| Backend LOCAL | Ollama |
| Backend CLOUD | OpenRouter |
| Modelo de embeddings | nomic-embed-text |
| Supervisión térmica | thermal_watchdog.py |

No todas las pruebas utilizaron ambos backends de inferencia; la mayoría fueron realizadas sobre el backend LOCAL.

---

# 3. Validación de LibreHardwareMonitor

## Objetivo

Confirmar que el sistema podía acceder correctamente a la información proporcionada por los sensores térmicos del equipo.

---

## Prueba realizada

Consulta directa al servicio de LibreHardwareMonitor:

```text
http://localhost:8085/data.json
```

Resultado esperado (ejemplo simplificado):

```json
{
  "Text": "Temperature #1",
  "Value": "45 °C"
}
```

---

## Resultado

Validado.

Se comprobó que el sensor utilizado corresponde al árbol:

```text
Nuvoton NCT6776F

        │
        └── Temperatures

                │
                └── Temperature #1
```

Este sensor fue posteriormente utilizado por el resto de la arquitectura de supervisión térmica.

---

# 4. Validación de export_temp_server.py

## Objetivo

Verificar la transformación de la información generada por LibreHardwareMonitor en una API simplificada accesible desde WSL2.

---

## Ejecución

Ubicación del proyecto:

```text
E:\Developer\Tools\LibreHardwareMonitor\python
```

Inicio del servicio:

```bat
start_server.bat
```

---

## Endpoint publicado

```text
http://localhost:5005/data.json
```

---

## Resultado obtenido

Ejemplo:

```json
{
  "id": 0,
  "Text": "CPU Temperature",
  "Value": 44.0,
  "Min": 0,
  "Max": 100,
  "timestamp": 1784056081
}
```

---

## Resultado

Validado.

El servicio publica únicamente la información necesaria para la supervisión térmica, evitando exponer la estructura completa generada por LibreHardwareMonitor.

---

# 5. Validación de la comunicación Windows ↔ WSL2

## Objetivo

Comprobar que el entorno Linux podía acceder correctamente al servicio HTTP publicado desde Windows.

---

## Prueba realizada desde WSL2

Comando ejecutado:

```bash
curl http://192.168.1.36:5005/data.json
```

---

## Resultado obtenido

Ejemplo:

```json
{
  "Text": "CPU Temperature",
  "Value": 45.0
}
```

---

## Resultado

Comunicación validada.

La resolución de la dirección IP se realiza mediante el mecanismo implementado con:

```text
Windows

      │

      ▼

windows_ip.txt

      │

      ▼

WSL2
```

Este mecanismo evita depender de direcciones IP configuradas manualmente.

---

# 6. Validación de thermal_watchdog.py

## Objetivo

Comprobar el funcionamiento continuo del sistema de supervisión térmica.

---

## Ejecución

Desde WSL2:

```bash
python3 thermal_watchdog.py
```

---

## Resultado obtenido

Ejemplo:

```text
📖 IP Windows detectada desde archivo:
192.168.1.36

🟢 Thermal Watchdog iniciado

🌐 Endpoint:
http://192.168.1.36:5005/data.json

🌡 CPU: 45.00°C | Avg(1):45.00°C | Estado:NORMAL
🌡 CPU: 45.00°C | Avg(5):44.80°C | Estado:NORMAL
```

---

## Resultado

Validado.

Se comprobó que el watchdog:

- obtiene periódicamente la temperatura del procesador;
- calcula el promedio móvil configurado;
- clasifica el estado térmico;
- mantiene la supervisión de forma continua;
- registra eventos cuando corresponde.

---

# 7. Validación del pipeline RAG

## Objetivo

Verificar el funcionamiento del flujo general de una consulta dentro del pipeline RAG.

El proceso validado puede resumirse como:

```text
Consulta

     │
     ▼

Embedding

     │
     ▼

Recuperación semántica

     │
     ▼

Preparación del contexto

     │
     ▼

llm_backend.py

     │
     ▼

Backend seleccionado

     │
     ▼

Respuesta
```

---

## Componentes validados

### Generación de embeddings

Archivo generado:

```text
embeddings.jsonl
```

Resultado observado:

```text
Embeddings cargados correctamente
```

---

### Ejecución de consultas

Comando utilizado:

```bash
python3 query.py
```

---

## Modos evaluados

### DEPURACIÓN

Modelo utilizado:

```text
qwen2.5-coder:1.5b
```

Objetivo:

- análisis de errores de compilación;
- revisión de código C#;
- asistencia durante el desarrollo.

---

### ARQUITECTURA

Modelo utilizado:

```text
llama3.2:3b
```

Objetivo:

- análisis de la arquitectura del sistema;
- comprensión de relaciones entre componentes.

---

### DOCUMENTACIÓN

Modelo utilizado:

```text
llama3.2:3b
```

Objetivo:

- explicación funcional del proyecto;
- generación de documentación técnica.

---
# 8. Validación del comportamiento térmico

## Objetivo

Evaluar el comportamiento térmico del equipo durante la ejecución de tareas con alta carga de procesamiento.

---

## Pruebas realizadas

Se realizaron pruebas principalmente durante:

- generación masiva de embeddings;
- consultas RAG con modelos locales;
- ejecución continuada del pipeline.

---

## Observaciones

Durante las tareas más intensivas se observaron:

```text
Uso elevado del procesador
(próximo al 100 %)
```

acompañado por un incremento significativo de la temperatura.

En algunas pruebas se registraron temperaturas cercanas a:

```text
70 °C
```

Estos resultados confirmaron la necesidad de incorporar mecanismos de protección para preservar la estabilidad del sistema durante ejecuciones prolongadas.

---

## Medidas implementadas

Como resultado de las pruebas se incorporaron diferentes mecanismos de protección, entre ellos:

- control de carga durante la generación de embeddings;
- pausas configurables entre operaciones intensivas;
- supervisión térmica continua;
- detención automática del proceso cuando se alcanzan condiciones críticas.

---

# 9. Validación de logger.py

## Objetivo

Verificar el registro cronológico de las operaciones realizadas durante la ejecución del pipeline.

---

## Eventos registrados

Entre los eventos observados durante las pruebas se encuentran:

```text
SESSION_START
MODE_SELECTED
INPUT_RECEIVED
EMBEDDING_START
EMBEDDING_OK
SEARCH_START
SEARCH_DONE
LLM_START
LLM_DONE
SESSION_END
```

Además del flujo de ejecución, el registro incorpora información como:

- tiempo transcurrido;
- temperatura del sistema;
- estado térmico;
- modo de operación seleccionado;
- backend utilizado (cuando corresponde).

---

## Resultado

Validado.

El registro generado facilita el análisis posterior de incidencias y el seguimiento del comportamiento del sistema durante las pruebas.

---

# 10. Problemas encontrados y soluciones

## Problema: acceso al servicio térmico desde WSL2

### Situación inicial

El entorno WSL2 no podía acceder directamente al servicio publicado en Windows utilizando `localhost`.

---

### Solución

Se implementó un mecanismo de descubrimiento basado en:

```text
windows_ip.txt
```

con respaldo mediante la detección automática del gateway de WSL2.

---

## Problema: identificación del sensor térmico

### Situación inicial

El archivo JSON generado por LibreHardwareMonitor contiene una gran cantidad de sensores, muchos de ellos no relacionados con la temperatura del procesador.

---

### Solución

Se implementó una búsqueda específica del sensor correspondiente a:

```text
Nuvoton NCT6776F

        │

        ▼

Temperature #1
```

garantizando la utilización del mismo sensor en todas las pruebas.

---

## Problema: carga elevada durante la generación de embeddings

### Situación inicial

La generación masiva de embeddings produjo un incremento considerable del uso del procesador y de la temperatura del sistema.

---

### Solución

Se incorporaron progresivamente:

- control de carga;
- pausas configurables;
- supervisión térmica continua;
- watchdog de protección.

Estas medidas permitieron mejorar la estabilidad del entorno durante ejecuciones prolongadas.

---

# 11. Estado actual de validación

Hasta el momento se han validado satisfactoriamente los siguientes componentes:

| Componente | Estado |
|------------|:------:|
| LibreHardwareMonitor | ✅ |
| export_temp_server.py | ✅ |
| Comunicación Windows ↔ WSL2 | ✅ |
| thermal_watchdog.py | ✅ |
| logger.py | ✅ |
| Generación de embeddings | ✅ |
| Recuperación documental | ✅ |
| Pipeline RAG | ✅ |
| Backend LOCAL (Ollama) | ✅ |
| Protección térmica | ✅ |

La arquitectura incorpora además soporte para un backend CLOUD mediante OpenRouter, cuya integración forma parte de la evolución del sistema.

---

# 12. Conclusión

Las pruebas realizadas permitieron validar progresivamente la arquitectura implementada, verificando tanto los componentes individuales como su funcionamiento integrado.

En particular, se comprobó el correcto funcionamiento de:

- la ingestión documental;
- la generación de embeddings;
- la recuperación semántica;
- el pipeline RAG;
- la supervisión térmica;
- el registro de eventos durante la ejecución.

Las pruebas también permitieron identificar limitaciones derivadas del hardware disponible, motivando la incorporación de mecanismos específicos de protección térmica y la posterior evolución hacia una arquitectura con soporte para distintos backends de inferencia.

En su estado actual, el proyecto constituye una plataforma experimental estable para el desarrollo y evaluación de arquitecturas RAG, manteniendo un equilibrio entre capacidad de experimentación, protección del hardware y coherencia entre la implementación y la documentación técnica.
