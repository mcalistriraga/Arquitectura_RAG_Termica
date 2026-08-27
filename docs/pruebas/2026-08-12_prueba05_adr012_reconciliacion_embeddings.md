# Prueba 05 — Validación ADR-012 y reconciliación incremental de embeddings

**Proyecto:** Arquitectura_RAG_Termica
**Fecha:** 12 de agosto de 2026
**Tipo:** Prueba de integración / validación arquitectónica
**Estado:** EXITOSA
**Implementación:** `embed.py v2.2`
**Decisión arquitectónica:** ADR-012 — Desacoplamiento de identidad y estado de contenido en Knowledge Sources

---

## 1. Objetivo

Validar mediante ejecuciones controladas que la implementación de
`embed.py v2.2` cumple el contrato definido por ADR-012 para separar:

* la identidad estable de una entidad mediante `record_id`;
* el estado de la representación textual mediante `content_hash`;
* el embedding como artefacto derivado.

La prueba también busca demostrar que el proceso de vectorización puede
realizarse de forma incremental, evitando regenerar embeddings cuando una
entidad no ha cambiado.

Se validan específicamente los siguientes comportamientos:

1. generación inicial de embeddings;
2. unicidad de la identidad de las entidades;
3. integridad estructural de la Knowledge Source;
4. integridad estructural del índice vectorial;
5. reutilización de embeddings sin cambios;
6. detección de modificaciones mediante `content_hash`;
7. regeneración selectiva del embedding modificado;
8. conservación de la identidad (`record_id`) ante una modificación del
   contenido;
9. restauración de la Knowledge Source original;
10. verificación final de estabilidad del índice.

---

## 2. Componentes involucrados

### 2.1. Knowledge Source primaria

La fuente primaria utilizada durante la prueba fue:

```text
~/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.jsonl
```

Esta Knowledge Source contiene las entidades estructuradas extraídas del
proyecto `MauiAppGestorMovil`.

Durante la validación se comprobó que contenía:

```text
63 registros
63 identidades únicas
0 duplicados de identidad
```

La Knowledge Source constituye la fuente primaria del conocimiento.

---

### 2.2. Artefacto vectorial

El artefacto derivado utilizado por `embed.py` fue:

```text
~/rag_workspace/MauiAppGestorMovil/knowledge/embeddings/embeddings.jsonl
```

Este archivo contiene los embeddings generados a partir de la Knowledge
Source.

Entre los campos estructurales utilizados por ADR-012 se encuentran:

```text
record_id
content_hash
source_type
file
source_path
source_line
content
embedding_model
embedding_dimension
embedding
```

El artefacto vectorial no constituye la fuente primaria del conocimiento.

Puede eliminarse y reconstruirse a partir de la Knowledge Source sin perder
la información estructural primaria.

---

### 2.3. Implementación evaluada

La implementación utilizada fue:

```text
~/rag_maui_docs_for_rag/scripts/embed.py
```

Versión:

```text
embed.py v2.2
```

La ejecución utiliza el modelo:

```text
nomic-embed-text
```

con una dimensión observada de:

```text
768
```

---

### 2.4. Configuración

La implementación obtiene de `embed.conf` los parámetros correspondientes
al modelo, endpoint de Ollama, carga objetivo de CPU y pacing.

Durante las pruebas se observó:

```text
Modelo                 : nomic-embed-text
Pacing por entidad     : 0.9s
```

El pacing se mantuvo durante la generación de embeddings para reducir la
carga sostenida sobre el sistema.

---

## 3. Preparación de la prueba

Antes de realizar la reconstrucción del índice se conservaron respaldos de
los artefactos existentes.

### 3.1. Respaldo del índice previo

Se creó el respaldo:

```text
~/rag_workspace/MauiAppGestorMovil/knowledge/embeddings/embeddings.pre-v2.2-2026-08-12.jsonl
```

El respaldo contenía:

```text
57 registros
```

Este dato es relevante porque el índice anterior correspondía a un estado
previo de la implementación y no contenía todavía la representación completa
de las 63 entidades presentes en la Knowledge Source validada.

---

### 3.2. Respaldo de la Knowledge Source

Antes de realizar la modificación controlada utilizada en la prueba de
reconciliación se creó:

```text
~/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.pre-test-modificacion-2026-08-12.jsonl
```

El respaldo contenía:

```text
63 registros
```

Este respaldo permitió restaurar posteriormente la Knowledge Source a su
estado original.

---

## 4. Validación previa de la Knowledge Source

Antes de ejecutar la vectorización se realizaron validaciones independientes
sobre `symbols_raw.jsonl`.

