# Pruebas del Proyecto

## Descripción

Esta carpeta contiene el registro de las principales pruebas realizadas durante el desarrollo de la arquitectura RAG con supervisión térmica.

Su propósito es conservar evidencia de las validaciones efectuadas sobre los componentes más relevantes del sistema y documentar los principales hitos alcanzados durante su evolución.

Los documentos aquí almacenados representan el estado del proyecto en la fecha indicada por cada archivo y complementan la información resumida en `docs/06_pruebas_y_validacion.md`.

---

## Organización

Las pruebas se documentan de forma cronológica, reflejando la evolución de la arquitectura desde las primeras validaciones del backend local hasta la integración del backend híbrido y la validación del sistema completo.

Cada documento describe el objetivo de la prueba, el entorno utilizado, el procedimiento seguido, los resultados obtenidos y las conclusiones correspondientes.

---

## Convención de nombres

Los archivos utilizan el siguiente formato:

```text
YYYY-MM-DD_descripcion.md
```

Ejemplo:

```text
2026-07-20_prueba01_backend_local_qwen2.5-coder-1.5b.md
```

---

## Alcance

Las pruebas pueden incluir la validación de aspectos como:

- backend LOCAL mediante Ollama;
- backend CLOUD mediante OpenRouter;
- arquitectura híbrida de inferencia;
- generación de embeddings;
- recuperación semántica;
- supervisión y protección térmica;
- registro de eventos mediante `logger.py`;
- integración del pipeline RAG.

---

## Alcance histórico

Los resultados documentados constituyen evidencia técnica del proceso de desarrollo y representan el estado del proyecto en el momento en que fueron realizados.

Por este motivo, algunos detalles de configuración, modelos utilizados o resultados obtenidos pueden diferir de versiones posteriores de la arquitectura, sin afectar la validez histórica de la documentación.
