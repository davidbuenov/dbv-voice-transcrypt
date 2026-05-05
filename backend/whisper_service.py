# =============================================================================
# DBV VoiceTranscrypt — Aplicación web para la transcripción y análisis de audio de forma 100% local con Whisper y Gemma 4.
# Copyright (c) 2026 David Bueno Vallejo · https://github.com/davidbuenov
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

import whisper
import asyncio
import os

# Inicializar modelo de forma global para no recargarlo en cada petición
# Se usa "base" por defecto, puedes cambiar a "small" o "medium" según tus recursos y VRAM
MODEL_NAME = "base"

import torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Cargando modelo Whisper ({MODEL_NAME}) en dispositivo: {DEVICE}...")
model = whisper.load_model(MODEL_NAME, device=DEVICE)
print(f"Modelo cargado exitosamente en {DEVICE}.")

async def transcribe_audio(file_path: str, websocket=None):
    """
    Transcribe un archivo de audio usando Whisper.
    Si se proporciona un websocket, envía mensajes de estado.
    """
    try:
        if websocket:
            await websocket.send_text("Analizando audio con Whisper... Esto puede tardar unos minutos para archivos grandes.")
        
        # Ejecutamos Whisper en un hilo separado para no bloquear el Event Loop de FastAPI
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: model.transcribe(file_path))
        
        if websocket:
            await websocket.send_text("Generando texto final...")
            
        return result["text"]
    except Exception as e:
        print(f"Error en transcripción: {e}")
        if websocket:
            await websocket.send_text(f"Error: {str(e)}")
        raise e
