@echo off
title Transcriptor Pro - Instalador Automático
echo =======================================================
echo    Instalando DBV VoiceTranscrypt (WhisperX + CUDA)
echo =======================================================
echo.

echo [1/3] Configurando el entorno virtual de Python...
cd backend

:: Deteccion inteligente de la version de Python (Prioriza 3.12, ideal para la compatibilidad CUDA/WhisperX)
set PYTHON_EXE=python
py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_EXE=py -3.12
)

if not exist venv (
    echo Detectado y usando: %PYTHON_EXE%
    %PYTHON_EXE% -m venv venv
    echo Entorno virtual creado con exito.
) else (
    echo El entorno virtual ya existe.
)

call venv\Scripts\activate.bat

echo.
echo [2/3] Instalando el motor de Inteligencia Artificial (PyTorch CUDA)...
echo Limpiando instalaciones previas corruptas...
pip uninstall -y torch torchvision torchaudio
echo Esto puede tardar varios minutos dependiendo de tu conexion (aprox 2.5GB).
echo.
pip install torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu126

echo.
echo [3/3] Instalando el resto de dependencias (WhisperX, FastAPI, etc)...
echo.
pip install -r requirements.txt

echo.
echo =======================================================
echo  Instalacion completada con exito.
echo  Ya puedes hacer doble clic en "start.cmd" para usarlo.
echo =======================================================
pause
