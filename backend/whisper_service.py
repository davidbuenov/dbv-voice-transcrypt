# =============================================================================
# DBV VoiceTranscrypt — Aplicación web para la transcripción y análisis de audio de forma 100% local con Whisper y Gemma 4.
# Copyright (c) 2026 David Bueno Vallejo · https://github.com/davidbuenov
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

import warnings
import logging

# Suprimir advertencias inofensivas en consola (torchcodec, lightning)
warnings.filterwarnings("ignore", message=".*torchcodec.*")
logging.getLogger("lightning.pytorch.utilities.migration.utils").setLevel(logging.ERROR)
logging.getLogger("pytorch_lightning").setLevel(logging.ERROR)

import whisperx
import asyncio
import os
import gc
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar modelo de forma global para no recargarlo en cada petición
# Se usa "base" por defecto, puedes cambiar a "small" o "medium" según tus recursos y VRAM
# WhisperX usa faster-whisper por debajo, por lo que consume menos recursos.
MODEL_NAME = "base"
import torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# WhisperX requiere int8 (o float32) si se corre en CPU, float16 es para GPU.
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"

print(f"Cargando modelo WhisperX ({MODEL_NAME}) en dispositivo: {DEVICE}...")
model = whisperx.load_model(MODEL_NAME, DEVICE, compute_type=COMPUTE_TYPE)
print(f"Modelo cargado exitosamente en {DEVICE}.")

async def transcribe_audio(file_path: str, websocket=None):
    """
    Transcribe un archivo de audio usando WhisperX.
    Realiza transcripción, alineación, y si hay HF_TOKEN, diarización.
    """
    try:
        if websocket:
            await websocket.send_text("Transcribiendo audio con WhisperX (alta velocidad)...")
        
        loop = asyncio.get_event_loop()
        
        # 1. Cargar audio y transcribir
        # WhisperX prefiere que el audio se cargue con su propia función
        audio = await loop.run_in_executor(None, whisperx.load_audio, file_path)
        
        # batch_size de 8 para balancear velocidad y VRAM (por defecto es 16)
        result = await loop.run_in_executor(None, lambda: model.transcribe(audio, batch_size=8))
        
        if websocket:
            await websocket.send_text("Alineando marcas de tiempo a nivel de palabra...")
            
        # 2. Alinear (necesario para precisión y diarización posterior)
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=DEVICE)
        result = whisperx.align(result["segments"], model_a, metadata, audio, DEVICE, return_char_alignments=False)
        
        # Limpiar modelo de alineación de memoria VRAM
        del model_a
        gc.collect()
        if DEVICE == "cuda":
            torch.cuda.empty_cache()

        hf_token = os.getenv("HF_TOKEN")
        
        # 3. Diarización (sólo si el token de HuggingFace está configurado en .env)
        if hf_token and hf_token.strip() and hf_token != "tu_token_aqui":
            if websocket:
                await websocket.send_text("Identificando locutores (Speaker Diarization)...")
            
            # Importar DiarizationPipeline
            from whisperx.diarize import DiarizationPipeline
            
            # Ejecutar diarización en hilo separado
            def diarize_audio():
                diarize_model = DiarizationPipeline(token=hf_token, device=DEVICE)
                return diarize_model(audio)
                
            diarize_segments = await loop.run_in_executor(None, diarize_audio)
            result = whisperx.assign_word_speakers(diarize_segments, result)
            
            # Formatear el texto agrupando por locutores
            formatted_text = ""
            for segment in result["segments"]:
                speaker = segment.get("speaker", "Desconocido")
                text = segment.get("text", "").strip()
                formatted_text += f"[{speaker}]: {text}\n\n"
            
            final_text = formatted_text.strip()
        else:
            if websocket:
                await websocket.send_text("Generando texto final (sin separación por locutor)...")
            
            # Formatear el texto sin etiquetas de locutor
            final_text = " ".join([segment["text"].strip() for segment in result["segments"]])
            
        return final_text
    except Exception as e:
        print(f"Error en transcripción: {e}")
        if websocket:
            await websocket.send_text(f"Error: {str(e)}")
        raise e
