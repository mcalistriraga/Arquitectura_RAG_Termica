# Arquitectura del Sistema

## 1. Introducción

La arquitectura del proyecto está basada en un modelo híbrido compuesto por dos entornos complementarios:

- **Windows**, encargado de la interacción con el hardware físico, la adquisición de información de sensores y la publicación de los datos térmicos necesarios para la supervisión del sistema.
- **WSL2 Ubuntu**, encargado de la ejecución del entorno de inteligencia artificial local, incluyendo el pipeline RAG, los modelos LLM y los mecanismos de protección térmica.

Esta separación permite aprovechar las fortalezas de cada plataforma:

- Windows mantiene el acceso directo al hardware mediante LibreHardwareMonitor.
- WSL2 proporciona un entorno Linux adecuado para la ejecución de modelos de inteligencia artificial, automatización y procesamiento documental.

La comunicación entre ambos entornos se realiza mediante un servicio HTTP ligero y un mecanismo automático de descubrimiento de la dirección IP del sistema Windows.

---

# 2. Vista general de la arquitectura

```text
                     ARQUITECTURA HÍBRIDA
                        WINDOWS + WSL2



                         EQUIPO FÍSICO
                               |
               +---------------+---------------+
               |                               |
               v                               v

            WINDOWS                      WSL2 UBUNTU
               |                               |
               |                               |
               v                               v
  LibreHardwareMonitor                    Ollama
               |                               |
               v                               v
   export_temp_server.py                Modelos LLM
        (Flask API)                     (llama3.2:3b)
               |                               |
               |                               |
               +----------- HTTP JSON ---------+
                           (Endpoint)
                               |
                               v
                    thermal_watchdog.py
                    (Supervisión térmica)
                               |
                  consulta temperatura CPU
                               |
                  +------------+------------+
                  |                         |
                  |                         |
          Estado NORMAL            Estado CRÍTICO
                  |                         |
                  |                   aborta ejecución
                  |                         |
                  +------------+------------+
                               |
                               v
                           query.py
                      (Pipeline RAG Local)
                               |
                               v
                          Respuesta IA
```

La supervisión térmica funciona como un servicio independiente que observa continuamente el estado del sistema y protege los procesos de inteligencia artificial cuando las condiciones térmicas lo requieren.

---

# 3. Distribución de componentes

## 3.1 Componentes Windows

### Ubicación

```text
E:\Developer\Tools\LibreHardwareMonitor\python
```

Este directorio contiene los componentes responsables de la adquisición y publicación de la información térmica del sistema.

---

### LibreHardwareMonitor

Aplicación encargada de acceder directamente a los sensores físicos del equipo.

Responsabilidades:

- detectar sensores disponibles;
- obtener la temperatura del procesador;
- exponer la información mediante un endpoint JSON.

---

### export_temp_server.py

Servicio intermedio encargado de transformar la información obtenida desde LibreHardwareMonitor en una API simplificada consumible desde WSL2.

Responsabilidades:

- consultar el endpoint JSON de LibreHardwareMonitor;
- localizar el sensor específico de temperatura del CPU;
- convertir el valor obtenido a formato numérico;
- publicar una API REST mediante Flask;
- generar automáticamente el archivo `windows_ip.txt`.

Endpoint publicado:

```text
http://IP_WINDOWS:5005/data.json
```

Ejemplo de respuesta:

```json
{
    "Text": "CPU Temperature",
    "Value": 45.0
}
```

---

### windows_ip.txt

Archivo generado automáticamente por `export_temp_server.py`.

Permite que los procesos ejecutados en WSL2 conozcan la dirección IP actual del sistema Windows.

Ejemplo:

```text
192.168.1.36
```

Este mecanismo evita la configuración manual de la dirección IP y facilita la comunicación entre ambos entornos.

---

### start_server.bat

Script encargado de iniciar el servicio térmico.

```text
Inicia export_temp_server.py
```

---

### stop_server.bat

Script encargado de detener el servicio térmico.

```text
Finaliza export_temp_server.py
```

---

# 4. Componentes WSL2 Ubuntu

## Ubicación

```text
/home/manuelc/rag_maui_docs_for_rag/scripts
```

Este directorio contiene los componentes principales del sistema RAG y de supervisión térmica.

---

## 4.1 Pipeline RAG

El pipeline documental está compuesto por varias etapas consecutivas.

```text
Documentos del proyecto
          |
          v
       ingest.py
          |
          v
    output_raw.jsonl
          |
          v
       chunk.py
          |
          v
        chunks
          |
          v
       embed.py
          |
          v
   embeddings.jsonl
```

---

### ingest.py

Responsable de la extracción inicial de la información documental.

Funciones:

- recorrer el proyecto fuente;
- identificar archivos compatibles;
- clasificar componentes por capa;
- generar un conjunto de datos estructurado.

Entrada:

```text
Proyecto fuente
```

Salida:

```text
output_raw.jsonl
```

---

### chunk.py

Responsable de dividir la información en fragmentos adecuados para la generación de embeddings.

Objetivos:

- mejorar la recuperación semántica;
- reducir el tamaño del contexto;
- mantener coherencia documental.

Salida:

```text
chunks/
```

---

### embed.py

Genera los embeddings utilizando el modelo:

```text
nomic-embed-text
```

Resultado:

```text
embeddings.jsonl
```

---

### symbol_extractor.py

Componente encargado del análisis estructural del código fuente.

Extrae:

