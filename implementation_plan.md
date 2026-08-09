---
dependencies:
  - "backend/requirements.txt: openai (SDK oficial OpenAI)"
  - "backend/requirements.txt: anthropic (SDK oficial Claude)"
  - "backend/requirements.txt: mcp (SDK oficial Model Context Protocol, Python)"
  - "backend/.env debe tener GEMINI_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY para que el MCP server pueda analizar (no requerido para transcribir)"
risks:
  - "Namespace de API key en localStorage: cambiar de proveedor en el selector sin recargar el campo #api-key correcto envía una clave equivocada al proveedor equivocado (ver Adversarial Review)."
  - "mcp_server.py como proceso independiente: cargar .env con ruta relativa al cwd falla si el cliente MCP lo lanza desde otro directorio (ver Adversarial Review)."
  - "Los IDs de modelo (Gemini/OpenAI/Claude) quedan obsoletos con el tiempo; catálogo centralizado en un único bloque de index.html para facilitar la actualización futura."
  - "Un agente MCP podría intentar transcribir archivos fuera de backend/uploads/; se valida con os.path.realpath + comprobación de prefijo antes de procesar."
rollback_strategy: "Ambas features son aditivas: no modifican endpoints/funciones existentes, solo añaden nuevas. Revertir es eliminar los ficheros nuevos (agent-plugin/, funciones analyze_with_openai/analyze_with_claude) y las líneas añadidas en requirements.txt/index.html/app.js sin tocar el resto de la app, que sigue funcionando igual que hoy con Gemini/Gemma."
---

# Plan de Implementación: Multi-proveedor LLM + Agent Plugin (MCP Server)

## User Review Required

- Catálogo de modelos propuesto (sección "Proposed Changes" más abajo) — confirma que son los que quieres o si prefieres una selección distinta.
- Orden de ejecución propuesto: primero Multi-proveedor LLM (más simple, sin dependencias de infraestructura nueva), después el MCP Server.

## Open Questions

- Ninguna — las dos decisiones de diseño pendientes (namespace de API key, carga de .env en mcp_server.py) ya se resolvieron en el Adversarial Review de esta misma sesión.

---

## Slice 1 — Multi-proveedor LLM (OpenAI + Claude + catálogo Gemini actualizado)

### [MODIFY] `backend/requirements.txt`
Añadir `openai` y `anthropic`.

### [MODIFY] `backend/llm_service.py`
Añadir dos funciones con la misma firma que `analyze_with_gemini(text, model, api_key, transformation, custom_prompt)`:
- `analyze_with_openai`: usa `openai.OpenAI(api_key=...).chat.completions.create(...)`, mismo `build_prompt()`/`custom_prompt` que ya existe.
- `analyze_with_claude`: usa `anthropic.Anthropic(api_key=...).messages.create(...)`, system prompt vía `build_prompt()`.

### [MODIFY] `backend/main.py`
En `analyze_text`, extender la validación `if req.provider not in [...]` para incluir `"openai"` y `"claude"`, y añadir las dos ramas `if/elif` correspondientes.

### [MODIFY] `frontend/index.html`
Reemplazar el contenido de `<select id="ai-model">` con:
```html
<optgroup label="Google Gemini">
  <option value="gemini-3.6-flash" data-provider="gemini" selected>Gemini 3.6 Flash</option>
  <option value="gemini-3.5-flash" data-provider="gemini">Gemini 3.5 Flash</option>
  <option value="gemini-3.5-flash-lite" data-provider="gemini">Gemini 3.5 Flash-Lite</option>
  <option value="gemini-3.1-pro-preview" data-provider="gemini">Gemini 3.1 Pro (razonamiento)</option>
</optgroup>
<optgroup label="OpenAI">
  <option value="gpt-5.6-sol" data-provider="openai">GPT-5.6 Sol</option>
  <option value="gpt-5.6-terra" data-provider="openai">GPT-5.6 Terra</option>
  <option value="gpt-5.6-luna" data-provider="openai">GPT-5.6 Luna</option>
</optgroup>
<optgroup label="Anthropic Claude">
  <option value="claude-opus-5" data-provider="claude">Claude Opus 5</option>
  <option value="claude-sonnet-5" data-provider="claude">Claude Sonnet 5</option>
  <option value="claude-haiku-4-5-20251001" data-provider="claude">Claude Haiku 4.5</option>
</optgroup>
<optgroup label="Modelos Locales">
  <option value="gemma-4" data-provider="gemma-local">Gemma 4 (Local)</option>
</optgroup>
```
Actualizar el placeholder del input `#api-key` a un texto genérico ("API Key del proveedor seleccionado...").

