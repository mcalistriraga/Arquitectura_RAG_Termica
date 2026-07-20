# Componentes Windows

## Servicio de exportación térmica

Ubicación original durante desarrollo:

E:\Developer\Tools\LibreHardwareMonitor\python

## Archivos

### export_temp_server.py

Servicio Flask encargado de:

- consultar LibreHardwareMonitor,
- localizar la temperatura del CPU,
- publicar `/data.json`,
- generar `windows_ip.txt`.

---

### start_server.bat

Script de inicio del servicio.