### 4.1. Conteo de registros

Comando utilizado:

```bash
wc -l ~/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.jsonl
```

Resultado:

```text
63 /home/manuelc/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.jsonl
```

Por tanto:

```text
Entidades = 63
```

---

### 4.2. Inspección estructural

La utilidad `jq` no se encontraba instalada en el entorno:

```text
Command 'jq' not found
```

Por esta razón se utilizó Python para inspeccionar directamente el primer
registro JSONL.

El registro correspondió a:

```text
entity_type : class
name        : Program
namespace   : MauiAppGestorMovil
file        : Platforms/iOS/Program.cs
access      : public
```

La estructura confirmó que la Knowledge Source contiene registros
estructurados y no únicamente texto libre.

---

## 5. Validación de identidad ADR-012

Se ejecutó una validación específica de la identidad estructural definida por
ADR-012.

Resultado:

```text
=== VALIDACIÓN ADR-012 ===
Entidades leídas       : 63
record_id únicos       : 63
Duplicados de identidad: 0
RESULTADO: OK - todas las entidades tienen identidad única.
```

La prueba demostró que los 63 registros de la Knowledge Source producen
identidades deterministas únicas.

Por tanto:

```text
63 entidades
63 record_id
0 colisiones
```

La validación es especialmente importante porque una de las motivaciones
principales de ADR-012 es evitar que la representación textual utilizada para
el embedding determine accidentalmente la identidad de una entidad.

---

## 6. Validación de campos estructurales

Se realizó una segunda validación independiente para comprobar la presencia
de los campos estructurales requeridos.

Resultado:

```text
=== VALIDACIÓN DE CAMPOS ESTRUCTURALES ADR-012 ===
Registros evaluados : 63
Registros con error : 0
RESULTADO: OK - los 63 registros contienen todos los campos estructurales.
```

Resultado consolidado:

```text
Registros evaluados : 63
Registros válidos   : 63
Errores             : 0
```

La Knowledge Source se consideró estructuralmente válida para continuar con
la reconstrucción del índice.

---

## 7. Reconstrucción inicial del índice

Para validar el nuevo contrato de identidad se eliminó únicamente el
artefacto derivado:

```text
~/rag_workspace/MauiAppGestorMovil/knowledge/embeddings/embeddings.jsonl
```

Comando utilizado:

```bash
rm -f ~/rag_workspace/MauiAppGestorMovil/knowledge/embeddings/embeddings.jsonl
```

La Knowledge Source primaria no fue eliminada ni modificada durante esta
operación.

La eliminación del artefacto derivado permitió comprobar el comportamiento
de una reconstrucción completa bajo `embed.py v2.2`.

---

## 8. Primera ejecución de `embed.py v2.2`

Se ejecutó:

```bash
python3 ~/rag_maui_docs_for_rag/scripts/embed.py
```

La ejecución informó:

```text
=== Vectorización embed.py v2.2 ===
Contrato de identidad : ADR-012
Knowledge Source       : /home/manuelc/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.jsonl
Artefacto destino      : /home/manuelc/rag_workspace/MauiAppGestorMovil/knowledge/embeddings/embeddings.jsonl
Source Type            : symbols
Modelo                 : nomic-embed-text
Pacing por entidad     : 0.9s
Registros vectoriales en índice previo : 0
Entidades leídas       : 63
```

La ejecución clasificó las 63 entidades como nuevas:

```text
Nuevos       : 63
Sin Cambios  : 0
Modificados  : 0
Eliminados   : 0
```

Resultado:

```text
Vectorización embed.py v2.2 completada exitosamente.
```

### Resultado esperado

El comportamiento coincide con el contrato de ADR-012:

```text
record_id no existe en el índice
        ↓
NUEVO
        ↓
generar embedding
```

Por tanto:

```text
63 entidades
→ 63 embeddings generados
```

---

## 9. Validación del artefacto generado

Después de la primera ejecución se comprobó el número de registros:

```bash
wc -l ~/rag_workspace/MauiAppGestorMovil/knowledge/embeddings/embeddings.jsonl
```

Resultado:

```text
63 /home/manuelc/rag_workspace/MauiAppGestorMovil/knowledge/embeddings/embeddings.jsonl
```

El número de registros del índice coincidió con el número de entidades de la
Knowledge Source:

```text
Knowledge Source : 63
Índice vectorial : 63
```

No se observaron pérdidas de registros durante la reconstrucción.

---

## 10. Inspección del primer registro vectorial

Se inspeccionó el primer registro generado utilizando Python.

Resultado observado:

