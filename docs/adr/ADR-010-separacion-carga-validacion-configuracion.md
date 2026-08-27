# ADR-010 — Separación entre carga y validación de configuración

## Estado

Aceptado

## Fecha aproximada

Agosto 2026

---

## Contexto

Durante la implementación de la política configurable definida en
**ADR-009 — Política configurable para la construcción de la base de conocimiento**
se incorporó inicialmente un componente denominado `config_manager.py`
con el objetivo de centralizar la gestión de archivos de configuración
del sistema.

Durante la evolución del diseño se identificó que la gestión completa
de configuración involucra responsabilidades diferentes que no deben
permanecer acopladas dentro de un único componente.

La lectura de configuración y la validación de configuración representan
problemas independientes.

La carga de configuración requiere:

- leer archivos externos;
- interpretar una sintaxis definida;
- ignorar comentarios;
- interpretar parámetros;
- convertir tipos básicos;
- entregar la configuración a los módulos consumidores.

La validación requiere:

- verificar parámetros obligatorios;
- comprobar tipos esperados;
- validar rangos permitidos;
- detectar inconsistencias;
- generar diagnósticos para el administrador.

Mezclar ambas responsabilidades dentro del mismo módulo aumenta el
acoplamiento y dificulta la evolución del sistema.

---

## Problema identificado

Los archivos `.conf` serán editados manualmente por usuarios administradores.

Esto introduce la posibilidad de errores como:

- nombres incorrectos de parámetros;
- valores con tipos inesperados;
- listas mal definidas;
- parámetros incompletos;
- configuraciones incompatibles con un módulo específico.

Estos errores deben poder detectarse antes de la ejecución normal
del sistema.

La herramienta encargada de cargar configuración no debe conocer las
reglas particulares de cada módulo, ya que esto violaría el principio
de responsabilidad única.

---

## Decisión

Se establece una separación arquitectónica entre:

1. **Carga de configuración**
2. **Validación y diagnóstico de configuración**

---

## Nuevo componente: config_loader.py

`config_loader.py` será responsable exclusivamente de cargar archivos
de configuración externos.

Sus responsabilidades son:

- leer archivos `.conf`;
- interpretar parámetros con formato:

