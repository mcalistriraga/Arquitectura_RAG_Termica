# Pruebas y Validación del Sistema

## 1. Introducción

Durante el desarrollo del proyecto se realizaron pruebas progresivas para validar cada capa de la arquitectura.

La estrategia utilizada fue validar los componentes de forma independiente antes de integrarlos:

```text
Hardware
   |
   v
LibreHardwareMonitor
   |
   v
export_temp_server.py
   |
   v
thermal_watchdog.py
   |
   v
query.py
   |
   v
RAG + Ollama
```

El objetivo fue garantizar que el sistema completo funcionara de forma estable en un equipo con recursos limitados.

---

# 2. Entorno de pruebas

## Hardware utilizado

Características principales:

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

## Software principal

| Componente | Tecnología |
|-|-|
| Monitoreo hardware | LibreHardwareMonitor |
| Servicio térmico | Flask + Python |
| IA local | Ollama |
| LLM | llama3.2:3b |
| Embeddings | nomic-embed-text |
| RAG | Python |
| Supervisión | thermal_watchdog.py |

---

# 3. Validación de LibreHardwareMonitor

## Objetivo

Confirmar que el sistema podía obtener información real del sensor térmico del procesador.

---

## Prueba realizada

Consulta directa:

```text
http://localhost:8085/data.json
```

Resultado esperado:

```json
{
 "Text":"Temperature #1",
 "Value":"45 °C"
}
```

---

## Resultado

Validado.

El sensor utilizado corresponde al árbol:

```text
Nuvoton NCT6776F

    |
    +-- Temperatures

            |
            +-- Temperature #1
```

---

# 4. Validación de export_temp_server.py

## Objetivo

Verificar la transformación del JSON de LibreHardwareMonitor en una API simplificada.

---

## Ejecución

Ubicación:

```text
E:\Developer\Tools\LibreHardwareMonitor\python
```

Inicio:

```bat
start_server.bat
```

---

## Endpoint generado

```text
http://localhost:5005/data.json
```

---

## Resultado obtenido

Ejemplo:

```json
{
 "Max":100,
 "Min":0,
 "Text":"CPU Temperature",
 "Value":44.0,
 "id":0,
 "timestamp":1784056081
}
```

---

## Resultado

Validado.

El servicio entrega únicamente la información necesaria para supervisión.

---

# 5. Validación comunicación Windows - WSL2

## Objetivo

Comprobar que WSL puede consultar el servicio térmico publicado en Windows.

---

## Prueba realizada desde WSL

Comando:

```bash
curl http://192.168.1.36:5005/data.json
```

---

## Resultado obtenido

```json
{
 "Text":"CPU Temperature",
 "Value":45.0
}
```

---

## Resultado

Comunicación validada.

El mecanismo utilizado es:

```text
Windows
    |
    v
windows_ip.txt
    |
    v
WSL
```

---

# 6. Validación thermal_watchdog.py

## Objetivo

Comprobar la supervisión continua de temperatura.

---

## Ejecución

Desde WSL:

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
🌡 CPU:45.00°C | Avg(5):44.80°C | Estado:NORMAL
```

---

## Resultado

Validado.

El watchdog:

* obtiene temperatura,
* calcula promedio móvil,
* clasifica estado,
* mantiene supervisión continua.

---

# 7. Validación del pipeline RAG

## Objetivo

Confirmar la ejecución completa del flujo:

```text
Pregunta
 |
 v
Embedding
 |
 v
Búsqueda semántica
 |
 v
Contexto
 |
 v
Ollama
 |
 v
Respuesta
```

---

## Componentes probados

### Embeddings

Archivo generado:

```text
embeddings.jsonl
```

Validación:

```text
Embeddings cargados correctamente
```

---

### Consulta

Ejecutado:

```bash
python3 query.py
```

---

## Modos probados

### DEPURACIÓN

Modelo:

```text
qwen2.5-coder:1.5b
```

Uso:

```text
Análisis de errores C#
```

---

### ARQUITECTURA

Modelo:

```text
llama3.2:3b
```

Uso:

```text
Análisis del sistema
```

---

### DOCUMENTACIÓN

Modelo:

```text
llama3.2:3b
```

Uso:

```text
Generación documental
```

---

# 8. Validación control térmico durante cargas altas

## Objetivo

Evaluar comportamiento térmico durante procesos intensivos.

---

## Prueba realizada

Proceso:

```text
Generación de embeddings
```

---

## Observación

Durante cargas elevadas:

```text
CPU cercana al 100%
```

se observó aumento de temperatura.

Ejemplo:

```text
Temperatura aproximada:
70 °C
```

---

## Acción tomada

Se incorporaron:

* control de carga,
* pausas configurables,
* supervisión térmica,
* mecanismo de abortado.

---

# 9. Validación logger.py

## Objetivo

Registrar el comportamiento interno de las consultas RAG.

---

## Información registrada

Ejemplo:

```text
SESSION_START

MODE_SELECTED

INPUT_RECEIVED

EMBEDDING_START

SEARCH_START

LLM_START

LLM_DONE
```

Incluyendo:

```text
Tiempo transcurrido
Temperatura
Estado térmico
Modo seleccionado
```

---

# 10. Problemas encontrados y soluciones

## Problema: acceso térmico desde WSL

### Situación inicial

WSL no podía acceder directamente al endpoint local de Windows.

---

### Solución

Implementación:

```text
windows_ip.txt
```

y descubrimiento automático.

---

## Problema: detección incorrecta del sensor

### Situación inicial

El JSON de LibreHardwareMonitor contiene muchos sensores.

---

### Solución

Búsqueda específica:

```text
Nuvoton NCT6776F
    |
    Temperature #1
```

---

## Problema: consumo excesivo durante embeddings

### Situación inicial

La generación masiva de embeddings elevaba considerablemente la temperatura.

---

### Solución

Implementación de:

* control de carga,
* pausas,
* watchdog térmico.

---

# 11. Estado actual de validación

Actualmente están validados:

| Componente | Estado |
|-|-|
| LibreHardwareMonitor | OK |
| export_temp_server.py | OK |
| Comunicación Windows-WSL | OK |
| thermal_watchdog.py | OK |
| Ollama | OK |
| Embeddings | OK |
| Consulta RAG | OK |
| Protección térmica | OK |
| Logger | OK |

---

# 12. Conclusión

Las pruebas realizadas demuestran que la arquitectura completa puede ejecutar un sistema RAG local con modelos LLM, incorporando supervisión térmica y mecanismos automáticos de protección.

El sistema actualmente permite experimentar con inteligencia artificial local manteniendo control sobre:

* datos,
* modelos,
* recursos computacionales,
* estabilidad térmica.
