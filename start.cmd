@echo off
title Transcriptor Pro - Servidor Local
echo Arrancando el servidor Transcriptor Pro...

:: Abre el cliente en el navegador web predeterminado
echo Abriendo el cliente en el navegador...
start http://127.0.0.1:8000

:: Entra en la carpeta del backend, activa el entorno virtual y lanza Uvicorn
cd backend
echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo Iniciando backend FastAPI y modelo Whisper...
.\venv\Scripts\python -m uvicorn main:app --reload-exclude "venv*"

pause