```text
=== PRIMER REGISTRO DEL NUEVO ÍNDICE ===
record_id           : 44ca9ced2ce85bc2eb0b11076c54b6c8a5d82aef2b7a4e8c09ec5f2a8a605c7f
content_hash        : 065b35ae1eafba5256ed45e81ba32695f4c838cf3a46c60066ff4dbb7f9bc85a
source_type         : symbols
file                : Platforms/iOS/Program.cs
source_path         : Platforms/iOS/Program.cs
source_line         : 1
embedding_model     : nomic-embed-text
embedding_dimension : 768
embedding_length    : 768
content_length      : 103
```

Este resultado confirmó que el registro vectorial contiene simultáneamente:

* identidad (`record_id`);
* estado textual (`content_hash`);
* procedencia;
* modelo utilizado;
* dimensión del vector;
* vector generado;
* representación textual utilizada para generarlo.

Esto constituye evidencia directa de la separación entre identidad y estado
definida por ADR-012.

---

## 11. Validación global del índice ADR-012

Una vez generado el nuevo índice vectorial se realizó una validación global
de su estructura.

La validación comprobó:

* cantidad de registros;
* unicidad de `record_id`;
* ausencia de duplicados;
* modelos de embedding utilizados;
* dimensiones de los vectores;
* validez del JSON;
* presencia de campos obligatorios;
* validez de los embeddings;
* consistencia entre la dimensión declarada y la longitud real del vector.

Resultado obtenido:

```text
=== VALIDACIÓN GLOBAL DEL ÍNDICE ADR-012 ===
Registros leídos          : 63
Record IDs únicos         : 63
Record IDs duplicados     : 0
Modelos encontrados       : {'nomic-embed-text'}
Dimensiones encontradas  : {768}
JSON inválidos            : 0
Campos obligatorios falt. : 0
Embeddings inválidos      : 0
Dimensiones inconsistentes: 0

RESULTADO: OK - índice ADR-012 estructuralmente válido.
```

El resultado demuestra que el índice reconstruido cumple estructuralmente
con el contrato esperado.

En particular:

```text
63 registros
63 record_id únicos
0 duplicados
1 modelo
768 dimensiones
0 JSON inválidos
0 embeddings inválidos
```

---

## 12. Segunda ejecución sin modificaciones

Una de las pruebas fundamentales de ADR-012 consiste en ejecutar nuevamente
`embed.py` sin modificar la Knowledge Source.

El objetivo es demostrar que los embeddings existentes pueden reutilizarse
cuando:

```text
record_id       = igual
content_hash    = igual
embedding_model = igual
embedding       = válido
```

Se ejecutó nuevamente:

```bash
python3 ~/rag_maui_docs_for_rag/scripts/embed.py
```

Resultado:

```text
=== Vectorización embed.py v2.2 ===
Contrato de identidad : ADR-012
Knowledge Source       : /home/manuelc/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.jsonl
Artefacto destino      : /home/manuelc/rag_workspace/MauiAppGestorMovil/knowledge/embeddings/embeddings.jsonl
Source Type            : symbols
Modelo                 : nomic-embed-text
Pacing por entidad     : 0.9s
Registros vectoriales en índice previo      : 63
Entidades leídas       : 63

=== Resumen de Reconciliación ===
Total procesados : 63
  Nuevos         : 0
  Sin Cambios    : 63
  Modificados    : 0
  Eliminados     : 0

Vectorización embed.py v2.2 completada exitosamente.
```

### Resultado

La prueba produjo exactamente el comportamiento esperado:

```text
63 → Sin Cambios
0   → Nuevos
0   → Modificados
0   → Eliminados
```

Esto demuestra que `embed.py v2.2` reconoce las entidades existentes y
reutiliza sus embeddings sin regenerarlos.

La prueba constituye evidencia del funcionamiento incremental del proceso.

El comportamiento puede representarse como:

```text
Knowledge Source
       |
       v
   record_id
       |
       v
¿Existe en índice?
       |
      SÍ
       |
       v
¿content_hash coincide?
       |
      SÍ
       |
       v
¿modelo y vector válidos?
       |
      SÍ
       |
       v
SIN CAMBIOS
       |
       v
Reutilizar embedding
```

---

## 13. Preparación de la modificación controlada

Para comprobar el comportamiento ante una modificación se creó previamente
un respaldo de la Knowledge Source original:

```text
~/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.pre-test-modificacion-2026-08-12.jsonl
```

El respaldo contenía:

```text
63 registros
```

El propósito del respaldo fue permitir que la Knowledge Source pudiera
restaurarse exactamente a su estado original después de finalizar la prueba.

