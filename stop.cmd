@echo off
title Transcriptor Pro - Detener Servidor Local
echo Buscando procesos en el puerto 8000...

:: Busca el PID (Process ID) asociado al puerto 8000 en estado LISTENING
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Se encontro un proceso utilizando el puerto 8000 (PID: %%a).
    echo Deteniendo el proceso %%a...
    taskkill /F /PID %%a
)

echo.
echo Todos los procesos relacionados han sido detenidos.
pause
