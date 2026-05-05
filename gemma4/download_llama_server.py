# =============================================================================
# DBV VoiceTranscrypt — Aplicación web para la transcripción y análisis de audio de forma 100% local con Whisper y Gemma 4.
# Copyright (c) 2026 David Bueno Vallejo · https://github.com/davidbuenov
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

"""
Script para descargar la ultima version de llama-server.exe para Windows (soporte CUDA).
"""
import os
import sys
import zipfile
import urllib.request
import json
from pathlib import Path

# Buscamos la release para windows CUDA cu12. Si no hay, fallback a CPU.
GITHUB_API_URL = "https://api.github.com/repos/ggerganov/llama.cpp/releases/latest"

def download_server():
    base_dir = Path(__file__).resolve().parent / "bin"
    base_dir.mkdir(parents=True, exist_ok=True)
    
    server_exe = base_dir / "llama-server.exe"
    if server_exe.exists():
        print(f"[INFO] llama-server.exe ya existe en {server_exe}")
        return

    print("[INFO] Consultando GitHub API para la ultima version de llama.cpp...")
    req = urllib.request.Request(GITHUB_API_URL, headers={"User-Agent": "Mozilla/5.0"})
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"[ERROR] No se pudo consultar GitHub: {e}")
        return
        
    assets = data.get("assets", [])
    target_asset = None
    
    # Priority: cudart12 -> vulkan -> cpu
    for asset in assets:
        name = asset["name"].lower()
        if "bin-win" in name and "cu12" in name:
            target_asset = asset
            break
            
    if not target_asset:
        for asset in assets:
            name = asset["name"].lower()
            if "bin-win" in name and "vulkan" in name:
                target_asset = asset
                break
                
    if not target_asset:
        print("[ERROR] No se encontro un binario apto para Windows en la ultima release.")
        return
        
    download_url = target_asset["browser_download_url"]
    zip_path = base_dir / target_asset["name"]
    
    print(f"[INFO] Descargando {target_asset['name']} (puede tardar un momento)...")
    try:
        urllib.request.urlretrieve(download_url, zip_path)
    except Exception as e:
        print(f"[ERROR] Error al descargar: {e}")
        return
        
    print(f"[INFO] Extrayendo ficheros...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Solo extraer llama-server.exe y las dlls necesarias
        for member in zip_ref.namelist():
            if member.endswith("llama-server.exe") or member.endswith(".dll"):
                # quitamos directorios intermedios
                content = zip_ref.read(member)
                filename = os.path.basename(member)
                with open(base_dir / filename, 'wb') as f:
                    f.write(content)
                    
    print("[INFO] Limpiando el archivo comprimido...")
    os.remove(zip_path)
    
    if server_exe.exists():
        print(f"[EXITO] llama-server configurado correctamente en {server_exe}")
    else:
        print("[ERROR] No se pudo encontrar llama-server.exe dentro del archivo.")

if __name__ == "__main__":
    download_server()
