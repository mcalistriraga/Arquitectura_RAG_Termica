# Mantenimiento y Evolución del Sistema

## 1. Introducción

La arquitectura del proyecto fue diseñada siguiendo un enfoque modular, donde cada componente mantiene responsabilidades claramente definidas y un bajo nivel de acoplamiento.

El sistema integra procesamiento documental, recuperación semántica, modelos de lenguaje, supervisión térmica y mecanismos de registro, por lo que las tareas de mantenimiento abarcan tanto el entorno de ejecución como los componentes software que forman el pipeline RAG.

Los principales objetivos del mantenimiento son:

- conservar la estabilidad del entorno de ejecución;
- garantizar la disponibilidad de los servicios requeridos;
- mantener actualizados los modelos y dependencias;
- facilitar el diagnóstico mediante registros de ejecución;
- permitir la incorporación progresiva de nuevas funcionalidades sin afectar la arquitectura existente.

---

# 2. Organización actual del sistema

La arquitectura se distribuye entre dos entornos principales que colaboran entre sí.

## Windows

Ubicación de los componentes de supervisión térmica:

```text
E:\Developer\Tools\LibreHardwareMonitor\python
```

Responsabilidades principales:

- acceso a los sensores físicos del equipo;
- ejecución de LibreHardwareMonitor;
- publicación de la temperatura mediante Flask;
- generación del archivo de descubrimiento de IP para WSL2.

Arquitectura simplificada:

```text
LibreHardwareMonitor
        │
        ▼
export_temp_server.py
        │
        ▼
windows_ip.txt
```

---

## WSL2 Ubuntu

Ubicación del proyecto:

```text
/home/manuelc/rag_maui_docs_for_rag
```

Responsabilidades principales:

- ejecución del pipeline RAG;
- procesamiento documental;
- generación de embeddings;
- recuperación semántica;
- comunicación con el backend de inferencia;
- supervisión térmica;
- registro de consultas.

Arquitectura simplificada:

```text
ingest.py
      │
      ▼

output_raw.jsonl
      │
      ▼

embed.py
      │
      ▼

embeddings.jsonl

symbol_extractor.py
      │
      ▼

symbols.jsonl

      │
      ▼

query.py
      │
      ▼

llm_backend.py

      │
 ┌────┴─────┐
 ▼          ▼

LOCAL     CLOUD

Ollama   OpenRouter

logger.py

thermal_watchdog.py
```

Los componentes auxiliares (`logger.py` y `thermal_watchdog.py`) funcionan de manera desacoplada respecto al flujo principal de inferencia.

---

# 3. Mantenimiento operativo

## Inicio recomendado del sistema

Para garantizar el funcionamiento correcto del entorno se recomienda seguir el siguiente orden de ejecución.

---

### Paso 1

Iniciar LibreHardwareMonitor en Windows.

Verificar que los sensores se encuentren disponibles y que el archivo JSON pueda consultarse correctamente.

---

### Paso 2

Iniciar el servicio de exportación térmica:

```bat
start_server.bat
```

Comprobar posteriormente el endpoint:

```text
http://localhost:5005/data.json
```

Ejemplo de respuesta:

```json
{
  "Text": "CPU Temperature",
  "Value": 45.0
}
```

---

### Paso 3

Iniciar el watchdog térmico desde WSL2:

```bash
python3 thermal_watchdog.py
```

Salida esperada (ejemplo):

```text
🟢 Thermal Watchdog iniciado

🌡 CPU: 45.00°C | Estado: NORMAL
```

---

### Paso 4

Activar el entorno virtual de Python:

```bash
source venv_rag/bin/activate
```

---

### Paso 5

Iniciar el servicio de Ollama:

```bash
ollama serve
```

> **Nota:** Si Ollama ya se encuentra ejecutándose como servicio, este paso puede omitirse.

---

### Paso 6

Ejecutar el pipeline RAG:

```bash
python3 query.py
```

Durante el inicio de la aplicación el usuario selecciona:

- el modo de operación;
- el backend de inferencia (LOCAL o CLOUD);
- el modelo correspondiente, según la configuración de la sesión.

---

# 4. Mantenimiento de los datos RAG

La información utilizada durante la recuperación semántica se genera mediante un proceso de indexación documental.

