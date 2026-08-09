# =============================================================================
# DBV VoiceTranscrypt — Aplicación web para la transcripción y análisis de audio de forma 100% local con Whisper y Gemma 4.
# Copyright (c) 2026 David Bueno Vallejo · https://github.com/davidbuenov
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

"""
Servidor MCP (stdio) de DBV VoiceTranscrypt.

Expone dos tools para agentes de IA (Claude Code, Claude Desktop, Cursor):
  - transcribe_audio: transcripción pura con WhisperX, sin coste de LLM.
  - analyze_transcription: aplica un prompt sobre un texto ya transcrito.

Reutiliza directamente los servicios de backend/ (whisper_service.py,
llm_service.py) en vez de duplicar lógica.
"""

import contextlib
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Resolver backend/ de forma absoluta a partir de la ubicación de este fichero,
# NUNCA relativa al cwd del proceso que lo lanza: un cliente MCP puede invocar
# este servidor desde cualquier directorio vía ${PLUGIN_ROOT}.
PLUGIN_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = (PLUGIN_ROOT / ".." / "backend").resolve()
UPLOADS_DIR = BACKEND_DIR / "uploads"

sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(BACKEND_DIR / ".env")

from mcp.server.mcpserver import MCPServer  # noqa: E402

# El canal stdio de MCP debe llevar EXCLUSIVAMENTE mensajes JSON-RPC. El SDK ya
# protege stdout mientras el servidor está sirviendo (mcp.run), pero importar
# whisper_service dispara la carga del modelo WhisperX, que hace print() y
# logging a stdout ANTES de que el servidor tome el control del descriptor.
# Redirigimos esa ventana de arranque a stderr para no corromper el protocolo.
with contextlib.redirect_stdout(sys.stderr):
    import whisper_service  # noqa: E402
    import llm_service  # noqa: E402

mcp = MCPServer(
    name="voice-transcrypt",
    description="Transcripcion y analisis de audio 100% local (WhisperX + LLM multi-proveedor).",
    version="1.0.0",
)

_ANALYZE_FUNCS = {
    "gemini": llm_service.analyze_with_gemini,
    "openai": llm_service.analyze_with_openai,
    "claude": llm_service.analyze_with_claude,
}

_ENV_VAR_BY_PROVIDER = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
}


@mcp.tool()
async def transcribe_audio(file_path: str) -> str:
    """Transcribe un fichero de audio local usando WhisperX.

    No requiere ninguna API key ni LLM: es reconocimiento de voz puro
    (con diarización automática si HF_TOKEN está configurado en backend/.env).

    file_path debe apuntar a un fichero ya existente dentro de backend/uploads/.
    Cualquier ruta fuera de esa carpeta se rechaza.
    """
    resolved = Path(file_path).resolve()
    try:
        resolved.relative_to(UPLOADS_DIR.resolve())
    except ValueError:
        raise ValueError(
            f"Ruta no permitida: {file_path}. Solo se pueden transcribir ficheros "
            f"dentro de {UPLOADS_DIR}."
        )
    if not resolved.is_file():
        raise FileNotFoundError(f"No existe el fichero: {resolved}")

    return await whisper_service.transcribe_audio(str(resolved))


@mcp.tool()
def analyze_transcription(
    text: str,
    transformation: str,
    custom_prompt: str = "",
    provider: str = "gemini",
    model: str = "gemini-3.6-flash",
) -> str:
    """Aplica un prompt (predefinido o personalizado) sobre un texto ya transcrito.

    provider: "gemini" | "openai" | "claude" | "gemma-local".
    transformation: una de las claves de PROMPT_TEMPLATES en llm_service.py
    (ej. "summary", "speaker_profiling", "custom"). Ver el SKILL.md de este
    plugin para el catálogo completo.
    """
    if provider == "gemma-local":
        return llm_service.analyze_with_gemma_local(
            text=text, model=model, transformation=transformation, custom_prompt=custom_prompt
        )

    analyze_fn = _ANALYZE_FUNCS.get(provider)
    if analyze_fn is None:
        raise ValueError(f"Proveedor no soportado: {provider}. Usa gemini, openai, claude o gemma-local.")

    env_var = _ENV_VAR_BY_PROVIDER[provider]
    api_key = os.getenv(env_var)
    # backend/.env.example deja las keys con un valor placeholder ("tu_api_key_de_..._aqui");
    # tratarlo como "no configurado" evita un error de autenticación confuso del proveedor.
    if not api_key or api_key.strip() == "" or api_key.startswith("tu_api_key_de"):
        raise RuntimeError(f"Falta la variable de entorno {env_var}. Definela en {BACKEND_DIR / '.env'}.")

    return analyze_fn(text=text, model=model, api_key=api_key, transformation=transformation, custom_prompt=custom_prompt)


if __name__ == "__main__":
    mcp.run(transport="stdio")
