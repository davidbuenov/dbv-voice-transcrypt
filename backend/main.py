# =============================================================================
# DBV VoiceTranscrypt — Aplicación web para la transcripción y análisis de audio de forma 100% local con Whisper y Gemma 4.
# Copyright (c) 2026 David Bueno Vallejo · https://github.com/davidbuenov
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

"""
Punto de entrada de la API FastAPI para DBV VoiceTranscrypt.

Responsabilidades de este módulo:
  - Configurar la aplicación y los middlewares.
  - Servir el frontend estático.
  - Definir los endpoints HTTP y WebSocket como orquestadores:
    reciben la petición, validan, delegan a los servicios y devuelven la respuesta.

La lógica de negocio vive en los servicios correspondientes:
  - whisper_service.py → transcripción local con Whisper
  - llm_service.py     → análisis de texto con Gemini (y futuros proveedores)
"""

from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import shutil
import os

from whisper_service import transcribe_audio
from llm_service import analyze_with_gemini, analyze_with_gemma_local, analyze_with_openai, analyze_with_claude

app = FastAPI(title="DBV VoiceTranscrypt", version="2.1.0")

# CORS abierto a todos los orígenes porque esta aplicación está diseñada
# para ejecutarse exclusivamente en localhost (uso personal/local).
# NO desplegar en un servidor público con esta configuración.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _uploaded_file_path(filename: str) -> str:
    """Resuelve la ruta de un fichero dentro de UPLOAD_DIR a partir de un nombre
    controlado por el cliente (subida HTTP o mensaje de WebSocket).

    Se descarta cualquier componente de directorio del nombre (os.path.basename)
    para que un nombre como "../../etc/passwd" o una ruta absoluta no permita
    escribir ni leer fuera de UPLOAD_DIR.
    """
    safe_filename = os.path.basename(filename)
    return os.path.join(UPLOAD_DIR, safe_filename)

# Monta los archivos estáticos para servir el frontend vanilla
app.mount("/static", StaticFiles(directory="../frontend"), name="static")


@app.get("/")
async def root():
    """Sirve la SPA del frontend."""
    with open("../frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    """Gestiona la sesión WebSocket de transcripción en tiempo real.

    Flujo:
      1. Acepta la conexión.
      2. Recibe el nombre de archivo (previamente subido vía /upload).
      3. Delega la transcripción a whisper_service (corre en hilo separado).
      4. Envía el resultado como JSON o propaga errores.
    """
    await websocket.accept()
    try:
        filename = await websocket.receive_text()
        file_path = _uploaded_file_path(filename)

        if not os.path.exists(file_path):
            await websocket.send_text(f"Error: Archivo {filename} no encontrado en el servidor.")
            return

        text = await transcribe_audio(file_path, websocket)
        await websocket.send_json({"status": "success", "text": text})

    except WebSocketDisconnect:
        print("Cliente desconectado del websocket")
    except Exception as e:
        await websocket.send_json({"status": "error", "message": str(e)})


@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    """Recibe el archivo de audio y lo almacena en disco.

    Soporta archivos grandes (~256 MB) copiando por chunks con shutil.
    El nombre resultante se usa como referencia en el WebSocket.
    """
    file_location = _uploaded_file_path(file.filename)
    safe_filename = os.path.basename(file_location)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    return {"info": f"Archivo '{safe_filename}' subido exitosamente.", "filename": safe_filename}


class AnalyzeRequest(BaseModel):
    text: str
    provider: str
    model: str
    api_key: str
    transformation: str
    custom_prompt: str = ""


@app.post("/api/analyze")
async def analyze_text(req: AnalyzeRequest):
    """Analiza la transcripción con el proveedor LLM seleccionado.

    La construcción de prompts y la llamada al SDK están encapsuladas
    en llm_service.py para mantener este endpoint como orquestador puro.
    """
    cloud_providers = {
        "gemini": analyze_with_gemini,
        "openai": analyze_with_openai,
        "claude": analyze_with_claude,
    }

    if req.provider not in cloud_providers and req.provider != "gemma-local":
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "Proveedor no soportado aún. Use 'gemini', 'openai', 'claude' o 'gemma-local'."},
        )

    if req.provider in cloud_providers and (not req.api_key or req.api_key == "local"):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": f"La API Key es obligatoria para {req.provider}."},
        )

    try:
        # Los SDKs de Gemini/OpenAI/Claude/llama-server son síncronos (I/O de red
        # bloqueante). Se ejecutan en el threadpool de FastAPI para no congelar
        # el event loop mientras esperan respuesta (lo que bloquearía, por
        # ejemplo, los mensajes de progreso del WebSocket de transcripción).
        if req.provider in cloud_providers:
            result = await run_in_threadpool(
                cloud_providers[req.provider],
                text=req.text,
                model=req.model,
                api_key=req.api_key,
                transformation=req.transformation,
                custom_prompt=req.custom_prompt,
            )
        else:
            result = await run_in_threadpool(
                analyze_with_gemma_local,
                text=req.text,
                model=req.model,
                transformation=req.transformation,
                custom_prompt=req.custom_prompt,
            )
        return {"status": "success", "result": result}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)},
        )
