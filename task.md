## Backlog

_Ninguna tarea pendiente en el backlog — ambas features del último ciclo se completaron. Ver "Hecho"._

## En Curso

_Ninguna tarea en curso — ver Snapshot de Contexto para retomar._

## Hecho

- `[x]` Migración del framework dbv-specs-ops v1.3.0 → v2.4.0 (estructura plana mantenida).
- `[x]` Rediseño de interfaz "Estudio Técnico" (sin gradientes/glassmorphism/emojis/CDNs externas).
- `[x]` Prompts y UI de análisis por locutores (Diarización).

### Feature: Soporte Multi-proveedor LLM (OpenAI, Claude, catálogo Gemini actualizado)
- `[x]` Backend — `llm_service.py`: añadidas `analyze_with_openai` y `analyze_with_claude` (misma firma que `analyze_with_gemini`), con `_resolve_system_instruction` compartida.
- `[x]` Backend — `requirements.txt`: añadidos `openai==2.53.0`, `anthropic==0.121.0`, `mcp==2.0.0`.
- `[x]` Backend — `main.py`: `analyze_text` acepta `provider in ["gemini","openai","claude","gemma-local"]` vía dict de dispatch.
- `[x]` Frontend — `index.html`: `<select id="ai-model">` actualizado con el catálogo verificado y placeholder de API Key genérico.
- `[x]` Frontend — `app.js`: clave en `localStorage` por proveedor (`{provider}_api_key`), recargada al cambiar de proveedor; validación de key generalizada a los 3 proveedores cloud.
- `[x]` Tests — `backend/tests/test_api.py`: dispatch a openai/claude mockeado, validación de API key para los 3 proveedores cloud, `test_analyze_rejects_unknown_provider` corregido. **12/12 tests pasan.**
- `[ ]` Test manual end-to-end con claves reales (pendiente para el usuario, no se puede probar sin credenciales).

### Feature: Agent Plugin (MCP Server)
- `[x]` `agent-plugin/plugin.json` (manifiesto Agent Plugins 1.0.0).
- `[x]` `agent-plugin/mcp.json` (servidor `stdio`, con `${PLUGIN_ROOT}`).
- `[x]` `agent-plugin/mcp_server.py`:
  - Tool `transcribe_audio(file_path)` — valida que la ruta esté dentro de `backend/uploads/`, reutiliza `whisper_service.transcribe_audio`.
  - Tool `analyze_transcription(...)` — reutiliza `llm_service.py`, lee API keys de `backend/.env`.
  - **Bug encontrado y corregido en /test:** los `print()`/logging que dispara la carga del modelo WhisperX al importar `whisper_service` ocurrían antes de que el SDK de MCP tomara el control del descriptor stdout, corrompiendo el canal JSON-RPC. Se envuelve el import en `contextlib.redirect_stdout(sys.stderr)`.
- `[x]` `mcp` añadido a `backend/requirements.txt`.
- `[x]` `agent-plugin/skills/voice-transcrypt-analysis/SKILL.md` (catálogo de transformaciones + flujo recomendado).
- `[x]` Tests — `agent-plugin/tests/test_mcp_server.py` (7 tests: restricción de rutas, dispatch por proveedor, variable de entorno faltante). **7/7 pasan.**
- `[x]` Verificación end-to-end real: servidor lanzado como subproceso vía el SDK cliente de `mcp`, `list_tools()` y `call_tool()` contra las dos tools, confirmando que el protocolo ya no se corrompe y los errores llegan estructurados (`is_error=True` con mensaje claro).
- `[x]` `backend/.env.example` documentado con `GEMINI_API_KEY`/`OPENAI_API_KEY`/`ANTHROPIC_API_KEY` para el MCP server, y checks de "valor placeholder sin rellenar" añadidos (con test).
- `[x]` `README.md`: sección "Agent Plugin (Servidor MCP)" con instrucciones para registrar el servidor en Claude Desktop (Windows) y probarlo.

