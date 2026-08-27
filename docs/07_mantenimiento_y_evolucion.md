# 07 — Mantenimiento y Evolución del Sistema

**Fecha:** 26 de agosto de 2026
**Versión:** 0.5.1
**Estado:** Consolidado / Documentación oficial
**Módulo:** Mantenimiento & Evolución / Operaciones Técnicas
**Propósito:** Especificar los procedimientos operativos estándar (SOP), el orden recomendado de arranque del sistema híbrido, el mantenimiento del espacio de trabajo y la base de conocimiento (KS2), el diagnóstico de logs y la hoja de ruta evolutiva.

---

> **Resumen ejecutivo:**  
> La arquitectura modular de **Arquitectura_RAG_Termica** facilita el mantenimiento operativo independiente de cada subsistema. La administración se divide entre los servicios de telemetría en Windows (`E:\Developer\Tools\LibreHardwareMonitor\python`), el motor de scripts del asistente en WSL2 (`~/rag_maui_docs_for_rag/scripts`) y la base de conocimiento aislada del Target Project en `~/rag_workspace/MauiAppGestorMovil`. Este documento consolida el procedimiento de arranque, la regeneración atómica de índices vectoriales y de símbolos (KS2), y la gestión de la deuda técnica hacia la Fase II.

---

## 1. Introducción

La arquitectura del proyecto se diseñó bajo un enfoque estrictamente modular, donde cada componente mantiene responsabilidades claramente definidas y un bajo nivel de acoplamiento.

El sistema integra procesamiento documental, filtrado seguro de workspace (`knowledge_filter.py` v1.7), extracción atómica de símbolos (`symbols_extractor.py` v1.1 / `csharp_parser.py` v2.1.5), recuperación semántica, modelos de lenguaje, supervisión térmica y observabilidad, por lo que las tareas de mantenimiento abarcan tanto el entorno Windows anfitrión como el entorno WSL2 Ubuntu.

Los principales objetivos del mantenimiento son:

* conservar la estabilidad del entorno de ejecución híbrido;
* garantizar la disponibilidad de los servicios requeridos (Flask en Windows, Ollama en WSL2);
* mantener actualizados los modelos y dependencias en `venv_rag`;
* facilitar el diagnóstico mediante registros de ejecución (`query_log.txt`, `thermal_watchdog_log.txt`);
* permitir la incorporación progresiva de nuevas funcionalidades sin afectar la arquitectura existente.

---

## 2. Organización tripartita del sistema

La arquitectura se distribuye en tres ubicaciones físicas y lógicas bien delimitadas:

```text
                        WINDOWS (Servicios Térmicos)
            Ruta: E:\Developer\Tools\LibreHardwareMonitor\python
                                     │
                                     ├─ LibreHardwareMonitor.exe
                                     ├─ export_temp_server.py (Flask HTTP :5005)
                                     ├─ start_server.bat / stop_server.bat
                                     └─ windows_ip.txt ("192.168.1.37")
                                             │
                                             │ HTTP / JSON (:5005)
                                             ▼
                              WSL2 UBUNTU (Scripts del Asistente)
                   Ruta: ~/rag_maui_docs_for_rag/scripts
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
  Entorno Python               Ollama Daemon             thermal_watchdog.py
   (venv_rag)               (nomic-embed-text)
         │                           │
         ▼                           ▼
   Pipeline RAG              Recuperación Local
 (KS2 & Parsers)             (embeddings.jsonl)
         │                           │
         └─────────────┬─────────────┘
                       ▼
           llm_backend.py (LOCAL / CLOUD)
                       │
                       ▼
                             WSL2 UBUNTU (Target Project Workspace)
                         Ruta: ~/rag_workspace/MauiAppGestorMovil
```

---

## 3. Mantenimiento operativo: Secuencia estándar de arranque (SOP)

Para garantizar la correcta inicialización y evitar fallos de conexión o referencias cruzadas, se recomienda seguir el siguiente orden estricto de ejecución:

