# Mantenimiento y Evolución del Sistema

## 1. Introducción

La arquitectura RAG local con supervisión térmica fue diseñada como un sistema experimental pero estructurado, donde cada componente mantiene responsabilidades independientes.

Debido a que integra inteligencia artificial local, monitoreo de hardware y automatización de procesos, el mantenimiento debe considerar tanto la capa de software como la capa de infraestructura.

Los principales objetivos del mantenimiento son:

* conservar la estabilidad del entorno,
* garantizar la disponibilidad de los servicios,
* mantener actualizados los modelos y dependencias,
* preservar la capacidad de diagnóstico,
* permitir la incorporación progresiva de nuevas funcionalidades.

---

# 2. Organización actual del sistema

La arquitectura está distribuida en dos ambientes principales.

## Windows

Ubicación:

```text
E:\Developer\Tools\LibreHardwareMonitor\python
```

Responsabilidades:

* acceso a sensores físicos,
* ejecución de LibreHardwareMonitor,
* publicación de temperatura mediante Flask,
* generación del archivo de descubrimiento de IP.

Componentes principales:

```text
LibreHardwareMonitor
        |
        v
export_temp_server.py
        |
        v
windows_ip.txt
```

---

## WSL2 Ubuntu

Ubicación:

```text
/home/manuelc/rag_maui_docs_for_rag/scripts
```

Responsabilidades:

* ejecución del pipeline RAG,
* interacción con Ollama,
* generación de embeddings,
* consulta semántica,
* supervisión térmica.

Componentes principales:

```text
ingest.py
    |
    v
embed.py
    |
    v
embeddings.jsonl
    |
    v
query.py

thermal_watchdog.py
logger.py
```

---

# 3. Mantenimiento operativo

## 3.1 Inicio normal del sistema

El orden recomendado de ejecución es:

### Paso 1

Iniciar LibreHardwareMonitor en Windows.

Verificar que los sensores estén disponibles.

---

### Paso 2

Iniciar el servicio térmico:

```bat
start_server.bat
```

Validar:

```text
http://localhost:5005/data.json
```

Ejemplo esperado:

```json
{
 "Text":"CPU Temperature",
 "Value":45.0
}
```

---

### Paso 3

Iniciar watchdog en WSL:

```bash
python3 thermal_watchdog.py
```

Salida esperada:

```text
🟢 Thermal Watchdog iniciado
🌡 CPU: 45.00°C | Estado: NORMAL
```

---

### Paso 4

Ejecutar consultas RAG:

```bash
python3 query.py
```

---

# 4. Mantenimiento de datos RAG

La base de conocimiento se genera mediante el siguiente flujo:

```text
Código / Documentos
        |
        v
ingest.py
        |
        v
output_raw.jsonl
        |
        v
embed.py
        |
        v
embeddings.jsonl
```

Cuando cambia la información documental se recomienda regenerar los embeddings.

Ejemplos:

* cambios importantes en el proyecto MAUI,
* nuevos documentos técnicos,
* actualización de arquitectura,
* incorporación de nuevos módulos.

---

# 5. Mantenimiento de modelos

El sistema utiliza modelos locales mediante Ollama.

Modelos actuales:

## Modelo de embeddings

```text
nomic-embed-text
```

Responsabilidad:

* representación vectorial del conocimiento.

---

## Modelo de lenguaje

```text
llama3.2:3b
```

Responsabilidad:

* generación de respuestas,
* análisis arquitectónico,
* asistencia técnica.

---

## Modelo especializado

```text
qwen2.5-coder:1.5b
```

Responsabilidad:

* apoyo en depuración de código.

---

Las actualizaciones de modelos deben evaluarse considerando:

* memoria disponible,
* temperatura generada,
* velocidad de respuesta,
* calidad de resultados.

En hardware limitado, un modelo más grande no siempre representa una mejora práctica.

---

# 6. Diagnóstico y registros

El sistema incorpora mecanismos de observabilidad.

## Logs térmicos

Generados por:

```text
thermal_watchdog.py
```

Permiten analizar:

* temperatura alcanzada,
* motivo de protección,
* eventos críticos,
* acciones ejecutadas.

---

## Logs de consulta RAG

Generados por:

```text
logger.py
```

Registran:

* inicio de sesión,
* modo seleccionado,
* modelo utilizado,
* etapas del procesamiento,
* tiempos de ejecución,
* temperatura durante la consulta.

Ejemplo conceptual:

```text
SESSION_START

MODE_SELECTED=ARCH

EMBEDDING_START

SEARCH_DONE

LLM_START

LLM_DONE
```

Estos registros permiten identificar cuellos de botella durante una consulta.

---

# 7. Copias de seguridad

Se recomienda conservar:

## Código fuente

```text
scripts/
```

Incluye:

* ingest.py
* embed.py
* query.py
* thermal_watchdog.py
* logger.py

---

## Base documental

```text
embeddings.jsonl
symbols.jsonl
```

---

## Documentación

```text
Arquitectura_RAG_Termica/docs
```

---

## Configuración Ollama

Registrar:

* modelos instalados,
* versiones,
* parámetros utilizados.

---

# 8. Posibles mejoras futuras

La arquitectura actual permite evolucionar hacia nuevas capacidades.

---

## 8.1 Mayor observabilidad

Incorporar:

* uso de CPU,
* uso de memoria RAM,
* consumo energético,
* carga del sistema,
* tiempo de respuesta del modelo.

---

## 8.2 Supervisión avanzada

Actualmente la protección se basa principalmente en temperatura CPU.

Posibles extensiones:

```text
CPU
 |
 +-- Temperatura
 |
 +-- Uso %
 |
 +-- Frecuencia
 |
 +-- Carga sostenida
```

---

## 8.3 Gestión inteligente de modelos

Futuras versiones podrían seleccionar modelos automáticamente:

Ejemplo:

```text
Temperatura baja
        |
        v
Modelo grande

Temperatura alta
        |
        v
Modelo reducido
```

---

## 8.4 Integración con Ollama

Posibles mejoras:

* iniciar/detener modelos automáticamente,
* liberar memoria después de consultas,
* seleccionar modelos según tarea,
* limitar concurrencia.

---

## 8.5 Interfaz de administración

La arquitectura podría evolucionar hacia un panel de control:

```text
Dashboard

Temperatura CPU
Estado RAG
Modelo activo
Consultas realizadas
Eventos térmicos
```

---

# 9. Consideraciones para hardware limitado

El diseño actual considera las restricciones del equipo utilizado.

Por esta razón se aplican estrategias como:

* modelos pequeños,
* ejecución local,
* control térmico,
* separación Windows / WSL2,
* registro de eventos,
* supervisión automática.

El objetivo no es solamente obtener respuestas mediante IA, sino construir un entorno estable y controlado.

---

# 10. Estado de evolución del proyecto

La arquitectura actual representa una primera versión funcional:

```text
RAG local
        +
LLM local
        +
Supervisión térmica
        +
Protección automática
```

Las próximas etapas pueden orientarse hacia:

* mayor automatización,
* mejor observabilidad,
* integración con nuevos sensores,
* optimización del rendimiento,
* publicación como proyecto técnico demostrativo.

---

# 11. Conclusión

El sistema construido demuestra que es posible integrar inteligencia artificial local, recuperación documental y mecanismos de protección del hardware mediante una arquitectura modular.

La separación de responsabilidades permite mantener el sistema comprensible, extensible y adaptable a diferentes escenarios de ejecución local de modelos de lenguaje.