- clases;
- propiedades;
- métodos;
- ViewModels.

Genera:

```text
symbols.jsonl
```

Este archivo complementa la recuperación semántica con información arquitectónica del proyecto.

---

### query.py

Componente principal del sistema RAG.

Responsabilidades:

- recibir preguntas del usuario;
- generar embeddings de consulta;
- recuperar contexto documental;
- incorporar contexto arquitectónico;
- seleccionar el modelo LLM adecuado;
- generar la respuesta final.

Archivos utilizados:

```text
embeddings.jsonl
symbols.jsonl
```

Flujo:

```text
Pregunta usuario
       |
       v
Embedding consulta
       |
       v
Búsqueda semántica
       |
       +--------------------+
       |                    |
       v                    v
Contexto documental   Contexto arquitectónico
       \                    /
        \                  /
         +----------------+
                 |
                 v
             Ollama
                 |
                 v
            Respuesta
```

---

## 4.2 Modelos locales

El sistema utiliza modelos ejecutados localmente mediante Ollama.

| Modelo | Propósito |
|---------|-----------|
| llama3.2:3b | Consultas generales y arquitectura |
| qwen2.5-coder:1.5b | Apoyo en depuración de código |
| nomic-embed-text | Generación de embeddings |

---

## 4.3 Supervisión térmica

### thermal_watchdog.py

Proceso independiente encargado de supervisar continuamente las condiciones térmicas del equipo.

No forma parte del pipeline RAG, sino que constituye una capa externa de protección.

Responsabilidades:

- consultar periódicamente la temperatura del CPU;
- consumir el servicio HTTP publicado por Windows;
- calcular un promedio móvil de temperatura;
- clasificar el estado térmico del sistema;
- registrar eventos de supervisión;
- detener automáticamente la ejecución de `query.py` cuando se supera el umbral configurado.

---

# 5. Comunicación entre Windows y WSL2

La comunicación entre ambos entornos utiliza dos mecanismos complementarios.

## 5.1 Servicio HTTP

Windows publica:

```text
http://IP_WINDOWS:5005/data.json
```

WSL2 consume este servicio mediante:

```python
requests.get(URL)
```

Ejemplo:

```json
{
    "Text": "CPU Temperature",
    "Value": 45.0
}
```

---

## 5.2 Descubrimiento automático de IP

Para evitar la configuración manual de la dirección IP, Windows genera automáticamente:

```text
windows_ip.txt
```

WSL2 utiliza:

```python
load_windows_ip()
```

Proceso:

```text
windows_ip.txt
        |
        v
thermal_watchdog.py
        |
        v
http://IP_WINDOWS:5005/data.json
```

Si el archivo no existe, el sistema utiliza como mecanismo de respaldo el gateway de WSL2.

---

# 6. Flujo completo de operación

## Paso 1 – Inicio del servicio térmico

En Windows:

```bat
start_server.bat
```

Resultado:

```text
LibreHardwareMonitor
        |
        v
export_temp_server.py
        |
        v
API Flask disponible
```

---

## Paso 2 – Inicio del watchdog

En WSL2:

```bash
python3 thermal_watchdog.py
```

Resultado:

```text
Watchdog activo
        |
        v
Supervisión continua del CPU
```

---

## Paso 3 – Ejecución del sistema RAG

En WSL2:

```bash
python3 query.py
```

Resultado:

```text
Usuario
   |
   v
Pipeline RAG
   |
   v
Ollama
   |
   v
Respuesta
```

---

# 7. Flujo de protección térmica

```text
Temperatura CPU
        |
        v
thermal_watchdog.py
        |
        +----------------------+
        |                      |
        v                      v

    NORMAL                CRÍTICO

 Continuar             Registrar evento
 ejecución                    |
                               v
                      detener query.py
```

---

# 8. Principios de diseño

## Separación de responsabilidades

| Componente | Responsabilidad |
|------------|-----------------|
| LibreHardwareMonitor | Acceso a sensores físicos |
| export_temp_server.py | Adaptación y publicación de la información térmica |
| thermal_watchdog.py | Supervisión y protección |
| ingest.py | Extracción documental |
| chunk.py | División de información |
| embed.py | Generación de embeddings |
| symbol_extractor.py | Análisis estructural |
| query.py | Consulta RAG |
| Ollama | Inferencia mediante modelos LLM |

---

## Bajo acoplamiento

El sistema RAG no depende directamente del hardware.

Los componentes de inteligencia artificial únicamente consumen la información publicada mediante servicios externos, sin conocer detalles internos de:

- sensores físicos;
- chips de monitoreo;
- LibreHardwareMonitor;
- plataforma Windows.

---

## Arquitectura extensible

La separación de responsabilidades facilita la incorporación de nuevas funcionalidades, entre ellas:

- supervisión de memoria RAM;
- monitoreo de GPU;
- métricas de rendimiento;
- administración avanzada de Ollama;
- almacenamiento vectorial especializado;
- paneles de observabilidad.

---

# 9. Estado actual de la arquitectura

Actualmente la arquitectura permite:

- ejecutar modelos LLM localmente;
- consultar información documental mediante un pipeline RAG;
- analizar la estructura del código fuente;
- supervisar continuamente la temperatura del sistema;
- proteger automáticamente los procesos ante condiciones térmicas críticas;
- registrar eventos para su posterior análisis.

La arquitectura representa una integración práctica entre inteligencia artificial local, recuperación aumentada de información, administración de sistemas y automatización.