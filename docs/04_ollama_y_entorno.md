# 04 — Entorno de Ejecución y Backends de Inferencia

**Fecha:** 26 de agosto de 2026
**Versión:** 0.5.1
**Estado:** Consolidado / Documentación oficial
**Módulo:** Infraestructura / Entorno WSL2 & Backends de Inferencia
**Propósito:** Especificar la configuración del entorno Windows anfitrión, el entorno WSL2 Ubuntu, la ubicación exacta de los scripts de ejecución, la estructura real del workspace aislado y la capa de abstracción de inferencia (`llm_backend.py`).

---

> **Resumen ejecutivo:**  
> **Arquitectura_RAG_Termica** opera sobre una infraestructura híbrida dividida en dos entornos de ejecución: un entorno en **Windows** dedicado a la telemetría de hardware (`export_temp_server.py`) y un entorno en **WSL2 Ubuntu** (`/home/manuelc/rag_maui_docs_for_rag/scripts`) donde residen los componentes principales del pipeline. La base de conocimiento activa del proyecto objetivo (**MauiAppGestorMovil**) se encuentra completamente desacoplada en `~/rag_workspace/MauiAppGestorMovil`, manteniendo aislados el código fuente C#/.NET MAUI y los índices de conocimiento vectoriales y estructurales (`embeddings.jsonl` y `symbols_raw.jsonl`).

---

## 1. Introducción

El proyecto utiliza un entorno de ejecución distribuido entre **Windows** (anfitrión) y **WSL2 Ubuntu**, donde se ejecutan los scripts del pipeline RAG, el motor de extracción de símbolos (KS2) y los modelos de inteligencia artificial.

La arquitectura se ha diseñado para separar strictly:
* los servicios de telemetría térmica en Windows (`export_temp_server.py`);
* el motor de scripts del asistente en WSL2 (`/home/manuelc/rag_maui_docs_for_rag/scripts`);
* la preparación y filtrado del espacio de trabajo del proyecto objetivo (`knowledge_filter.py`);
* la extracción determinista de símbolos (`symbols_extractor.py` con `csharp_parser.py` v2.1.5);
* la recuperación semántica y persistencia vectorial (`embed.py` / `embeddings.jsonl`);
* la generación de respuestas mediante una capa de abstracción de inferencia (`llm_backend.py`);
* la observabilidad del pipeline (`logger.py`);
* la supervisión térmica preventiva (`thermal_watchdog.py`).

Actualmente el proyecto soporta dos modalidades de inferencia:
* **Backend LOCAL**, mediante Ollama.
* **Backend CLOUD**, mediante OpenRouter.

Esta arquitectura híbrida permite ejecutar el sistema 100% local cuando el hardware lo soporta o derivar la inferencia a modelos remotos de alta capacidad cuando se requieren respuestas complejas, sin alterar la recuperación del conocimiento local.

---

## 2. Arquitectura del entorno distribuido

El sistema distingue tres ubicaciones físicas/lógicas principales en la máquina anfitriona:

```text
                                WINDOWS (Servicios Térmicos)
                    Ruta: E:\Developer\Tools\LibreHardwareMonitor\python
                                         │
                                         ├─ LibreHardwareMonitor.exe
                                         ├─ export_temp_server.py (Flask HTTP :5005)
                                         ├─ start_server.bat / stop_server.bat
                                         └─ windows_ip.txt ("192.168.1.37")
                                                 │
                                                 │ HTTP / JSON
                                                 ▼
                                  WSL2 UBUNTU (Scripts del Asistente)
                       Ruta: ~/rag_maui_docs_for_rag/scripts
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         ▼                               ▼                               ▼
  Entorno Python                   Ollama Daemon                 Supervisión Térmica
   (venv_rag)                   (nomic-embed-text)              (thermal_watchdog.py)
         │                               │                               │
         ▼                               ▼                               │
   Pipeline RAG                  Recuperación Local                      │
 (KS2 & Parsers)                 (embeddings.jsonl)                      │
         │                               │                               │
         └───────────────┬───────────────┘                               │
                         ▼                                               ▼
             Construcción del contexto ──────────────────────> Interrupción Preventiva
                         │                                    en Sobretemperatura
                         ▼
                  llm_backend.py
                   /          \
                  /            \
                 v              v
            Ollama Local   OpenRouter Cloud
                 │              │
                 └──────┬───────┘
                        ▼
                 Respuesta final
                (query_log.txt)
                         │
                         ▼
                               WSL2 UBUNTU (Target Project Workspace)
                           Ruta: ~/rag_workspace/MauiAppGestorMovil
```

---

## 3. Distribución de componentes y directorios

El proyecto organiza sus scripts y datos en tres ubicaciones físicas bien delimitadas:

### 3.1 Entorno Windows (Telemetría de Hardware)
* **Directorio:** `E:\Developer\Tools\LibreHardwareMonitor\python`
* **Propósito:** Captura de datos de los sensores térmicos físicos del procesador mediante `LibreHardwareMonitor` y publicación de un API REST HTTP.

Archivos contenidos:
* `export_temp_server.py`: Servidor ligero Flask en puerto 5005.
* `start_server.bat`: Script de inicio del servidor Flask en Windows.
* `stop_server.bat`: Script de detención del servidor en Windows.
* `windows_ip.txt`: Archivo generado automáticamente con la IP anfitriona (ej. `192.168.1.37`).

---

### 3.2 Entorno WSL2 — Scripts del Asistente RAG
* **Directorio Base:** `\\wsl.localhost\Ubuntu\home\manuelc\rag_maui_docs_for_rag\scripts`
* **Subdirectorio de Parsers:** `~/rag_maui_docs_for_rag/scripts/parsers/`
* **Propósito:** Alojamiento de todo el motor ejecutable del asistente técnico RAG.

Archivos principales en `scripts/`:
* `knowledge_filter.py` (v1.7): Filtrado seguro de espacio de trabajo con guarda `is_safe_to_delete()`.
* `symbols_extractor.py` (v1.1): Extractor determinista con carga dinámica via `importlib`.
* `ingest.py`: Ingestión documental y etiquetado por capas.
* `chunk.py`: Fragmentador semántico de documentos.
* `embed.py`: Generador y reconciliador de índices vectoriales.
* `query.py`: Coordinador principal del pipeline RAG y formateador de prompts.
* `llm_backend.py`: Capa de abstracción para Ollama (Local) y OpenRouter (Cloud).
* `logger.py`: Observabilidad, registro de métricas y función `log_debug()`.
* `thermal_watchdog.py`: Monitor continuo que consulta el servicio Flask en Windows.
* `monitor_temperatura.py` / `test_config.py` / `config_loader.py`: Scripts auxiliares y de diagnóstico.
* `parsers/`: Directorio especializado que alberga los parsers por lenguaje, incluyendo `csharp_parser.py` (v2.1.5).

---

### 3.3 Entorno WSL2 — Workspace del Proyecto Objetivo (`Target Project`)
* **Directorio Base:** `\\wsl.localhost\Ubuntu\home\manuelc\rag_workspace`
* **Caso de Prueba Activo:** `MauiAppGestorMovil`
* **Propósito:** Alojamiento aislado del proyecto asistido (.NET MAUI) y de su base de conocimiento estructurada.

Árbol de directorios real (`~/rag_workspace/MauiAppGestorMovil`):

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
├── project.conf                                       # Configuración del workspace (workspace_path)
└── source/                                            # Código fuente C#/.NET MAUI (82 archivos, 27 carpetas)
    ├── ARQUITECTURA_DETALLADA.md
    ├── CHANGELOG.md
    ├── INSTRUCCIONES_RECONSTRUCCION.md
    ├── README.md
    ├── Controls/
    │   └── BotonPersonalizado.cs
    ├── Converters/
    │   ├── BoolToFlechaConverter.cs
    │   ├── IntIncrementConverter.cs
    │   ├── IntToBoolConverter.cs
    │   ├── IntToThicknessConverter.cs
    │   └── NullToBooleanConverter.cs
    ├── DatosIniciales/ (Excluido de indexación por política)
    │   ├── categorias.json
    │   └── productos.json
    ├── Helpers/
    │   ├── AppNavigator.cs
    │   ├── AppState.cs
    │   ├── CategoriaHelper.cs
    │   ├── CloseTecladoHelper.cs
    │   ├── DecimalHelper.cs
    │   ├── Logger.cs
    │   └── PropiedadesHelper.cs
    ├── Messages/
    │   ├── CategoriaMessages.cs
    │   └── ProductoAgregadoMessage.cs
    ├── Models/
    │   ├── Categoria.cs
    │   ├── CategoriaNodo.cs
    │   ├── Producto.cs
    │   └── Propiedad.cs
    ├── Platforms/
    │   ├── Android/ (MainActivity.cs, MainApplication.cs)
    │   ├── MacCatalyst/ (AppDelegate.cs, Program.cs)
    │   ├── Tizen/ (Main.cs)
    │   ├── Windows/ (App.xaml, App.xaml.cs)
    │   └── iOS/ (AppDelegate.cs, Program.cs)
    ├── Repositories/
    │   └── SQLite/ (CategoriaSQLiteRepository.cs, ProductoSQLiteRepository.cs)
    ├── Resources/
    │   └── Styles/ (Colors.xaml, Styles.xaml)
    ├── Services/
    │   ├── ICategoriaRepository.cs
    │   ├── ICategoriaService.cs
    │   └── InicializadorDatos.cs
    ├── ViewModels/
    │   ├── AgregarProductoViewModel.cs
    │   ├── EditarCategoriaViewModel.cs
    │   ├── FrameDashboardViewModel.cs
    │   ├── GestionDeCategoriasViewModel.cs
    │   ├── GestionDeProductosViewModel.cs
    │   ├── Helpers/ (BaseViewModel.cs)
    │   └── SeleccionarCategoriaProductoViewModel.cs
    └── Views/ (Vistas XAML y Code-Behind .xaml.cs)
        ├── AgregarCategoria.xaml / .xaml.cs
        ├── AgregarProducto.xaml / .xaml.cs
        ├── AgregarSubcategoria.xaml / .xaml.cs
        ├── CargandoApp.xaml / .xaml.cs
        ├── Controls/ (CategoriaItemSeleccionView, CategoriaItemView)
        ├── DetallesDelProducto.xaml / .xaml.cs
        ├── EditarCategoria.xaml / .xaml.cs
        ├── EditarProducto.xaml / .xaml.cs
        ├── EncabezadoEmpresa.xaml / .xaml.cs
        ├── FrameDashboard.xaml / .xaml.cs
        ├── GestionDeCategorias.xaml / .xaml.cs
        ├── GestionDeProductos.xaml / .xaml.cs
        └── SeleccionarCategoriaProducto.xaml / .xaml.cs