## 14. Primera modificación controlada

Se modificó exclusivamente el primer registro de la Knowledge Source.

Se agregó el campo:

```text
test_adr012
```

con el valor:

```text
MODIFICACION_CONTROLADA_ADR012
```

La modificación no cambió:

```text
namespace
entity_type
name
file
```

Por tanto, los componentes estructurales utilizados para generar el
`record_id` permanecieron iguales.

La modificación se realizó de forma controlada mediante Python.

Resultado:

```text
=== MODIFICACIÓN CONTROLADA ADR-012 ===
Entidad       : Program
Archivo       : Platforms/iOS/Program.cs
Access nuevo  : internal
Campo de test : MODIFICACION_CONTROLADA_ADR012
```

La modificación se utilizó únicamente para provocar un cambio en la
representación semántica generada por `embed.py`.

---

## 15. Ejecución posterior a la modificación

Después de modificar la Knowledge Source se ejecutó nuevamente:

```bash
python3 ~/rag_maui_docs_for_rag/scripts/embed.py
```

Resultado:

```text
=== Vectorización embed.py v2.2 ===
Contrato de identidad : ADR-012
Knowledge Source       : /home/manuelc/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.jsonl
Artefacto destino      : /home/manuelc/rag_workspace/MauiAppGestorMovil/knowledge/embeddings/embeddings.jsonl
Source Type            : symbols
Modelo                 : nomic-embed-text
Pacing por entidad     : 0.9s
Registros vectoriales en índice previo      : 63
Entidades leídas       : 63

[MODIFICADO] Program (Platforms/iOS/Program.cs) -> content_hash cambió

=== Resumen de Reconciliación ===
Total procesados : 63
  Nuevos         : 0
  Sin Cambios    : 62
  Modificados    : 1
  Eliminados     : 0

Vectorización embed.py v2.2 completada exitosamente.
```

---

## 16. Resultado de la prueba de modificación

El resultado obtenido fue:

```text
Nuevos       : 0
Sin Cambios  : 62
Modificados  : 1
Eliminados   : 0
```

Este resultado coincide con el comportamiento definido en ADR-012.

Solamente la entidad modificada fue identificada como `MODIFICADO`.

Las otras 62 entidades mantuvieron sus embeddings sin regeneración.

El flujo observado fue:

```text
Program
   |
   v
record_id existente
   |
   v
content_hash diferente
   |
   v
MODIFICADO
   |
   v
regenerar embedding
```

Mientras que para las demás entidades:

```text
record_id existente
       +
content_hash igual
       +
modelo igual
       +
vector válido
       |
       v
SIN CAMBIOS
       |
       v
reutilizar embedding
```

Esta prueba demuestra que el cambio de contenido no provoca la creación de
una nueva identidad.

---

## 17. Validación conceptual de la separación identidad / estado

La prueba de modificación constituye una validación práctica del principio
central de ADR-012.

La entidad:

```text
Program
```

continuó siendo identificada mediante su misma estructura canónica:

```text
source_type
namespace
entity_type
name
file
```

Mientras que la representación textual utilizada para generar el embedding
cambió debido a la modificación controlada.

Por tanto, el comportamiento esperado es:

```text
record_id      = igual
content_hash   = diferente
embedding      = regenerado
```

Esto corresponde exactamente al concepto:

```text
MISMA ENTIDAD
      +
NUEVO ESTADO DE CONTENIDO
```

y no:

```text
NUEVA ENTIDAD
```

Esta distinción constituye el objetivo principal de ADR-012.

---

## 18. Restauración de la Knowledge Source

Finalizada la prueba de modificación, se restauró la Knowledge Source
utilizando el respaldo creado antes del experimento:

```text
~/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.pre-test-modificacion-2026-08-12.jsonl
```

El archivo original fue restaurado mediante:

```bash
cp ~/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.pre-test-modificacion-2026-08-12.jsonl \
   ~/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.jsonl
```

Después de la restauración se verificó nuevamente el número de registros:

```bash
wc -l ~/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.jsonl
```

Resultado esperado y observado:

```text
63
```

La Knowledge Source volvió a contener las 63 entidades originales.

---

## 19. Ejecución posterior a la restauración

Después de restaurar la Knowledge Source original se ejecutó nuevamente:

```bash
python3 ~/rag_maui_docs_for_rag/scripts/embed.py
```

Resultado:

