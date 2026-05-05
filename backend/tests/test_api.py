"""
Tests de integración y unitarios para DBV VoiceTranscrypt.

Uso (con venv activo):
    pip install httpx pytest
    pytest backend/tests/test_api.py -v

Nota: Los tests del endpoint de WebSocket y de transcripción real no se incluyen
aquí porque requieren el modelo Whisper cargado (costoso en CI). Se prueban
las validaciones HTTP y la lógica pura de construcción de prompts.
"""

import pytest
from fastapi.testclient import TestClient

# Importamos la app sin arrancar Whisper — el modelo se carga al importar
# whisper_service. Para los tests de la API HTTP no necesitamos Whisper,
# por lo que mockeamos el import antes de importar main.
import sys
import types
from unittest.mock import MagicMock

# Mock de whisper_service para no cargar el modelo al importar
mock_whisper_service = types.ModuleType("whisper_service")
mock_whisper_service.transcribe_audio = MagicMock()
sys.modules["whisper_service"] = mock_whisper_service

from main import app  # noqa: E402 — el mock debe estar antes del import

client = TestClient(app)


# ---------------------------------------------------------------------------
# Tests del endpoint raíz
# ---------------------------------------------------------------------------

def test_root_returns_html():
    """GET / debe devolver 200 con content-type HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


# ---------------------------------------------------------------------------
# Tests del endpoint /upload
# ---------------------------------------------------------------------------

def test_upload_requires_file():
    """POST /upload sin fichero adjunto debe devolver 422 (Unprocessable Entity)."""
    response = client.post("/upload")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests del endpoint /api/analyze
# ---------------------------------------------------------------------------

def test_analyze_rejects_unknown_provider():
    """POST /api/analyze con un provider no soportado debe devolver 400."""
    payload = {
        "text": "texto de prueba",
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "sk-test",
        "transformation": "summary",
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 400
    assert "Proveedor no soportado" in response.json()["detail"]


def test_analyze_requires_api_key():
    """POST /api/analyze con api_key vacía debe devolver 400."""
    payload = {
        "text": "texto de prueba",
        "provider": "gemini",
        "model": "gemini-2.0-flash",
        "api_key": "",
        "transformation": "summary",
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 400
    assert "API Key" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Tests unitarios de llm_service (lógica pura, sin llamadas de red)
# ---------------------------------------------------------------------------

def test_build_prompt_all_transformations():
    """build_prompt debe devolver un string no vacío para cada tipo registrado."""
    from llm_service import build_prompt, PROMPT_TEMPLATES, FALLBACK_PROMPT

    known_types = list(PROMPT_TEMPLATES.keys())
    for t in known_types:
        prompt = build_prompt(t)
        assert isinstance(prompt, str) and len(prompt) > 0, f"Prompt vacío para: {t}"


def test_build_prompt_fallback_for_unknown():
    """build_prompt con un tipo desconocido debe devolver el prompt de fallback."""
    from llm_service import build_prompt, FALLBACK_PROMPT

    result = build_prompt("tipo_inexistente_xyz")
    assert result == FALLBACK_PROMPT
