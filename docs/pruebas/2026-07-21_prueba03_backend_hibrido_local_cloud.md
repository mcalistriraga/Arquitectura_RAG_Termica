# Prueba 03 - Validación del Backend Híbrido (LOCAL / CLOUD)

**Fecha:** 2026-07-21

---

# 1. Objetivo

Validar la nueva arquitectura de inferencia desacoplada implementada mediante `llm_backend.py`, comprobando que el pipeline RAG mantiene el mismo funcionamiento independientemente del backend de inferencia seleccionado.

La prueba busca verificar que:

- el proceso de recuperación documental permanece inalterado;
- la construcción del contexto se realiza de forma local;
- la selección del backend de inferencia se realiza correctamente;
- la aplicación puede utilizar tanto un proveedor LOCAL como CLOUD sin modificar el resto del pipeline.

---

# 2. Componentes evaluados

```text
query.py

        │

        ▼

Recuperación semántica

        │

        ▼

Construcción del contexto

        │

        ▼

llm_backend.py

   ┌───────────────┐

   ▼               ▼

LOCAL           CLOUD

Ollama      OpenRouter
```

---

# 3. Entorno de pruebas

## Sistema operativo

```text
Windows 10 Pro

WSL2 Ubuntu
```

---

## Backend LOCAL

```text
Ollama
```

Modelos configurados:

```text
Embeddings:
nomic-embed-text

Depuración:
qwen2.5-coder:1.5b

Arquitectura:
llama3.2:3b

Documentación:
llama3.2:3b
```

---

## Backend CLOUD

```text
OpenRouter
```

Configuración mediante:

```text
scripts/.env
```

---

# 4. Procedimiento

Para cada ejecución se inició el pipeline mediante:

```bash
python3 query.py
```

Durante el inicio de la sesión se seleccionó:

- modo de operación;
- backend de inferencia;
- modelo correspondiente.

Se realizaron pruebas independientes utilizando:

- Backend LOCAL;
- Backend CLOUD.

---

# 5. Resultados obtenidos

## Recuperación documental

En ambos casos se verificó que:

- la generación de embeddings permaneció sin cambios;
- la recuperación semántica utilizó el mismo índice documental;
- el contexto enviado al modelo fue construido por el mismo pipeline RAG.

---

## Backend LOCAL

Se comprobó que `llm_backend.py` dirigió correctamente la solicitud hacia Ollama.

La respuesta fue generada utilizando los modelos instalados localmente.

---

## Backend CLOUD

Se comprobó que `llm_backend.py` dirigió correctamente la solicitud hacia OpenRouter utilizando la API configurada.

La respuesta fue obtenida desde el proveedor remoto sin modificar el resto del pipeline.

---

# 6. Validación

Durante la prueba se verificó que:

- el pipeline RAG no requiere modificaciones al cambiar de backend;
- `llm_backend.py` abstrae correctamente el proveedor de inferencia;
- la recuperación documental permanece completamente local;
- la única diferencia entre ambos modos corresponde a la etapa de inferencia.

---

# 7. Conclusiones

La prueba permitió validar la arquitectura híbrida implementada en el proyecto.

La separación entre recuperación documental e inferencia facilita la incorporación de nuevos proveedores de modelos sin afectar el funcionamiento del pipeline principal.

Se confirmó que la utilización de un backend CLOUD permite reducir la dependencia del hardware local manteniendo el mismo flujo general de procesamiento y reutilizando la infraestructura RAG existente.
