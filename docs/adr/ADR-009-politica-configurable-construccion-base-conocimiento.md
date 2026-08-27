# ADR-009 — Política configurable para la construcción de la base de conocimiento

## Estado

Aceptado

## Fecha aproximada

Agosto 2026

---

## Contexto

Durante la evolución del proyecto **Arquitectura_RAG_Termica** se identificó que la calidad de las respuestas generadas por el sistema depende directamente de la calidad del conocimiento indexado.

Inicialmente, `embed.py` recorría el árbol completo del proyecto para generar la base de conocimiento, lo que ocasionaba la incorporación de archivos y directorios que no representan conocimiento útil del software.

Entre ellos:

- `.git`
- `bin`
- `obj`
- archivos temporales
- artefactos de compilación
- otros elementos generados automáticamente por herramientas de desarrollo.

La inclusión de este contenido introduce ruido en la recuperación semántica y reduce la calidad del contexto enviado al modelo de lenguaje.

---

## Problema identificado

La política de selección de archivos estaba implícita dentro de `embed.py`.

Esto presenta varias limitaciones:

- dificulta modificar los criterios de indexación;
- mezcla la lógica de configuración con la lógica del pipeline;
- obliga a modificar código para cambiar qué archivos deben indexarse;
- impide reutilizar la política de filtrado desde otros módulos futuros.

A medida que la arquitectura evolucione podrán aparecer nuevos procesos que necesiten aplicar exactamente los mismos criterios de selección.

---

## Decisión

Se adopta una política de configuración externa para controlar la construcción de la base de conocimiento.

Se incorporará un archivo de configuración dedicado (por ejemplo `embed.filter`) donde se definirán:

- directorios excluidos;
- extensiones permitidas;
- extensiones excluidas;
- archivos específicos a ignorar;
- reglas futuras relacionadas con el proceso de indexación.

El archivo admitirá comentarios mediante el prefijo `#`, permitiendo documentar cada regla.

---

## Nueva responsabilidad arquitectónica

La lectura y procesamiento de archivos de configuración no será responsabilidad de `embed.py`.

Se crea un componente específico denominado `config_manager.py`, encargado de gestionar todos los archivos de configuración del sistema.

Su responsabilidad será:

- localizar archivos de configuración;
- leerlos;
- interpretar comentarios;
- validar su contenido;
- proporcionar una interfaz uniforme al resto del proyecto.

Este componente centralizará toda la lógica relacionada con la configuración del sistema, permitiendo que el resto de los módulos permanezcan desacoplados de los detalles de almacenamiento y formato.

En futuras versiones podrá administrar otros archivos de configuración además de `embed.filter`, manteniendo un único punto de evolución para esta responsabilidad.

---

## Consecuencias

### Ventajas

- Política de indexación completamente configurable.
- Eliminación del ruido generado por artefactos de compilación.
- Mayor calidad de la recuperación semántica.
- Menor acoplamiento entre configuración y lógica del pipeline.
- Facilita futuras ampliaciones del sistema.
- Permite reutilizar el mecanismo de configuración desde otros módulos.
- Centraliza toda la gestión de archivos de configuración.

### Costes

- Se incorpora un nuevo módulo al proyecto.
- Será necesario mantener sincronizados los archivos de configuración con la evolución del sistema.
- Se añade una etapa adicional durante la inicialización de los componentes que dependan de configuración.

---

## Relación con la visión futura

Esta decisión constituye un primer paso hacia una arquitectura donde la adquisición del conocimiento sea completamente configurable e independiente de los algoritmos que posteriormente procesan dicho conocimiento.

La construcción de la base de conocimiento deja de depender exclusivamente de la implementación de `embed.py` y pasa a estar gobernada por una política explícita, documentada y evolutiva.

Esta filosofía es consistente con la visión futura del proyecto, donde las distintas fuentes de conocimiento y los proveedores de contexto podrán incorporar sus propias políticas de configuración sin modificar el núcleo del sistema.

---

## Principios arquitectónicos reforzados

- Responsabilidad única.
- Bajo acoplamiento.
- Configuración sobre implementación.
- Evolución incremental.
- Reutilización.
- Mantenibilidad.
- Observabilidad.

---

## Impacto esperado

A corto plazo, esta decisión permitirá excluir del proceso de indexación directorios como `bin`, `obj`, `.git` y otros archivos no relevantes, mejorando la calidad de la base de conocimiento.

A mediano plazo, proporcionará una infraestructura reutilizable para administrar toda la configuración del proyecto.

A largo plazo, `config_manager.py` podrá convertirse en el punto central de administración de la configuración arquitectónica del sistema, facilitando la incorporación de nuevas capacidades sin aumentar el acoplamiento entre componentes.

---

## Relación con ADR anteriores

Esta decisión complementa los siguientes ADR del proyecto:

- **ADR-007** — Evolución hacia una arquitectura híbrida y desacoplada para la inferencia.
- **ADR-008** — Adopción de ADR como memoria arquitectónica del proyecto.

En conjunto, estas decisiones continúan la evolución de Arquitectura_RAG_Termica hacia una arquitectura modular, extensible y orientada a la construcción de conocimiento de alta calidad para asistir al desarrollador durante todo el ciclo de vida del software.