### Paso 1: Inicializar la telemetría en Windows
1. Iniciar `LibreHardwareMonitor.exe` en Windows.
2. Ejecutar el servidor de exportación térmica navegando a `E:\Developer\Tools\LibreHardwareMonitor\python` y corriendo:
   ```bat
   start_server.bat
   ```
3. Verificar el endpoint desde el navegador o terminal Windows: `http://localhost:5005/data.json`. Esto genera o actualiza automáticamente `windows_ip.txt` con la IP anfitriona (ej. `192.168.1.37`).

---

### Paso 2: Activar el servicio de modelos de lenguaje (WSL2)
En la terminal de WSL2 Ubuntu, verificar si el daemon de Ollama está activo:
```bash
ollama list
```
Si el servicio no está en ejecución, iniciarlo con:
```bash
ollama serve
```

---

### Paso 3: Activar la supervisión térmica (WSL2)
En una terminal secundaria de WSL2, navegar al directorio de scripts e iniciar el *watchdog*:
```bash
cd ~/rag_maui_docs_for_rag/scripts
source venv_rag/bin/activate
python3 thermal_watchdog.py
```
*Salida esperada:*
```text
📖 IP Windows detectada desde archivo: 192.168.1.37
🟢 Thermal Watchdog iniciado | Endpoint: http://192.168.1.37:5005/data.json
🌡 CPU: 45.00°C | Avg(5): 44.80°C | Estado: NORMAL
```

---

### Paso 4: Ejecutar el pipeline de conocimiento KS2 (Sincronización del Workspace)
Antes de realizar consultas sobre un proyecto actualizado o recién modificado:
```bash
cd ~/rag_maui_docs_for_rag/scripts
source venv_rag/bin/activate

# 1. Filtrar workspace seguro
python3 knowledge_filter.py

# 2. Extraer símbolos C# estructurados
python3 symbols_extractor.py

# 3. Generar / Reconciliar índice vectorial de embeddings
python3 embed.py
```

---

### Paso 5: Iniciar el motor de consultas RAG
```bash
python3 query.py
```
Seleccionar el modo de operación (**DEPURACIÓN**, **ARQUITECTURA** o **DOCUMENTACIÓN**) y el backend de inferencia (**LOCAL** u **OpenRouter CLOUD**).

---

## 4. Mantenimiento de los datos RAG y el workspace (KS2)

La base de conocimiento activa del proyecto objetivo resalta aislada dentro de `~/rag_workspace/MauiAppGestorMovil`.

```text
~/rag_workspace/MauiAppGestorMovil
├── knowledge/
│   ├── embeddings/
│   │   ├── embeddings.jsonl                          # Índice vectorial activo (57 entidades)
│   │   ├── embeddings.pre-ADR012-2026-08-12.jsonl   # Respaldo histórico ADR-012
│   │   └── embeddings.pre-v2.2-2026-08-12.jsonl     # Respaldo histórico v2.2
│   └── symbols/
│       └── symbols_raw.jsonl                         # 57 símbolos C# extraídos por KS2
├── knowledge_policy.conf                             # Políticas v1.2 (Exclusión de Deprecated/Backups)
└── project.conf                                       # Configuración del workspace (workspace_path)
```

### Cuándo ejecutar la regeneración de índices:
* **`knowledge_filter.py`:** Al añadir nuevos archivos `.cs`, `.xaml` o cambiar las políticas de exclusión en `knowledge_policy.conf`.
* **`symbols_extractor.py`:** Al agregar o modificar firmas de métodos, clases o constructores en C#.
* **`embed.py`:** Se ejecuta tras la extracción de símbolos. Gracias a la lógica atómica del **ADR-012**, `embed.py` detecta qué entidades sufrieron modificaciones (43 en el último ciclo de v2.1.5) y cuáles permanecieron idénticas (14), evitando llamadas redundantes al modelo `nomic-embed-text`.

---

## 5. Diagnóstico de errores y auditoría de logs

El mantenimiento preventivo y correctivo se apoya en dos archivos de auditoría independientes:

### 5.1 Diagnóstico del Pipeline RAG (`query_log.txt`)
Administrado por `logger.py`, registra las sesiones de consulta y desglosa las latencias:
* `EMBEDDING_TIME`: Generación de vector de la consulta.
* `SEARCH_TIME`: Búsqueda de similitud coseno sobre `embeddings.jsonl`.
* `LLM_TIME`: Tiempo consumido por Ollama u OpenRouter.
* `PIPELINE_TIME`: Duración total end-to-end.
* **Inspección de Chunks:** Habilitar la bandera `DEBUG_CHUNKS = True` en `query.py` para escribir los fragmentos recuperados en `query_log.txt`.

### 5.2 Diagnóstico Térmico (`thermal_watchdog_log.txt`)
Administrado por `thermal_watchdog.py`, permite auditar:
* picos de temperatura del procesador anfitrión;
* cierres preventivos ejecutados mediante `pkill -f query.py`;
* fallos de red o desconexiones con el servicio Flask en Windows (`5005`).

---

## 6. Gestión de respaldos y repositorio Git

Para garantizar la integridad ante fallos de disco o refactorizaciones de código:

1. **Estructura para Git (Windows Host):** Sincronizar manualmente los scripts de WSL2 (`scripts/`), la telemetría de Windows (`LibreHardwareMonitor/python/`) y la documentación (`docs/`) dentro de la carpeta clonada en Windows:
   ```text
   E:\Developer\IA\Arquitectura_RAG_Termica
   ```
2. **Archivos Excluidos (`.gitignore`):** Verificar que archivos temporales (`query_log.txt`, `thermal_watchdog_log.txt`, `windows_ip.txt`), entornos virtuales (`venv_rag/`) y cachés de Python (`__pycache__/`) permanezcan ignorados por Git.
3. **Respaldo de la Base Vectorial:** Conservar los archivos `.jsonl` respaldados en `knowledge/embeddings/` (ej. `embeddings.pre-ADR012-2026-08-12.jsonl`) para acelerar la restauración sin re-vectorizar el código.

---

## 7. Evolución prevista y Hoja de Ruta (Deuda Técnica)

El sistema evoluciona de forma incremental conservando la paridad entre arquitectura y código. Las siguientes etapas establecen la prioridad inmediata post-commit:

```text
 [ Estado Actual v0.5.1 ] ──> [ Commit GitHub ] ──> [ Deuda Técnica v0.5.2 ] ──> [ Fase II - v0.6 ]
   KS2 Congelado & Probad.       Subir cambios         - Consumo de símbolos       Architecture Orientada
   (57 símbolos C# / 57 vect.)   a repositorio           ricos en query.py          a Construcción de Contexto
                                                       - Validar Parser CSS        (Knowledge Packages)
```

1. **Inmediato Post-Commit (v0.5.2):**
   * **Integración Rica en `query.py`:** Adaptar `query.py` para aprovechar la rica estructura de constructores y metadatos extraídos por `symbols_extractor.py` v1.1 y `csharp_parser.py` v2.1.5.
   * **Validación de Parsers Secundarios:** Incorporar y probar end-to-end parsers de formatos complementarios (como el parser CSS).
2. **Evolución a Fase II (Versión 0.6):**
   * Transición a una **Arquitectura Orientada a Construcción de Contexto**, introduciendo contratos de datos explicitados (`IntentSpec`, `Knowledge Package`) y *Context Pruners* para optimizar la ventana de contexto del LLM.

---

## 8. Estado actual de mantenimiento

Al **26 de agosto de 2026**, el procedimiento de mantenimiento y la estructura del sistema se encuentran consolidados:
* **Entornos Alineados:** Windows (`5005`), WSL2 (`~/rag_maui_docs_for_rag/scripts`) y Target Project (`~/rag_workspace/MauiAppGestorMovil`) operando sin interferencias.
* **Ciclo KS2 Congelado:** Sincronización vectorial atómica probada en `embed.py` sobre 57 entidades C#.
* **Logs Operativos:** Auditoría transparente en `query_log.txt` y `thermal_watchdog_log.txt`.
* **Ruta de Versiones Clara:** Repositorio v0.5.1 listo para sincronización prioritaria en GitHub.

