"""
Tests unitarios para el servidor MCP de DBV VoiceTranscrypt (agent-plugin/mcp_server.py).

Uso (con venv de backend/ activo):
    pytest agent-plugin/tests/test_mcp_server.py -v

No se prueba el protocolo MCP en sí (eso ya lo cubre el SDK oficial `mcp`),
solo la lógica propia: la restricción de rutas de transcribe_audio y el
dispatch/manejo de errores de analyze_transcription.
"""

import asyncio
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Mock de whisper_service para no cargar el modelo WhisperX real al importar.
mock_whisper_service = types.ModuleType("whisper_service")
mock_whisper_service.transcribe_audio = MagicMock()
sys.modules["whisper_service"] = mock_whisper_service

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import mcp_server  # noqa: E402


def test_transcribe_audio_rejects_path_outside_uploads():
    with pytest.raises(ValueError, match="Ruta no permitida"):
        asyncio.run(mcp_server.transcribe_audio("C:/Windows/win.ini"))


def test_transcribe_audio_rejects_missing_file_inside_uploads():
    missing_path = mcp_server.UPLOADS_DIR / "no-existe-este-fichero.wav"
    with pytest.raises(FileNotFoundError):
        asyncio.run(mcp_server.transcribe_audio(str(missing_path)))


def test_transcribe_audio_delegates_to_whisper_service(tmp_path, monkeypatch):
    monkeypatch.setattr(mcp_server, "UPLOADS_DIR", tmp_path)
    fake_audio = tmp_path / "audio.wav"
    fake_audio.write_bytes(b"fake")

    mock_transcribe = MagicMock(return_value="texto transcrito")

    async def fake_transcribe_audio(path):
        return mock_transcribe(path)

    monkeypatch.setattr(mcp_server.whisper_service, "transcribe_audio", fake_transcribe_audio)

    result = asyncio.run(mcp_server.transcribe_audio(str(fake_audio)))

    assert result == "texto transcrito"
    mock_transcribe.assert_called_once_with(str(fake_audio.resolve()))


def test_analyze_transcription_requires_env_var(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        mcp_server.analyze_transcription(text="hola", transformation="summary", provider="gemini")


def test_analyze_transcription_rejects_placeholder_env_var(monkeypatch):
    """Un .env sin rellenar (copiado de .env.example) no debe pasar como clave válida."""
    monkeypatch.setenv("GEMINI_API_KEY", "tu_api_key_de_gemini_aqui")
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        mcp_server.analyze_transcription(text="hola", transformation="summary", provider="gemini")


def test_analyze_transcription_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Proveedor no soportado"):
        mcp_server.analyze_transcription(text="hola", transformation="summary", provider="mistral")


def test_analyze_transcription_dispatches_to_claude(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "clave-de-prueba")
    mock_fn = MagicMock(return_value="resultado de claude")
    monkeypatch.setitem(mcp_server._ANALYZE_FUNCS, "claude", mock_fn)

    result = mcp_server.analyze_transcription(
        text="hola", transformation="summary", provider="claude", model="claude-sonnet-5"
    )

    assert result == "resultado de claude"
    mock_fn.assert_called_once_with(
        text="hola", model="claude-sonnet-5", api_key="clave-de-prueba",
        transformation="summary", custom_prompt="",
    )


def test_analyze_transcription_dispatches_to_gemma_local(monkeypatch):
    mock_fn = MagicMock(return_value="resultado local")
    monkeypatch.setattr(mcp_server.llm_service, "analyze_with_gemma_local", mock_fn)

    result = mcp_server.analyze_transcription(
        text="hola", transformation="summary", provider="gemma-local", model="gemma-4"
    )

    assert result == "resultado local"
    mock_fn.assert_called_once_with(
        text="hola", model="gemma-4", transformation="summary", custom_prompt=""
    )