```text
=== Vectorización embed.py v2.2 ===
Contrato de identidad : ADR-012
Knowledge Source       : /home/manuelc/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.jsonl
Artefacto destino      : /home/manuelc/rag_workspace/MauiAppGestorMovil/knowledge/embeddings/embeddings.jsonl
Source Type            : symbols
Modelo                 : nomic-embed-text
Pacing por entidad     : 0.9s
Registros vectoriales en índice previo      : 63
Entidades leídas       : 63

=== Resumen de Reconciliación ===
Total procesados       : 63
  Nuevos               : 0
  Sin Cambios          : 63
  Modificados          : 0
  Eliminados           : 0

Vectorización embed.py v2.2 completada exitosamente.
```

El resultado confirma que la restauración devolvió la Knowledge Source al
estado correspondiente al índice estable.

---

## 20. Interpretación de la restauración

La ejecución posterior a la restauración produjo:

```text
Nuevos       : 0
Sin Cambios  : 63
Modificados  : 0
Eliminados   : 0
```

Esto demuestra que el índice volvió a encontrarse en correspondencia con la
Knowledge Source original.

La secuencia completa de la prueba fue:

```text
                 Knowledge Source original
                          |
                          v
                    Primera ejecución
                          |
                          v
                     63 NUEVOS
                          |
                          v
                  Índice completo
                          |
                          v
               Segunda ejecución
                          |
                          v
                   63 SIN CAMBIOS
                          |
                          v
              Modificación controlada
                          |
                          v
                1 MODIFICADO
                62 SIN CAMBIOS
                          |
                          v
                  Restauración
                          |
                          v
               Nueva reconciliación
                          |
                          v
                   63 SIN CAMBIOS
```

La secuencia confirma que el estado del índice puede reconciliarse
nuevamente después de una modificación controlada de la fuente.

---

## 21. Estados de reconciliación validados

Las pruebas ejecutadas permitieron demostrar tres de los cuatro estados de
reconciliación definidos por `embed.py v2.2`.

### 21.1. NUEVO

Validado durante la primera reconstrucción:

```text
63 NUEVOS
```

Condición:

```text
record_id no existe en el índice previo
```

Acción:

```text
generar embedding
```

---

### 21.2. SIN CAMBIOS

Validado durante:

* segunda ejecución;
* ejecución posterior a la restauración.

Resultado:

```text
63 SIN CAMBIOS
```

Condición:

```text
record_id existe
content_hash coincide
modelo coincide
vector válido
```

Acción:

```text
reutilizar embedding
```

---

### 21.3. MODIFICADO

Validado mediante la modificación controlada:

```text
1 MODIFICADO
62 SIN CAMBIOS
```

Condición:

```text
record_id existe
content_hash cambió
```

Acción:

```text
regenerar embedding
```

---

### 21.4. ELIMINADO

El estado `ELIMINADO` forma parte de la lógica implementada en `embed.py v2.2`,
mediante la comparación entre:

```text
record_id existentes en el índice previo
```

y:

```text
record_id presentes en la Knowledge Source actual
```

Sin embargo, **no se ejecutó una prueba destructiva de eliminación de una
entidad durante esta validación**.

Por tanto, este documento no declara experimentalmente validado el estado
`ELIMINADO`.

La implementación sí contiene la lógica correspondiente:

```text
IDs existentes en índice
        -
IDs presentes en Knowledge Source
        =
IDs eliminados
```

pero su validación experimental queda pendiente de una prueba específica si
posteriormente se considera necesaria.

## 22. Resumen consolidado de resultados

Las principales ejecuciones realizadas durante la prueba produjeron los
siguientes resultados:

| Escenario                        | Nuevos | Sin cambios | Modificados | Eliminados | Resultado |
| -------------------------------- | -----: | ----------: | ----------: | ---------: | --------- |
| Primera indexación               |     63 |           0 |           0 |          0 | EXITOSA   |
| Segunda ejecución sin cambios    |      0 |          63 |           0 |          0 | EXITOSA   |
| Modificación controlada          |      0 |          62 |           1 |          0 | EXITOSA   |
| Restauración de Knowledge Source |      0 |          63 |           0 |          0 | EXITOSA   |

La secuencia demuestra que `embed.py v2.2` puede reconciliar el índice
vectorial con el estado actual de la Knowledge Source sin regenerar
innecesariamente los embeddings.

---

## 23. Validaciones estructurales realizadas

Durante la prueba se realizaron varias validaciones independientes.

### Knowledge Source

```text
Registros                 : 63
Record IDs únicos         : 63
Duplicados                : 0
Campos estructurales falt.: 0
```

Resultado:

```text
OK
```

### Índice vectorial

