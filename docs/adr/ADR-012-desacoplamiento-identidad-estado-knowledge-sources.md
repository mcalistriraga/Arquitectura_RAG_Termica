# Decisiones fuera del alcance de este ADR

Este ADR define el contrato arquitectónico de identidad y estado, pero no
pretende convertir la implementación concreta de `embed.py` en parte del
contrato arquitectónico.

La implementación actual (`embed.py v2.2`) materializa este contrato y ha sido
validada mediante pruebas controladas.

Quedan fuera del alcance de este ADR:

- la elección futura del modelo de embeddings;
- el algoritmo de búsqueda vectorial;
- el mecanismo futuro de almacenamiento histórico;
- la detección semántica de renames o moves;
- la incorporación de una base de datos de identidades;
- la estrategia definitiva para Knowledge Sources distintas de `symbols`;
- cualquier optimización de rendimiento que no modifique el contrato de
  identidad y estado.

La implementación podrá evolucionar sin modificar este ADR mientras mantenga
el contrato establecido:

`record_id` identifica la entidad y `content_hash` identifica el estado de
su representación textual.