### [MODIFY] `frontend/js/app.js`
En el listener `aiModel.addEventListener('change', ...)`:
- Mantener la lógica actual de ocultar la key para `gemma-local`.
- Para el resto de proveedores: guardar/leer la key con clave `${provider}_api_key` en `localStorage` (en vez del fijo `gemini_api_key`), y al cambiar de proveedor, recargar `apiKeyInput.value` desde el namespace correspondiente (o vaciar si no hay guardada).
- `saveKeyBtn` guarda en el namespace del proveedor activo en ese momento.

## Slice 2 — Agent Plugin (MCP Server)

### [NEW] `agent-plugin/plugin.json`
Manifiesto Agent Plugins 1.0.0 con nombre/versión/descripción del proyecto.

### [NEW] `agent-plugin/mcp.json`
```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "voice-transcrypt": {
      "type": "stdio",
      "command": "${PLUGIN_ROOT}/../backend/venv/Scripts/python.exe",
      "args": ["${PLUGIN_ROOT}/mcp_server.py"]
    }
  }
}
```
(Ajustar el binario de Python al venv real en Windows/Linux durante el build.)

### [NEW] `agent-plugin/mcp_server.py`
- Resuelve `BACKEND_DIR` de forma absoluta a partir de `__file__` (no del cwd) y hace `sys.path.insert(0, BACKEND_DIR)` para importar `whisper_service` y `llm_service` sin duplicar código.
- Carga `backend/.env` con `load_dotenv(BACKEND_DIR / ".env")` explícito.
- Tool `transcribe_audio(file_path: str) -> str`: resuelve `os.path.realpath(file_path)` y verifica que empiece por `os.path.realpath(BACKEND_DIR / "uploads")`; si no, error claro. Si es válida, llama a `whisper_service.transcribe_audio(path)`.
- Tool `analyze_transcription(text, transformation, custom_prompt="", provider="gemini", model="...")`: lee `GEMINI_API_KEY`/`OPENAI_API_KEY`/`ANTHROPIC_API_KEY` de entorno según `provider`; si falta, error indicando el nombre exacto de la variable a definir en `backend/.env`. Llama a la función `analyze_with_*` correspondiente de `llm_service.py`.

### [MODIFY] `backend/requirements.txt`
Añadir `mcp`.

### [NEW] `agent-plugin/skills/voice-transcrypt-analysis/SKILL.md`
Documenta el catálogo de `transformation` disponibles (mismo listado que `PROMPT_TEMPLATES`) y el flujo recomendado: transcribir una vez con `transcribe_audio`, analizar N veces con `analyze_transcription` sin repetir la transcripción.

## Verification Plan

### Manual Verification
- Slice 1: ejecutar un análisis de tipo `summary` con los 4 proveedores (Gemini, OpenAI, Claude, Gemma local) sobre la misma transcripción y confirmar que cada uno usa su propia clave guardada.
- Slice 2: registrar `agent-plugin/mcp.json` en Claude Desktop o Claude Code, listar las tools, llamar a `transcribe_audio` con un fichero real de `backend/uploads/` y luego `analyze_transcription` sobre el resultado. Confirmar que una ruta fuera de `uploads/` es rechazada.
