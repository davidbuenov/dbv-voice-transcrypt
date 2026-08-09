# Resumen de Entrega: v2.1.0 — Multi-proveedor LLM, Agent Plugin (MCP) y Rediseño

Ciclo completo `/spec → /plan → /build → /test → /code-simplify → /ship` sobre tres frentes: actualización del framework, rediseño visual y dos funcionalidades nuevas.

## Cambios Realizados

### 1. Framework `dbv-specs-ops` v1.3.0 → v2.4.0
Actualización in-place (estructura plana mantenida, sin migrar a subcarpeta `dbv-specs-ops/`). Ficheros de framework actualizados; `docs/SPECIFICATIONS.md`, `docs/ARCHITECTURE.md`, `task.md` y `CHANGELOG.md` del proyecto quedaron intactos como exige el propio `UPGRADE_PROMPT.md`.

### 2. Rediseño de Interfaz: "Estudio Técnico"
Sustituida la estética anterior (glassmorphism, degradado índigo/violeta, Inter vía Google Fonts, iconos emoji + Font Awesome) — un patrón visual fácilmente reconocible como "genérico de IA" — por un sistema plano sin dependencias de red: fondo carbón/gris neutro, acento ámbar único, tipografía de sistema y un set propio de iconos SVG lineales (`frontend/js/icons.js`). `docs/DESIGN.md` documenta los tokens como fuente de verdad.

### 3. Soporte Multi-proveedor LLM
Añadidos **OpenAI (GPT-5.6 Sol/Terra/Luna)** y **Anthropic Claude (Opus 5/Sonnet 5/Haiku 4.5)** junto a Gemini (catálogo actualizado a la generación 3.x) y Gemma 4 local. Cada proveedor gestiona su propia API Key en `localStorage` del navegador, sin persistencia en servidor.

### 4. Agent Plugin (Servidor MCP)
Nuevo `agent-plugin/` (estándar Agent Plugins 1.0.0) con dos herramientas: `transcribe_audio` (WhisperX puro) y `analyze_transcription` (cualquier prompt del catálogo, en los 4 proveedores). Incluye `SKILL.md` documentando el flujo recomendado para agentes.

### 5. Code Simplify + Auditoría de Seguridad
- **Fix de seguridad:** `/upload` y `/ws/transcribe` saneaban insuficientemente el nombre de fichero del cliente (path traversal). Corregido con `_uploaded_file_path()`.
- `/api/analyze` bloqueaba el event loop de FastAPI con llamadas síncronas a los 4 SDKs — movido a threadpool.
- `analyze_with_claude`: `max_tokens` insuficiente (4096 → 8192) para transformaciones largas.
- `analyze_with_gemma_local` unificado con el resto de proveedores (`_resolve_system_instruction`).
- Verificado: sin credenciales hardcodeadas, dependencias (`openai`, `anthropic`, `mcp`) confirmadas como paquetes oficiales reales.

### 6. Fix de Configuración: Gemma 4 Local
`gemma4/.env` existía pero no lo leía nadie (host/puerto hardcodeados en `start_gemma.py` y en `llm_service.py`). Ahora ambos leen el mismo fichero; añadido `gemma4/.env.example`.

### 7. Verificación end-to-end del MCP en Claude Desktop
Al probarlo en real se descubrió que la instalación de Claude Desktop desde Microsoft Store virtualiza `%APPDATA%` (contenedor MSIX) — el `claude_desktop_config.json` de la ruta "estándar" no lo lee la app. Documentado en `README.md` cómo localizar la ruta real (`%LOCALAPPDATA%\Packages\Claude_<id>\LocalCache\Roaming\Claude\`).

## Verificación

- **25 tests automatizados** pasan (17 `backend/tests/test_api.py` + 8 `agent-plugin/tests/test_mcp_server.py`).
- Verificación end-to-end real del protocolo MCP: servidor lanzado como subproceso vía el SDK cliente oficial, `list_tools()` y `call_tool()` contra las dos tools.
- Rediseño verificado visualmente en navegador (modo oscuro y claro) con capturas de pantalla.
- MCP server registrado y verificado funcionando en Claude Desktop real por el usuario.

> [!TIP]
> Para usar los nuevos proveedores necesitas tu propia API Key de OpenAI/Claude (Gemini ya se pedía antes). Para el Agent Plugin, sigue la sección "🤖 Agent Plugin (Servidor MCP)" del `README.md` — presta atención al aviso sobre Claude Desktop instalado desde la Microsoft Store si no ves el servidor conectado.
