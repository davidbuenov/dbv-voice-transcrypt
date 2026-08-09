"""
Tests de integración y unitarios para DBV VoiceTranscrypt.

Uso (con venv activo):
    pip install httpx pytest
    pytest backend/tests/test_api.py -v

Nota: Los tests del endpoint de WebSocket y de transcripción real no se incluyen
aquí porque requieren el modelo Whisper cargado (costoso en CI). Se prueban
las validaciones HTTP y la lógica pura de construcción de prompts.
"""

import os
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


def test_upload_sanitizes_path_traversal_filename(tmp_path, monkeypatch):
    """Un filename con path traversal (o ruta absoluta) no debe escapar de UPLOAD_DIR."""
    import main

    monkeypatch.setattr(main, "UPLOAD_DIR", str(tmp_path))

    response = client.post("/upload", files={"file": ("../../evil.wav", b"contenido falso")})

    assert response.status_code == 200
    returned_name = response.json()["filename"]
    assert "/" not in returned_name and "\\" not in returned_name
    assert (tmp_path / returned_name).is_file()
    # El fichero no debe haberse escrito fuera de tmp_path (ej. en su directorio padre)
    assert not (tmp_path.parent / "evil.wav").exists()


def test_uploaded_file_path_strips_directory_traversal():
    """_uploaded_file_path debe ignorar cualquier componente de directorio del nombre."""
    from main import _uploaded_file_path, UPLOAD_DIR

    result = _uploaded_file_path("../../../etc/passwd")
    assert os.path.dirname(result) == UPLOAD_DIR
    assert os.path.basename(result) == "passwd"


def test_uploaded_file_path_strips_absolute_path():
    """Una ruta absoluta como nombre no debe poder escapar de UPLOAD_DIR."""
    from main import _uploaded_file_path, UPLOAD_DIR

    result = _uploaded_file_path("/etc/passwd")
    assert os.path.dirname(result) == UPLOAD_DIR
    assert os.path.basename(result) == "passwd"


# ---------------------------------------------------------------------------
# Tests del endpoint /api/analyze
# ---------------------------------------------------------------------------

def test_analyze_rejects_unknown_provider():
    """POST /api/analyze con un provider no soportado debe devolver 400."""
    payload = {
        "text": "texto de prueba",
        "provider": "mistral",
        "model": "mistral-large",
        "api_key": "sk-test",
        "transformation": "summary",
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 400
    assert "Proveedor no soportado" in response.json()["detail"]


@pytest.mark.parametrize("provider,model", [
    ("gemini", "gemini-3.6-flash"),
    ("openai", "gpt-5.6-sol"),
    ("claude", "claude-sonnet-5"),
])
def test_analyze_requires_api_key(provider, model):
    """POST /api/analyze con api_key vacía debe devolver 400 para cualquier proveedor cloud."""
    payload = {
        "text": "texto de prueba",
        "provider": provider,
        "model": model,
        "api_key": "",
        "transformation": "summary",
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 400
    assert "API Key" in response.json()["detail"]


@pytest.mark.parametrize("provider,patch_target", [
    ("openai", "main.analyze_with_openai"),
    ("claude", "main.analyze_with_claude"),
])
def test_analyze_dispatches_to_correct_provider(provider, patch_target, monkeypatch):
    """POST /api/analyze debe invocar la función de análisis del proveedor elegido."""
    mock_fn = MagicMock(return_value="resultado simulado")
    monkeypatch.setattr(patch_target, mock_fn)

    payload = {
        "text": "texto de prueba",
        "provider": provider,
        "model": "modelo-de-prueba",
        "api_key": "clave-de-prueba",
        "transformation": "summary",
    }
    response = client.post("/api/analyze", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "success", "result": "resultado simulado"}
    mock_fn.assert_called_once_with(
        text="texto de prueba",
        model="modelo-de-prueba",
        api_key="clave-de-prueba",
        transformation="summary",
        custom_prompt="",
    )


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


def test_resolve_system_instruction_uses_custom_prompt_verbatim():
    """En modo 'custom', la instrucción de sistema debe incluir el texto del usuario."""
    from llm_service import _resolve_system_instruction

    result = _resolve_system_instruction("custom", "Traduce al francés")
    assert "Traduce al francés" in result


def test_resolve_system_instruction_falls_back_without_custom_prompt():
    """En modo 'custom' sin texto, debe comportarse como una transformación normal."""
    from llm_service import _resolve_system_instruction, build_prompt

    result = _resolve_system_instruction("custom", "")
    assert result == build_prompt("custom")


def test_gemma_local_base_url_defaults_when_env_not_set(monkeypatch):
    """Sin LLAMA_HOST/LLAMA_PORT en el entorno, debe usar los defaults de start_gemma.py."""
    from llm_service import _gemma_local_base_url

    monkeypatch.delenv("LLAMA_HOST", raising=False)
    monkeypatch.delenv("LLAMA_PORT", raising=False)
    assert _gemma_local_base_url() == "http://127.0.0.1:8080"


def test_gemma_local_base_url_respects_gemma4_env(monkeypatch):
    """Si gemma4/.env define un host/puerto distinto, debe usarse ese en vez del hardcodeado."""
    from llm_service import _gemma_local_base_url

    monkeypatch.setenv("LLAMA_HOST", "192.168.1.50")
    monkeypatch.setenv("LLAMA_PORT", "9090")
    assert _gemma_local_base_url() == "http://192.168.1.50:9090"
