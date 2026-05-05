@echo off
title DBV VoiceTranscrypt - Setup Gemma 4 Local
echo ============================================================
echo   Instalacion Automatica: Servidor y Modelos Gemma 4
echo ============================================================
echo.

cd /d "%~dp0"

set "VENV_PYTHON=..\backend\venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo [ERROR] No se encontro el entorno virtual en ..\backend\venv
    echo         Por favor, instala primero las dependencias del proyecto principal.
    pause
    exit /b 1
)

echo [1/3] Instalando dependencias necesarias (huggingface-hub)...
"%VENV_PYTHON%" -m pip install huggingface-hub>=0.24.0 python-dotenv >nul 2>&1

echo [2/3] Descargando motor llama-server...
"%VENV_PYTHON%" download_llama_server.py

echo [3/3] Descargando modelos GGUF (Gemma 4 + Vision)...
"%VENV_PYTHON%" setup_model.py

echo.
echo ============================================================
echo   Setup de Gemma 4 finalizado con exito.
echo   Ya puedes usar "start_gemma.cmd" en la raiz.
echo ============================================================
pause