```text
Registros                 : 63
Record IDs únicos         : 63
Record IDs duplicados     : 0
Modelos                   : nomic-embed-text
Dimensiones               : 768
JSON inválidos            : 0
Campos obligatorios falt. : 0
Embeddings inválidos      : 0
Dimensiones inconsistentes: 0
```

Resultado:

```text
OK
```

---

## 24. Validación del contrato de identidad

La prueba permitió comprobar que la identidad de la entidad `Program` no
dependió de la modificación realizada sobre su representación semántica.

La identidad está determinada por la clave estructural definida por
ADR-012:

```text
source_type::namespace::entity_type::name::file
```

Para la Knowledge Source `symbols`, esta estructura contiene:

```text
source_type
namespace
entity_type
name
file
```

La modificación realizada sobre la entidad no alteró estos componentes.

Por tanto, el sistema pudo reconocerla como la misma entidad y no como una
entidad nueva.

Esto constituye la evidencia experimental principal de la separación:

```text
IDENTIDAD
    |
    +--> record_id
    |
    |       independiente de
    |
    v
ESTADO DE CONTENIDO
    |
    +--> content_hash
```

---

## 25. Validación del contrato de estado

El estado de la representación textual se determinó mediante:

```text
content_hash = SHA256(contenido_normalizado)
```

La modificación controlada alteró la representación semántica generada por
`embed.py`.

Como consecuencia:

```text
content_hash anterior
        !=
content_hash nuevo
```

El sistema detectó correctamente la diferencia y clasificó la entidad como:

```text
MODIFICADO
```

La regeneración del embedding se produjo únicamente para esa entidad.

---

## 26. Validación de la naturaleza derivada del embedding

La prueba también confirmó el principio arquitectónico de que el embedding
es un artefacto derivado.

La secuencia de reconstrucción fue:

```text
Knowledge Source
       |
       v
registros estructurados
       |
       v
record_id
       +
content_hash
       |
       v
representación textual
       |
       v
modelo de embedding
       |
       v
embedding
       |
       v
embeddings.jsonl
```

El índice vectorial pudo eliminarse antes de la reconstrucción inicial sin
afectar a la Knowledge Source.

La reconstrucción produjo nuevamente los 63 registros.

Por tanto:

```text
Knowledge Source
        =
fuente primaria
```

mientras que:

```text
embeddings.jsonl
        =
artefacto derivado y reconstruible
```

---

## 27. Validación de la ejecución incremental

La ejecución incremental permitió evitar llamadas innecesarias al modelo de
embeddings.

En la segunda ejecución:

```text
63 entidades
0 modificaciones
```

el resultado fue:

```text
0 nuevos
63 sin cambios
0 modificados
```

Por tanto, ninguna de las 63 entidades necesitó ser regenerada.

En la modificación controlada:

```text
63 entidades
1 modificación
```

el resultado fue:

```text
0 nuevos
62 sin cambios
1 modificado
```

Esto demuestra que la regeneración puede limitarse a las entidades cuyo
estado de representación cambió.

---

## 28. Validación de estabilidad ante desplazamientos de contenido

ADR-012 establece que la identidad no debe depender de la representación
textual utilizada para generar el embedding.

La prueba de modificación controlada confirmó este principio para un cambio
de contenido que no alteró los atributos estructurales utilizados por
`record_id`.

La entidad continuó siendo identificada como:

```text
Program
```

en:

```text
Platforms/iOS/Program.cs
```

mientras su representación semántica fue modificada.

El sistema respondió:

```text
mismo record_id
+
nuevo content_hash
=
entidad modificada
```

Este comportamiento evita que una evolución del formateador transforme
artificialmente una entidad existente en una entidad nueva.

---

## 29. Aspectos de ADR-012 validados experimentalmente

Los siguientes aspectos fueron comprobados directamente durante esta prueba:

| Aspecto                      | Validación            | Resultado |
| ---------------------------- | --------------------- | --------- |
| Identidad determinista       | 63 entidades / 63 IDs | OK        |
| Ausencia de colisiones       | 0 duplicados          | OK        |
| Campos estructurales         | 63/63 válidos         | OK        |
| Reconstrucción completa      | 63 nuevos             | OK        |
| Reutilización incremental    | 63 sin cambios        | OK        |
| Detección de modificación    | 1 modificado          | OK        |
| Regeneración selectiva       | 1 de 63               | OK        |
| Conservación de identidad    | Entidad `Program`     | OK        |
| `content_hash` independiente | Cambio detectado      | OK        |
| Modelo persistido            | `nomic-embed-text`    | OK        |
| Dimensión persistida         | 768                   | OK        |
| Integridad del índice        | 63 registros válidos  | OK        |
| Restauración de fuente       | 63 registros          | OK        |

