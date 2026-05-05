@echo off
title DBV VoiceTranscrypt - Gemma 4 Local Launcher
echo =======================================================
echo    Arrancando Servidor Local Gemma 4...
echo =======================================================

cd gemma4
..\backend\venv\Scripts\python.exe start_gemma.py
pause