```

---

## 4. Entorno Python y dependencias

El motor ejecutable en WSL2 aísla sus librerías mediante un entorno virtual dedicado.

* **Nombre del entorno:** `venv_rag`
* **Ubicación recomendada:** `~/rag_maui_docs_for_rag/scripts/venv_rag`
* **Activación:**
  ```bash
  source ~/rag_maui_docs_for_rag/scripts/venv_rag/bin/activate
  ```
* **Versión de Python:** Python 3.12.x

---

## 5. Layer de abstracción del backend (`llm_backend.py`)

La comunicación con los modelos de lenguaje se centraliza en `llm_backend.py` dentro de `scripts/`. Este módulo desacopla por completo la recuperación de información del motor de generación.

```text
query.py  ──> Contexto RAG + Prompt  ──> llm_backend.py ──┬──> Ollama (HTTP 11434)
                                                          └──> OpenRouter (HTTPS API)
```

---

## 6. Backend LOCAL (Ollama) y Backend CLOUD (OpenRouter)

### Backend LOCAL (Ollama)
* **Endpoint:** `http://localhost:11434`
* **Modelos configurados:**
  * Embeddings: `nomic-embed-text`
  * Depuración/Código: `qwen2.5-coder:1.5b`
  * Razonamiento: `llama3.2:3b`

### Backend CLOUD (OpenRouter)
* **Autenticación:** Variable de entorno `OPENROUTER_API_KEY`.
* **Seguridad y Privacidad:** La base vectorial (`embeddings.jsonl`) y el árbol de símbolos (`symbols_raw.jsonl`) residen 100% en WSL2 (`~/rag_workspace/MauiAppGestorMovil/knowledge/`); el servicio cloud solo recibe el fragmento de contexto empaquetado para la consulta activa.

---

## 7. Comandos de operación técnica del entorno

Para ejecutar el pipeline RAG desde la terminal WSL2:

```bash
# 1. Navegar al directorio base de scripts
cd ~/rag_maui_docs_for_rag/scripts

# 2. Activar el entorno virtual
source venv_rag/bin/activate

# 3. Ejecutar el filtrado del workspace (knowledge_filter.py v1.7)
python3 knowledge_filter.py

# 4. Extraer símbolos del proyecto objetivo (symbols_extractor.py v1.1)
python3 symbols_extractor.py

# 5. Generar y reconciliar índices vectoriales (embed.py)
python3 embed.py

# 6. Iniciar el motor de consultas RAG (query.py)
python3 query.py
```

---

## 8. Estado actual del entorno

Al **26 de agosto de 2026**, el entorno de ejecución ofrece:
* **Separación Tripartita de Directorios:**
  1. Windows `E:\Developer\Tools\LibreHardwareMonitor\python` para la telemetría térmica.
  2. WSL2 `~/rag_maui_docs_for_rag/scripts` para los ejecutables del motor RAG y parsers.
  3. WSL2 `~/rag_workspace/MauiAppGestorMovil` para el espacio de trabajo aislado del Target Project.
* **Persistencia Estructurada en `MauiAppGestorMovil`:**
  * `knowledge/symbols/symbols_raw.jsonl` (57 símbolos extraídos).
  * `knowledge/embeddings/embeddings.jsonl` (57 vectores reconciliados).
* **Políticas de Exclusión Respetadas:** Exclusión verificada de `DatosIniciales/` y copias de respaldo mediante `knowledge_policy.conf` (v1.2).
* **Supervisión y Auditoría:** Auditoría en `logger.py` y protección térmica activa entre Flask (Windows) y `thermal_watchdog.py` (WSL2).

