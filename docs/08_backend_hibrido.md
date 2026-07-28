# Backend de Inferencia

## 1. Introducción

Uno de los principios fundamentales de la arquitectura del proyecto consiste en separar completamente el proceso de recuperación del conocimiento (RAG) del mecanismo encargado de generar las respuestas.

El pipeline RAG mantiene localmente todas las etapas relacionadas con el procesamiento documental, la generación de embeddings, la recuperación semántica y la construcción del contexto. La inferencia mediante modelos de lenguaje se delega a un componente especializado (`llm_backend.py`), responsable de abstraer el proveedor de inteligencia artificial utilizado durante cada consulta.

Esta separación permite mantener estable el resto de la arquitectura independientemente del backend de inferencia seleccionado.

---

# 2. Motivación

Las primeras versiones del proyecto ejecutaban todas las consultas utilizando Ollama como servidor local de modelos.

Este enfoque proporcionaba ventajas importantes:

- funcionamiento sin conexión a Internet;
- control completo sobre los datos;
- privacidad de la información;
- independencia de servicios externos.

Sin embargo, las pruebas realizadas sobre el hardware utilizado durante el desarrollo evidenciaron algunas limitaciones:

- elevada utilización del procesador durante la inferencia;
- incremento de la temperatura del sistema;
- tiempos de respuesta dependientes de la capacidad del equipo.

Como consecuencia, se decidió desacoplar el mecanismo de inferencia del resto del pipeline RAG mediante una capa de abstracción que permitiera incorporar distintos proveedores sin modificar la lógica principal de la aplicación.

---

# 3. Principios de diseño

La arquitectura del backend de inferencia se diseñó siguiendo los siguientes principios.

## Separación entre recuperación e inferencia

Todo el procesamiento relacionado con el conocimiento permanece en el entorno local.

En particular:

- documentos fuente;
- procesamiento documental;
- generación de embeddings;
- recuperación semántica;
- contexto arquitectónico.

El backend de inferencia recibe únicamente el contexto recuperado y la consulta del usuario para generar la respuesta final.

---

## Bajo acoplamiento

El pipeline RAG no interactúa directamente con Ollama, OpenRouter ni con ningún otro proveedor de modelos.

Toda la comunicación se realiza mediante una única capa de abstracción:

```text
query.py
      │
      ▼
llm_backend.py
```

Esta organización facilita el mantenimiento y reduce el impacto de futuras modificaciones.

---

## Extensibilidad

La incorporación de nuevos proveedores de inferencia requiere únicamente implementar una nueva función dentro de `llm_backend.py`, manteniendo inalterado el resto del sistema.

---

# 4. Arquitectura general

El flujo de inferencia puede resumirse mediante el siguiente diagrama:

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

              ┌─────────────┐

              ▼             ▼

          LOCAL          CLOUD

          Ollama      OpenRouter

              │             │

              └──────┬──────┘

                     ▼

              Respuesta LLM
```

La aplicación nunca interactúa directamente con un proveedor concreto.

Toda la comunicación con los modelos de lenguaje se realiza exclusivamente mediante `llm_backend.py`.

---

# 5. llm_backend.py

`llm_backend.py` constituye la capa de abstracción encargada de gestionar la comunicación con los distintos proveedores de inferencia.

Entre sus responsabilidades se encuentran:

- seleccionar el backend configurado para la sesión;
- preparar las solicitudes de inferencia;
- enviar el contexto recuperado al modelo correspondiente;
- recibir la respuesta generada;
- devolver un formato homogéneo al resto de la aplicación.

Esta organización permite mantener desacopladas las responsabilidades de recuperación documental e inferencia.

# 6. Backend LOCAL

El backend LOCAL utiliza Ollama como servidor de inferencia ejecutándose en el entorno WSL2.

Características principales:

- ejecución completamente local;
- funcionamiento sin conexión a Internet;
- privacidad de la información;
- utilización de modelos instalados localmente;
- dependencia de la capacidad del hardware disponible.

Modelos actualmente utilizados:

| Función | Modelo |
|----------|--------|
| Embeddings | `nomic-embed-text` |
| Depuración | `qwen2.5-coder:1.5b` |
| Arquitectura | `llama3.2:3b` |
| Documentación | `llama3.2:3b` |

Este backend corresponde al modo de funcionamiento original del proyecto y continúa siendo la opción preferente cuando el hardware disponible permite ejecutar la inferencia localmente.

---

# 7. Backend CLOUD

El backend CLOUD permite delegar la inferencia a un proveedor remoto manteniendo inalterado el resto del pipeline RAG.

Actualmente el proyecto implementa OpenRouter como primer proveedor de este tipo.

La arquitectura, sin embargo, fue diseñada para permitir la incorporación de nuevos proveedores sin modificar `query.py` ni el resto del sistema.

Entre las ventajas del backend CLOUD se encuentran:

- reducción de la carga computacional local;
- acceso a modelos de mayor capacidad;
- independencia respecto al hardware utilizado para el desarrollo;
- reutilización del mismo pipeline RAG.

El backend CLOUD recibe exactamente el mismo contexto generado por el pipeline local, garantizando un comportamiento consistente independientemente del proveedor de inferencia seleccionado.

---

# 8. Gestión de credenciales

Las credenciales necesarias para acceder a proveedores de inferencia remotos no forman parte del código fuente del proyecto.

Actualmente la API Key utilizada por el backend CLOUD se almacena en el archivo:

```text
scripts/.env
```

Ejemplo:

```text
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx
```

El archivo `.env` permanece excluido del repositorio mediante `.gitignore`, evitando la publicación accidental de credenciales.

Esta estrategia facilita además la sustitución de proveedores o la utilización de distintas claves de acceso sin modificar el código de la aplicación.

---

# 9. Validación inicial

Antes de integrar el backend CLOUD en el pipeline principal se realizaron pruebas independientes para validar la comunicación con el proveedor.

Las pruebas incluyeron:

- autenticación mediante API Key;
- verificación del endpoint;
- validación del formato JSON de las solicitudes;
- comprobación del formato de las respuestas;
- selección del modelo de inferencia.

Las primeras pruebas se realizaron utilizando Postman, lo que permitió validar el servicio antes de incorporarlo a `llm_backend.py`.

Durante este proceso también se comprobó la conveniencia de especificar explícitamente el parámetro `max_tokens` para controlar el tamaño máximo de las respuestas.

---

# 10. Flujo de inferencia

El pipeline RAG mantiene el mismo funcionamiento independientemente del backend utilizado.

El flujo general es el siguiente:

```text
Consulta del usuario

         │
         ▼

