# Prueba 04 - Integración Final del Sistema

**Fecha:** 2026-07-28

---

# 1. Objetivo

Validar el funcionamiento integrado de la versión actual del proyecto, comprobando la interacción entre los distintos componentes que conforman la arquitectura RAG híbrida con supervisión térmica.

La prueba verifica que los principales módulos del sistema funcionan de manera coordinada y que la arquitectura mantiene la separación de responsabilidades definida durante el desarrollo.

---

# 2. Componentes evaluados

La validación comprende los siguientes componentes:

```text
Documentación

        │

        ▼

ingest.py

        │

        ▼

embed.py

        │

        ▼

embeddings.jsonl

        │

        ▼

query.py

        │

        ▼

llm_backend.py

   ┌───────────────┐

   ▼               ▼

LOCAL           CLOUD

Ollama      OpenRouter

        │

        ▼

logger.py

thermal_watchdog.py
```

---

# 3. Entorno de pruebas

## Sistema operativo

```text
Windows 10 Pro

WSL2 Ubuntu
```

---

## Componentes utilizados

- LibreHardwareMonitor
- export_temp_server.py
- thermal_watchdog.py
- logger.py
- query.py
- llm_backend.py
- Ollama
- OpenRouter

---

# 4. Procedimiento

Se verificó el funcionamiento integrado del sistema siguiendo el flujo habitual de ejecución:

1. Inicio de LibreHardwareMonitor.
2. Inicio del servicio de exportación térmica.
3. Inicio de `thermal_watchdog.py`.
4. Activación del entorno virtual de Python.
5. Inicio del servicio Ollama (cuando se utiliza el backend LOCAL).
6. Ejecución de `query.py`.
7. Selección del modo de operación.
8. Selección del backend de inferencia.
9. Ejecución de consultas de prueba.

---

# 5. Resultados obtenidos

Durante las pruebas se comprobó que:

- la recuperación documental funciona correctamente;
- los embeddings son utilizados durante la búsqueda semántica;
- el contexto se construye antes de la inferencia;
- `llm_backend.py` selecciona correctamente el backend configurado;
- la inferencia puede realizarse utilizando un backend LOCAL o CLOUD;
- `logger.py` registra las principales etapas del pipeline;
- `thermal_watchdog.py` supervisa continuamente la temperatura del sistema de forma independiente.

No fue necesario modificar el pipeline principal al cambiar entre proveedores de inferencia.

---

# 6. Validación de la arquitectura

Se verificó el correcto funcionamiento de los siguientes aspectos arquitectónicos:

| Componente | Estado |
|------------|:------:|
| Pipeline RAG | ✅ |
| Recuperación semántica | ✅ |
| llm_backend.py | ✅ |
| Backend LOCAL | ✅ |
| Backend CLOUD | ✅ |
| logger.py | ✅ |
| thermal_watchdog.py | ✅ |
| Supervisión térmica desacoplada | ✅ |

---

# 7. Observaciones

La arquitectura mantiene una clara separación entre:

- procesamiento documental;
- recuperación semántica;
- inferencia mediante modelos de lenguaje;
- registro de eventos;
- supervisión térmica.

Esta organización facilita el mantenimiento del sistema y permite incorporar nuevos proveedores de inferencia sin modificar la lógica principal del pipeline.

---

# 8. Conclusiones

La integración final confirmó el funcionamiento coordinado de los componentes implementados durante el desarrollo del proyecto.

La arquitectura híbrida permite reutilizar el mismo pipeline RAG con distintos backends de inferencia, manteniendo la recuperación documental en el entorno local y delegando únicamente la generación de respuestas al proveedor seleccionado.

Los mecanismos de supervisión térmica y registro de eventos complementan la arquitectura, proporcionando mayor estabilidad, capacidad de diagnóstico y protección del hardware durante la ejecución de consultas.

La versión actual del proyecto se considera una base funcional y modular para continuar la evolución de la arquitectura RAG, incorporando nuevas capacidades sin alterar los principios de diseño establecidos.