### Fix (fuera de spec original, pedido explícitamente): Configuración real de Gemma 4 Local
- `[x]` `gemma4/.env` no lo leía nadie (`start_gemma.py` y `llm_service.py` tenían host/puerto hardcodeados). Ahora ambos leen el mismo `.env` vía `python-dotenv`.
- `[x]` `gemma4/.env.example` creado documentando las 5 variables; `gemma4/README.md` actualizado.
- `[x]` Tests para `_gemma_local_base_url()` (defaults y override). **14/14 tests pasan en backend** (12 → 14).

### /code-simplify: Limpieza y Auditoría de Seguridad
- `[x]` **Security fix:** `/upload` y `/ws/transcribe` saneaban el filename del cliente contra path traversal/rutas absolutas (`_uploaded_file_path()` con `os.path.basename()`).
- `[x]` `analyze_with_claude`: `max_tokens` subido de 4096 a 8192 (truncaba transformaciones largas).
- `[x]` `analyze_with_gemma_local` unificado para usar `_resolve_system_instruction` (antes tenía su propio texto de "custom" divergente).
- `[x]` `/api/analyze`: las llamadas a los 4 proveedores (síncronas/bloqueantes) se ejecutan ahora en threadpool (`run_in_threadpool`) para no congelar el event loop / el WebSocket de transcripción.
- `[x]` `app.js`: `handleAiAnalysis` reutiliza `currentProvider()` en vez de duplicar la lógica.
- `[x]` Checklist de seguridad obligatorio verificado: sin credenciales hardcodeadas, `openai`/`anthropic`/`mcp` confirmados como paquetes oficiales reales, `.env` reales fuera de git.
- `[x]` 6 tests nuevos. **25/25 tests pasan** (17 backend + 8 agent-plugin).

### /ship: v2.1.0
- `[x]` MCP server registrado y verificado funcionando en Claude Desktop real por el usuario (tras resolver el problema de la ruta de configuración virtualizada por MSIX/Microsoft Store).
- `[x]` `README.md` actualizado: badges de versión, características, tecnologías, estructura del proyecto, créditos (Claude Code añadido).
- `[x]` `walkthrough.md` reescrito con el resumen completo de la entrega v2.1.0.
- `[x]` `CHANGELOG.md`: `[Sin publicar]` publicado como `[2.1.0] - 2026-08-09`.
- `[x]` Versión bump en `backend/main.py` (`FastAPI(version=...)`) de 2.0.0 → 2.1.0.
- `[x]` Memory Gate ejecutado: `memory.md` actualizado con 3 decisiones técnicas y 3 lecciones nuevas.

---

## 📸 Snapshot de Contexto (última sesión: 2026-08-09)

**Dónde estamos:** Ciclo completo cerrado — `/spec`, `/plan`, `/build`, `/test`, `/code-simplify` y `/ship` para v2.1.0 (multi-proveedor LLM + Agent Plugin/MCP + rediseño + fix de Gemma). 25/25 tests automatizados pasan. Falta solo el commit + tag + push (en curso).

**Próximo paso exacto:** si se retoma en otra sesión y el commit/tag/push no se completó, revisar `git log -1` y `git tag` para ver hasta dónde llegó, y completar `git push origin main --tags`.

**Decisiones ya tomadas (no volver a preguntar):**
- El MCP server reutiliza `backend/.env` para las API keys (no un `.env` propio en `agent-plugin/`), decisión explícita del usuario.
- El Agent Plugin vive en `agent-plugin/` en la raíz (no `.well-known/`), porque `Agent Readiness (Web) = No`.
- `transcribe_audio` solo acepta rutas dentro de `backend/uploads/`.
- Catálogo de modelos verificado por búsqueda web el 2026-08-09 (ver `docs/SPECIFICATIONS.md` sección 4) — antes de dar por bueno un modelo en el futuro, reverificar en vez de asumir que sigue vigente.
- El `mcp.json` asume Windows (`venv/Scripts/python.exe`); si el proyecto se usa alguna vez en Linux/Mac habría que cambiar a `venv/bin/python`.
- Si Claude Desktop no detecta el MCP server, comprobar primero si está instalado desde Microsoft Store (MSIX) — en ese caso la config real está en `%LOCALAPPDATA%\Packages\Claude_<id>\LocalCache\Roaming\Claude\`, no en `%APPDATA%\Claude\`. Ver `README.md`.