Generación del embedding

         │
         ▼

Recuperación semántica

         │
         ▼

Construcción del contexto

         │
         ▼

llm_backend.py

         │
         ▼

Backend seleccionado

         │
         ▼

Modelo de lenguaje

         │
         ▼

Respuesta
```

La única etapa que varía entre los distintos modos de operación es la inferencia mediante el modelo de lenguaje.

Todas las etapas anteriores permanecen invariables.

# 11. Selección del backend

La selección del backend forma parte de la configuración de la sesión iniciada por el usuario.

Conceptualmente, la aplicación distingue entre:

```text
Backend de inferencia

1. LOCAL

2. CLOUD
```

A partir de esta selección, `llm_backend.py` dirige automáticamente cada consulta hacia el proveedor correspondiente.

De esta forma, la decisión se mantiene durante toda la sesión y no es necesario modificar el resto del pipeline.

---

# 12. Evolución prevista

La arquitectura actual fue diseñada para facilitar futuras ampliaciones del sistema.

Entre las posibles líneas de evolución se encuentran:

- incorporación de nuevos proveedores de inferencia;
- selección dinámica de modelos;
- registro del proveedor utilizado;
- registro del modelo empleado;
- métricas de consumo de tokens;
- estimación del coste de inferencia cuando corresponda;
- políticas automáticas para seleccionar el backend más adecuado según el contexto de ejecución.

Estas funcionalidades podrán incorporarse manteniendo la misma interfaz expuesta por `llm_backend.py`.

---

# 13. Beneficios de la arquitectura

La incorporación de una capa de abstracción para la inferencia aporta diversas ventajas técnicas.

Entre las principales se encuentran:

- separación entre recuperación documental e inferencia;
- independencia respecto al proveedor de modelos;
- reutilización del pipeline RAG existente;
- incorporación sencilla de nuevos proveedores;
- mantenimiento simplificado;
- menor impacto de futuras migraciones tecnológicas.

Esta organización permite que la evolución del sistema se concentre en componentes específicos sin afectar la arquitectura general.

---

# 14. Estado actual

En la versión actual del proyecto, la arquitectura dispone de:

- pipeline RAG completamente local;
- recuperación semántica mediante `embeddings.jsonl`;
- recuperación de contexto arquitectónico mediante `symbols.jsonl`;
- capa de abstracción de inferencia implementada en `llm_backend.py`;
- backend LOCAL basado en Ollama;
- backend CLOUD basado en OpenRouter;
- integración con el sistema de registro (`logger.py`);
- compatibilidad con la supervisión térmica del entorno de ejecución.

La arquitectura permite seleccionar el backend de inferencia sin modificar el funcionamiento del resto del pipeline.

---

# 15. Conclusión

La incorporación de `llm_backend.py` representa una evolución significativa en la arquitectura del proyecto al separar claramente las responsabilidades de recuperación documental e inferencia mediante modelos de lenguaje.

Gracias a este diseño, el pipeline RAG permanece independiente del proveedor utilizado para generar las respuestas, facilitando la incorporación de nuevos modelos y servicios de inferencia sin alterar la lógica principal de la aplicación.

Esta arquitectura proporciona una base flexible para continuar la evolución del proyecto, manteniendo la coherencia entre la implementación, la documentación técnica y los principios de diseño establecidos desde las primeras versiones.