Flujo general:

```text
Documentos

      │
      ▼

ingest.py

      │
      ▼

output_raw.jsonl

      │
      ├──────────────┐
      ▼              ▼

embed.py     symbol_extractor.py

      │              │
      ▼              ▼

embeddings.jsonl   symbols.jsonl
```

Cuando cambia la documentación o el código fuente del proyecto, se recomienda regenerar los índices correspondientes.

Entre las situaciones habituales se encuentran:

- incorporación de nuevos documentos;
- modificaciones relevantes del código fuente;
- cambios en la arquitectura del sistema;
- reorganización del proyecto;
- incorporación de nuevos módulos o funcionalidades.

Mantener actualizados estos archivos garantiza una recuperación documental coherente con el estado real del proyecto.

---

# 5. Mantenimiento de modelos y backends

La generación de respuestas se encuentra desacoplada del pipeline mediante `llm_backend.py`, permitiendo utilizar distintos proveedores de inferencia.

## Backend LOCAL

El backend local utiliza Ollama para ejecutar modelos instalados en el equipo.

Modelos actualmente configurados:

| Función | Modelo |
|----------|--------|
| Embeddings | `nomic-embed-text` |
| Depuración | `qwen2.5-coder:1.5b` |
| Arquitectura | `llama3.2:3b` |
| Documentación | `llama3.2:3b` |

Las actualizaciones de modelos deben evaluarse considerando aspectos como:

- memoria disponible;
- carga del procesador;
- temperatura alcanzada;
- velocidad de respuesta;
- calidad de las respuestas obtenidas.

En equipos con recursos limitados, un modelo de mayor tamaño no siempre representa una mejora práctica.

---

## Backend CLOUD

El backend cloud utiliza OpenRouter como proveedor de inferencia remota.

Su mantenimiento incluye, entre otros aspectos:

- verificar la disponibilidad de la API Key;
- comprobar la conectividad con el servicio;
- validar el modelo configurado para cada sesión;
- revisar posibles cambios en la configuración del proveedor.

La utilización de este backend permite mantener el mismo flujo RAG sin depender exclusivamente de la capacidad de procesamiento del hardware local.

---

## Evolución de los modelos

La incorporación de nuevos modelos debe realizarse procurando mantener la compatibilidad con la arquitectura existente.

Se recomienda evaluar previamente:

- calidad de las respuestas;
- consumo de recursos;
- compatibilidad con el hardware disponible;
- impacto sobre la temperatura del sistema;
- tiempo de respuesta durante las consultas.

La separación entre `query.py` y `llm_backend.py` facilita la incorporación de nuevos modelos o proveedores de inferencia con un impacto mínimo sobre el resto del sistema.

---
# 6. Diagnóstico y registros

La arquitectura incorpora mecanismos de registro que facilitan el análisis del comportamiento del sistema y el diagnóstico de incidencias.

## Registros de supervisión térmica

Generados por:

```text
thermal_watchdog.py
```

Estos registros permiten analizar información como:

- temperatura del procesador;
- promedio móvil utilizado para la toma de decisiones;
- estado térmico detectado;
- eventos críticos;
- acciones de protección ejecutadas.

La información queda almacenada en un archivo de registro para su posterior análisis.

---

## Registros del pipeline RAG

Generados por:

```text
logger.py
```

Durante cada consulta se registran eventos representativos del flujo de ejecución.

Ejemplo conceptual:

```text
SESSION_START

MODE_SELECTED

INPUT_RECEIVED

EMBEDDING_START

SEARCH_START

LLM_START

LLM_DONE

SESSION_END
```

Dependiendo de la configuración de la aplicación, los registros pueden incluir información adicional como:

- modo de operación seleccionado;
- backend utilizado;
- modelo empleado;
- tiempos de ejecución;
- temperatura registrada;
- eventos de interrupción.

Estos registros facilitan el análisis del rendimiento del sistema y la identificación de posibles cuellos de botella.

---

# 7. Copias de seguridad

Se recomienda realizar copias de seguridad periódicas de los componentes más importantes del proyecto.

## Código fuente

Directorio principal:

```text
scripts/
```

Incluye, entre otros:

- ingest.py
- chunk.py
- embed.py
- symbol_extractor.py
- query.py
- llm_backend.py
- logger.py
- thermal_watchdog.py

---

## Índices documentales

Archivos generados durante el procesamiento:

```text
embeddings.jsonl

symbols.jsonl
```

Estos archivos pueden regenerarse, pero conservar una copia evita repetir procesos de indexación cuando la documentación no ha cambiado.

---

## Documentación técnica

Directorio:

```text
docs/
```

Se recomienda mantener sincronizada la documentación con la evolución del código para evitar inconsistencias entre ambos.

---

## Configuración del entorno

Conviene conservar la configuración relacionada con:

- entorno virtual de Python;
- modelos instalados en Ollama;
- configuración del backend CLOUD;
- archivos de configuración (`.env`);
- scripts auxiliares utilizados durante el desarrollo.

---

# 8. Evolución prevista

La arquitectura actual fue diseñada para facilitar la incorporación gradual de nuevas capacidades.

Las siguientes mejoras representan posibles líneas de evolución y no forman parte de la implementación actual.

---

## Mayor observabilidad

Entre las posibles ampliaciones se encuentran:

- utilización del procesador;
- consumo de memoria RAM;
- carga del sistema;
- tiempos de respuesta;
- métricas de recuperación documental;
- métricas de inferencia.

---

## Supervisión térmica ampliada

Actualmente la supervisión se centra principalmente en la temperatura del procesador.

En futuras versiones podrían incorporarse otros indicadores como:

```text
CPU

 │

 ├── Temperatura

 ├── Utilización

 ├── Frecuencia

 └── Carga sostenida
```

---

## Gestión dinámica de modelos

Una posible evolución consiste en seleccionar automáticamente el backend o el modelo más adecuado según las condiciones del sistema.

Ejemplo conceptual:

```text
Carga baja
      │
      ▼
Modelo de mayor capacidad

Carga elevada
      │
      ▼
Modelo ligero o backend CLOUD
```

---

## Automatización del entorno

Entre las posibles mejoras futuras se encuentran:

- inicio automático de servicios;
- comprobación de dependencias;
- verificación del estado del entorno;
- administración automática de modelos;
- limpieza de recursos al finalizar una sesión.

---

## Herramientas de administración

Otra posible evolución consiste en desarrollar una interfaz que permita supervisar el estado general del sistema.

Ejemplo:

```text
Dashboard

Temperatura CPU

Estado del pipeline

Backend activo

Modelo utilizado

Consultas realizadas

Eventos registrados
```

---

# 9. Consideraciones para hardware limitado

La arquitectura fue desarrollada teniendo en cuenta las características del equipo utilizado durante el proyecto.

Por este motivo se adoptaron diversas estrategias orientadas a mejorar la estabilidad del sistema:

- utilización de modelos ligeros para ejecución local;
- separación entre Windows y WSL2;
- supervisión térmica desacoplada;
- registro detallado de eventos;
- posibilidad de utilizar un backend CLOUD para reducir la carga local.

Estas decisiones permitieron desarrollar y evaluar el sistema sin requerir hardware especializado para inteligencia artificial.

---

# 10. Estado actual del proyecto

En su estado actual, el proyecto dispone de una arquitectura funcional compuesta por:

```text
Pipeline RAG

        │

        ▼

Recuperación semántica

        │

        ▼

llm_backend.py

        │

 ┌──────┴──────┐

 ▼             ▼

LOCAL       CLOUD

        │

        ▼

Supervisión térmica

        │

        ▼

Registro de ejecución
```

La arquitectura continúa en evolución y sirve como plataforma experimental para el estudio de técnicas de recuperación documental, inferencia con modelos de lenguaje y supervisión de recursos en hardware limitado.

---

# 11. Conclusión

La organización modular del proyecto facilita el mantenimiento y la evolución de cada uno de sus componentes de forma independiente.

La separación entre el procesamiento documental, la recuperación semántica, la inferencia mediante modelos de lenguaje y la supervisión térmica permite incorporar mejoras progresivas sin modificar la estructura general del sistema.

En conjunto, la arquitectura proporciona una base sólida para continuar experimentando con soluciones RAG locales e híbridas, manteniendo la coherencia entre la implementación, la documentación técnica y los objetivos de investigación del proyecto.