---

## 30. Aspectos no validados experimentalmente

Para mantener la trazabilidad y evitar atribuir a esta prueba resultados que
no fueron ejecutados, quedan explícitamente fuera de la evidencia
experimental de Prueba 05:

### 30.1. Estado ELIMINADO

No se eliminó físicamente una entidad de `symbols_raw.jsonl` para comprobar
su detección durante la reconciliación.

La lógica está implementada en `embed.py v2.2`, pero su comportamiento no se
declara validado experimentalmente en esta prueba.

### 30.2. Cambio de modelo

No se modificó `embedding_model` durante la prueba para provocar una
regeneración completa basada exclusivamente en el cambio de modelo.

### 30.3. Cambio de dimensión

No se utilizó un modelo alternativo con una dimensión diferente para validar
un cambio de dimensión.

### 30.4. Corrupción del embedding

No se introdujo deliberadamente un vector corrupto o inconsistente para
validar el mecanismo de recuperación.

### 30.5. Movimiento de archivos

No se movió una entidad entre archivos para validar experimentalmente el
comportamiento de la identidad cuando `file` forma parte del `record_id`.

### 30.6. Renombrado de entidades

No se renombró una entidad para comprobar experimentalmente la generación de
una nueva identidad.

Estos escenarios pueden documentarse mediante pruebas posteriores si la
evolución del proyecto los hace necesarios.

---

## 31. Observación sobre la prueba de modificación

La modificación utilizada en esta prueba fue deliberadamente controlada.

No representa necesariamente un cambio normal producido por el extractor
de símbolos durante una ejecución real.

Su propósito fue aislar el mecanismo de reconciliación y demostrar que una
alteración de la representación de una entidad provoca:

```text
content_hash diferente
```

sin provocar:

```text
record_id diferente
```

La prueba debe interpretarse, por tanto, como una prueba funcional del
contrato de reconciliación y no como una prueba de calidad semántica del
contenido generado por el extractor.

---

## 32. Resultado final

La Prueba 05 se considera:

```text
EXITOSA
```

La implementación `embed.py v2.2` demostró experimentalmente los principales
comportamientos requeridos por ADR-012:

```text
                    ADR-012
                       |
          +------------+------------+
          |                         |
          v                         v
      IDENTIDAD                  ESTADO
          |                         |
          v                         v
     record_id                content_hash
          |                         |
          +------------+------------+
                       |
                       v
                RECONCILIACIÓN
                       |
          +------------+------------+
          |            |            |
          v            v            v
       NUEVO      SIN CAMBIOS   MODIFICADO
          |            |            |
          v            v            v
      generar       reutilizar   regenerar
      embedding     embedding    embedding
```

Los resultados obtenidos fueron consistentes con el contrato arquitectónico
definido.

---

## 33. Conclusión

La prueba demuestra que la implementación actual de `embed.py v2.2` puede
mantener un índice vectorial sincronizado con la Knowledge Source `symbols`
utilizando una separación explícita entre identidad y estado.

La evidencia obtenida confirma:

1. Las 63 entidades poseen identidades deterministas únicas.
2. No se produjeron colisiones de `record_id`.
3. La Knowledge Source contiene todos los campos estructurales requeridos.
4. El índice vectorial puede reconstruirse desde cero.
5. Los embeddings existentes pueden reutilizarse cuando no existe ningún
   cambio.
6. Una modificación de contenido produce un cambio de `content_hash`.
7. La modificación no genera una nueva identidad cuando los atributos
   estructurales permanecen iguales.
8. Solamente la entidad modificada requiere regeneración.
9. El índice mantiene una estructura consistente de 768 dimensiones con
   `nomic-embed-text`.
10. La Knowledge Source puede restaurarse después de una prueba controlada.
11. Una nueva reconciliación posterior a la restauración vuelve a producir
    63 registros `SIN CAMBIOS`.

Por tanto, la implementación actual proporciona evidencia suficiente para
considerar **validado experimentalmente el núcleo del contrato de ADR-012**.

---

## 34. Estado de la implementación después de la prueba

Al finalizar la prueba se dejó restaurada la Knowledge Source original:

```text
~/rag_workspace/MauiAppGestorMovil/knowledge/symbols/symbols_raw.jsonl
```

con:

```text
63 registros
```

El índice vectorial quedó nuevamente reconciliado con dicha fuente:

```text
~/rag_workspace/MauiAppGestorMovil/knowledge/embeddings/embeddings.jsonl
```

con:

```text
63 registros
```

