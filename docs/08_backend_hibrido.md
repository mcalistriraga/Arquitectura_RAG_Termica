# 08 — Backend de Inferencia Híbrido

**Fecha:** 26 de agosto de 2026
**Versión:** 0.5.1
**Estado:** Consolidado / Documentación oficial
**Módulo:** Inferencia / Abstracción Multi-Provider & API Layer
**Propósito:** Especificar la arquitectura del backend de inferencia híbrido (`llm_backend.py`), la separación entre la recuperación de conocimiento local y la generación de respuestas, la integración con Ollama (Local) y OpenRouter (Cloud), y la gestión segura de credenciales.

---

> **Resumen ejecutivo:**  
> Uno de los pilares de la arquitectura de **Arquitectura_RAG_Termica** es el desacoplamiento estricto entre la preparación y recuperación del conocimiento local (KS2, embeddings vectoriales, fragmentación) y la inferencia por modelos de lenguaje. El módulo `llm_backend.py` actúa como una capa de abstracción agnóstica que encapsula las llamadas tanto a servidores locales (**Ollama**) como a proveedores en la nube (**OpenRouter API**), permitiendo alternar de backend sin alterar una sola línea del pipeline de recuperación en WSL2.

---

## 1. Introducción y motivación

Las primeras iteraciones del proyecto dependían exclusivamente de Ollama para la generación local de respuestas. Si bien este enfoque ofrecía privacidad total y funcionamiento offline, las pruebas sobre hardware anfitrión de recursos limitados (AMD FX-6300 sin GPU dedicada) mostraron cuellos de botella:

* uso intensivo y prolongado del CPU durante la inferencia de modelos de razonamiento;
* elevación sostenida de la temperatura anfitriona cerca de los límites críticos ($62.0\ ^\circ\text{C}$);
* latencias de respuesta superiores a 20 segundos por consulta RAG.

Para resolver estas limitaciones sin perder la soberanía sobre los datos documentales ni la protección del hardware, se diseñó e implementó la capa de abstracción `llm_backend.py`.

Esta arquitectura híbrida garantiza que:
* la indexación documental, filtrado seguro (`knowledge_filter.py` v1.7), extracción de símbolos (`symbols_extractor.py` v1.1 / `csharp_parser.py` v2.1.5) y reconciliación de vectores (`embed.py`) permanezcan **100% locales** en WSL2 Ubuntu;
* la inferencia pueda ser derivada dinámicamente a **Ollama** (Local) o a **OpenRouter** (Cloud) según la complejidad de la consulta o el estado térmico del procesador.

---

## 2. Principios de diseño del backend

```text
                  [ Pipeline RAG Local en WSL2 ]
      (documentos, símbolos C#, embeddings, similitud coseno)
                                │
                                ▼
                     Construcción del Contexto
                                │
                                ▼
                         llm_backend.py
                ┌───────────────┴───────────────┐
                ▼                               ▼
          Backend LOCAL                   Backend CLOUD
             Ollama                        OpenRouter
   (http://localhost:11434)            (API Key vía HTTPS)
                │                               │
                └───────────────┬───────────────┘
                                ▼
                         Respuesta LLM
                      (Logged by logger.py)
```

1. **Separación de Responsabilidades:** El motor RAG prepara el contexto técnico; `llm_backend.py` únicamente empaqueta el prompt y transmite la solicitud al proveedor.
2. **Bajo Acoplamiento:** `query.py` desconoce los detalles de red, endpoints HTTP o estructuras JSON específicas de Ollama u OpenRouter.
3. **Soberanía y Seguridad del Conocimiento:** Al utilizar el backend Cloud, únicamente se transmite el fragmento de contexto empaquetado para responder la duda puntual; la base documental completa y el mapa de símbolos residen en `~/rag_workspace/MauiAppGestorMovil/`.
4. **Extensibilidad:** Agregar un nuevo proveedor (ej. Anthropic direct, LocalAI, vLLM) requiere únicamente añadir una función adaptadora en `llm_backend.py`.

