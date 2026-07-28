Conclusión:

La arquitectura RAG local fue validada hasta la etapa de inferencia LLM. El backend local Ollama ejecuta correctamente, pero la generación sostenida del modelo qwen2.5-coder:1.5b supera la capacidad térmica disponible del hardware actual, activándose correctamente el mecanismo de protección thermal_watchdog.py.