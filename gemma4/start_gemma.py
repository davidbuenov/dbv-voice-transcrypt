# =============================================================================
# DBV VoiceTranscrypt — Aplicación web para la transcripción y análisis de audio de forma 100% local con Whisper y Gemma 4.
# Copyright (c) 2026 David Bueno Vallejo · https://github.com/davidbuenov
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

import os
import subprocess
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

# Configuración básica (podría extenderse con python-dotenv)
GEMMA4_DIR = Path(__file__).resolve().parent
BIN_DIR = GEMMA4_DIR / "bin"
MODELS_DIR = GEMMA4_DIR / "models"

LLAMA_EXE = BIN_DIR / "llama-server.exe"
MODEL_GGUF = MODELS_DIR / "gemma-4-E2B-it-Q4_K_M.gguf"
MMPROJ_GGUF = MODELS_DIR / "mmproj-F16.gguf"

HOST = "127.0.0.1"
PORT = 8080
CTX_SIZE = 32768
GPU_LAYERS = 99

def _llama_alive() -> bool:
    try:
        with urllib.request.urlopen(f"http://{HOST}:{PORT}/health", timeout=1):
            return True
    except urllib.error.HTTPError:
        return True
    except Exception:
        return False

def _drain_pipe(proc: subprocess.Popen) -> None:
    if proc.stdout:
        for _ in proc.stdout:
            pass

def main():
    print("-" * 56)
    print("  Gemma 4 Local Launcher (llama-server)")
    print("-" * 56)

    if _llama_alive():
        print(f"[INFO] El servidor ya está corriendo en el puerto {PORT}.")
        print("Puedes cerrarlo y volverlo a abrir, o simplemente usarlo.")
        input("Presiona ENTER para salir...")
        return

    # Validaciones
    if not LLAMA_EXE.exists():
        print(f"[ERROR] No se encontró el ejecutable en {LLAMA_EXE}")
        print("  -> Ejecuta: python download_llama_server.py")
        input("Presiona ENTER para salir...")
        return

    if not MODEL_GGUF.exists() or not MMPROJ_GGUF.exists():
        print("[ERROR] No se encontraron los modelos GGUF en la carpeta models/.")
        print("  Faltan:")
        print(f"    - {MODEL_GGUF.name}")
        print(f"    - {MMPROJ_GGUF.name}")
        print("\n  -> Revisa el README.md para las instrucciones de descarga.")
        input("Presiona ENTER para salir...")
        return

    cmd = [
        str(LLAMA_EXE),
        "-m", str(MODEL_GGUF),
        "--mmproj", str(MMPROJ_GGUF),
        "--port", str(PORT),
        "-c", str(CTX_SIZE),
        "--n-gpu-layers", str(GPU_LAYERS),
        "-fa", "on"
    ]

    print("[INFO] Iniciando llama-server...")
    print(f"[INFO] Comando: {' '.join(cmd)}")
    
    server_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    threading.Thread(target=_drain_pipe, args=(server_process,), daemon=True).start()

    print("\n[INFO] Esperando a que el servidor esté listo...")
    timeout = 30
    for i in range(timeout):
        if server_process.poll() is not None:
            print(f"\n[ERROR] llama-server falló inesperadamente (código {server_process.returncode}).")
            input("Presiona ENTER para salir...")
            return
        if _llama_alive():
            print(f"\n[EXITO] llama-server está listo en http://{HOST}:{PORT}/")
            print("        (Mantén esta ventana abierta para seguir procesando peticiones)")
            break
        time.sleep(1)
    else:
        print(f"\n[AVISO] El servidor tardó más de {timeout}s en responder. Podría seguir cargando.")

    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Deteniendo llama-server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main()