La última ejecución de `embed.py v2.2` produjo:

```text
Nuevos       : 0
Sin Cambios  : 63
Modificados  : 0
Eliminados   : 0
```

El estado final es, por tanto:

```text
Knowledge Source : estable
Índice vectorial : estable
Reconciliación   : correcta
ADR-012          : validado en los escenarios probados
```

---

## 35. Archivos y componentes relacionados

### Implementación

```text
scripts/embed.py
scripts/embed.conf
```

### Knowledge Source

```text
knowledge/symbols/symbols_raw.jsonl
```

### Artefacto vectorial

```text
knowledge/embeddings/embeddings.jsonl
```

### Respaldos utilizados durante la prueba

```text
knowledge/embeddings/embeddings.pre-v2.2-2026-08-12.jsonl
knowledge/symbols/symbols_raw.pre-test-modificacion-2026-08-12.jsonl
```

> **Nota:** Debe conservarse únicamente el nombre de respaldo que realmente
> exista en el repositorio. No debe documentarse como evidencia un archivo
> que no haya sido creado durante la prueba.

### Decisión arquitectónica

```text
docs/adr/ADR-012-desacoplamiento-identidad-estado-knowledge-sources.md
```

---

## 36. Evidencia principal de la prueba

La evidencia experimental se resume en cuatro ejecuciones principales.

### Ejecución 1 — Reconstrucción

```text
Nuevos       : 63
Sin Cambios  : 0
Modificados  : 0
Eliminados   : 0
```

### Ejecución 2 — Sin modificaciones

```text
Nuevos       : 0
Sin Cambios  : 63
Modificados  : 0
Eliminados   : 0
```

### Ejecución 3 — Modificación controlada

```text
Nuevos       : 0
Sin Cambios  : 62
Modificados  : 1
Eliminados   : 0
```

### Ejecución 4 — Restauración

```text
Nuevos       : 0
Sin Cambios  : 63
Modificados  : 0
Eliminados   : 0
```

Estas cuatro ejecuciones constituyen la evidencia principal de la
reconciliación incremental validada en esta prueba.

---

## 37. Relación con la evolución arquitectónica

Esta prueba representa un punto de control importante en la evolución de la
arquitectura RAG.

El comportamiento anterior estaba condicionado por la relación entre el
contenido textual y la identidad del registro.

Con ADR-012 y `embed.py v2.2`, la arquitectura adopta explícitamente:

```text
Entidad
   |
   +--> Identidad estable
   |       |
   |       +--> record_id
   |
   +--> Representación actual
           |
           +--> content_hash
                   |
                   +--> embedding
```

Esta separación permite que los formateadores y representaciones semánticas
evolucionen sin que cada cambio textual implique necesariamente una nueva
identidad.

El embedding permanece como un artefacto derivado, reemplazable y
reconstruible.

---

## 38. Próximas pruebas posibles

No se requiere ejecutar inmediatamente ninguna de las siguientes pruebas.

Podrán realizarse posteriormente si la evolución del proyecto lo justifica:

1. eliminación controlada de una entidad;
2. cambio controlado del modelo de embeddings;
3. validación de cambio de dimensión;
4. corrupción controlada de un vector;
5. movimiento controlado de una entidad entre archivos;
6. renombrado controlado de una entidad;
7. reconstrucción completa utilizando un nuevo formateador;
8. validación de comportamiento ante cambios de `source_path` y
   `source_line`.

Estas pruebas deberán documentarse por separado y no deben incorporarse a
Prueba 05 como resultados ya obtenidos.

---

## 39. Referencias

* ADR-012 — Desacoplamiento de identidad y estado de contenido en Knowledge
  Sources.
* `scripts/embed.py` v2.2.
* `scripts/embed.conf`.
* `knowledge/symbols/symbols_raw.jsonl`.
* `knowledge/embeddings/embeddings.jsonl`.
* Respaldos generados durante la prueba.
* Resultados de ejecución registrados en la terminal durante el 12 de agosto
  de 2026.

---

## 40. Estado final

**Prueba 05 — EXITOSA**

La implementación `embed.py v2.2` queda respaldada por evidencia
experimental para los escenarios de:

```text
NUEVO
SIN CAMBIOS
MODIFICADO
```

La prueba confirma que la separación entre:

```text
record_id
```

y:

```text
content_hash
```

funciona de acuerdo con el principio central establecido por ADR-012.

El estado `ELIMINADO` permanece implementado pero pendiente de una prueba
experimental específica.

El índice vectorial y la Knowledge Source quedaron finalmente reconciliados
y estables.