---

## 3. Especificación técnica del adaptador (`llm_backend.py`)

### Ubicación del ejecutable:
```text
\\wsl.localhost\Ubuntu\home\manuelc\rag_maui_docs_for_rag\scripts\llm_backend.py
```

`llm_backend.py` ofrece una interfaz unificada expuesta a `query.py` que recibe el prompt, la configuración de sesión y los parámetros de depuración, encargándose del ruteo interno.

```text
query.py ──> query_llm(prompt, config) ──> llm_backend.py ──> Retorna String Formateado
```

---

## 4. Backend LOCAL (Ollama)

Servidor local ejecutándose como daemon en WSL2.

* **Endpoint Estándar:** `http://localhost:11434/api/generate` o `/api/chat`
* **Modelos Asignados por Modo de Operación:**

| Modo de Trabajo | Modelo Configurado | Rol Principal |
| :--- | :--- | :--- |
| **Embeddings** | `nomic-embed-text` | Generación de vectores para `embeddings.jsonl` y consultas. |
| **DEPURACIÓN** | `qwen2.5-coder:1.5b` | Análisis rápido de sintaxis, métodos C# y bugs de compilación. |
| **ARQUITECTURA** | `llama3.2:3b` | Análisis de dependencias, ViewModels, Views XAML y patrones MVVM. |
| **DOCUMENTACIÓN** | `llama3.2:3b` | Explicaciones funcionales y redacción de manuales técnicos. |

---

## 5. Backend CLOUD (OpenRouter)

Servicio de inferencia remota multimodelo vía API HTTPS.

* **Endpoint Estándar:** `https://openrouter.ai/api/v1/chat/completions`
* **Manejo de Respuestas:** Configuración explícita de `max_tokens` y `temperature` para evitar respuestas truncadas o alucinadas.
* **Ventajas en Operación:**
  * Cero carga computacional o térmica sobre el CPU anfitrión (`AMD FX-6300`).
  * Respuestas en latencias notablemente reducidas (~1.2s vs ~18.7s en local).
  * Acceso a modelos de frontera para validar razonamientos complejos sobre la arquitectura .NET MAUI.

---

## 6. Gestión segura de credenciales

Para cumplir con las normas de seguridad e impedir la filtración de credenciales en Git:

* Las API Keys del backend Cloud se leen desde variables de entorno o mediante el archivo de configuración privado:
  ```text
  ~/rag_maui_docs_for_rag/scripts/.env
  ```
* **Contenido de `.env`:**
  ```env
  OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  ```
* **Protección de Repositorio:** El archivo `.env` está estrictamente ignorado en `.gitignore`, evitando su subida accidental al repositorio remoto.

---

## 7. Integración con Observabilidad y Protección Térmica

`llm_backend.py` se integra nativamente con el ecosistema de supervisión del proyecto:

1. **Auditoría de Latencias (`logger.py`):** El tiempo consumido exclusivamente por la llamada de inferencia es cronometrado y registrado bajo la métrica `LLM_TIME`.
2. **Protección Térmica (`thermal_watchdog.py`):** Si durante la ejecución en backend Local la temperatura supera los $62.0\ ^\circ\text{C}$ (`TEMP_CRITICAL`), el watchdog aborta atómicamente la ejecución (`pkill -f query.py`), cortando la llamada a Ollama y protegiendo el hardware.

---

## 8. Estado actual de implementación

Al **26 de agosto de 2026**, el backend de inferencia híbrido presenta el siguiente estado:

* **Módulo Abstraído:** `llm_backend.py` completamente funcional en `scripts/`.
* **Pruebas de Integración Aprobadas:** Validación documentada en `docs/pruebas/2026-07-21_prueba03_backend_hibrido_local_cloud.md`.
* **Seguridad Garantizada:** Exclusión de credenciales `.env` verificada en la raíz de Git.
* **Paridad de Prompt:** Exactamente la misma plantilla de prompt contextualizado RAG se envía a Ollama u OpenRouter, garantizando comparabilidad de resultados.

