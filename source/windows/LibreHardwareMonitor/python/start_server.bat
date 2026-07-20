@echo off
cd /d E:\Developer\Tools\LibreHardwareMonitor\python

echo Iniciando Export Temp Server...

start "TempServer" python export_temp_server.py

echo Servidor iniciado en background.
pause