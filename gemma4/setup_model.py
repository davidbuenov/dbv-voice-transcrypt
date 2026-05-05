# =============================================================================
# DBV VoiceTranscrypt — Descarga automatizada del modelo Gemma 4 local
# Copyright (c) 2026 David Bueno Vallejo · https://github.com/davidbuenov
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================
"""
Script de descarga automática del modelo Gemma 4 E2B GGUF.
Ejecutar una vez antes de usar el modo local:
    python setup_model.py
"""
import sys
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent / "models"

# Repositorio HuggingFace del modelo GGUF
HF_REPO_ID = "unsloth/gemma-4-E2B-it-GGUF"
MODEL_FILENAME = "gemma-4-E2B-it-Q4_K_M.gguf"
MMPROJ_FILENAME = "mmproj-F16.gguf"


def download_model() -> None:
    """Descarga el modelo Gemma 4 E2B GGUF desde HuggingFace Hub."""
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("ERROR: huggingface_hub no instalado.")
        print("Ejecuta: pip install huggingface_hub>=0.24.0")
        sys.exit(1)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model_path = MODELS_DIR / MODEL_FILENAME
    mmproj_path = MODELS_DIR / MMPROJ_FILENAME

    if model_path.exists() and mmproj_path.exists():
        print(f"[OK] Modelo ya descargado en: {MODELS_DIR}")
        print(f"  - {MODEL_FILENAME} ({model_path.stat().st_size / 1e9:.1f} GB)")
        print(f"  - {MMPROJ_FILENAME} ({mmproj_path.stat().st_size / 1e6:.0f} MB)")
        return

    print("=" * 60)
    print("  DBV VoiceTranscrypt — Descarga del modelo Gemma 4 E2B")
    print("=" * 60)
    print(f"\nRepositorio: {HF_REPO_ID}")
    print(f"Destino:     {MODELS_DIR}\n")

    # Descargar modelo principal
    if not model_path.exists():
        print(f"[1/2] Descargando {MODEL_FILENAME}...")
        print("      (Esto puede tardar varios minutos según tu conexión)")
        downloaded = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=MODEL_FILENAME,
            local_dir=str(MODELS_DIR),
        )
        print(f"      Completado: {downloaded}")
    else:
        print(f"[1/2] {MODEL_FILENAME} ya existe. Omitido.")

    # Descargar projector multimodal
    if not mmproj_path.exists():
        print(f"[2/2] Descargando {MMPROJ_FILENAME}...")
        downloaded = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=MMPROJ_FILENAME,
            local_dir=str(MODELS_DIR),
        )
        print(f"      Completado: {downloaded}")
    else:
        print(f"[2/2] {MMPROJ_FILENAME} ya existe. Omitido.")

    print("\n[OK] Modelo Gemma 4 E2B listo para uso offline.")

if __name__ == "__main__":
    download_model()
