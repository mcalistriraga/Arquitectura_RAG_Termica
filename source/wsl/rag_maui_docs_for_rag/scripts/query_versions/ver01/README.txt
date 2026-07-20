scripts/
│
├── query.py                 <-- versión activa
├── logger.py                <-- versión activa
│
└── versions/
    │
    ├── ver01/
    │   ├── query_ver01.py
    │   ├── logger_ver01.py
    │   └── README.md
    │
    └── ver02/
        ├── query_ver02.py
        ├── logger_ver02.py
        └── README.md

# Versión 01 - Línea base RAG

Fecha:
20/07/2026

Componentes:
- query_ver01.py
- logger_ver01.py

Modelo:
- qwen2.5-coder:1.5b
- llama3.2:3b
- nomic-embed-text

Objetivo:
Versión estable antes de instrumentación de rendimiento.

Estado:
Funcional.