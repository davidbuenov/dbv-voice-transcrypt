# 🎙️ DBV VoiceTranscrypt

[![Release](https://img.shields.io/github/v/release/davidbuenov/dbv-voice-transcrypt?display_name=tag&sort=semver)](https://github.com/davidbuenov/dbv-voice-transcrypt/releases)
![Version](https://img.shields.io/badge/version-2.1.0-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Status](https://img.shields.io/badge/status-active-success)
[![Last Update](https://img.shields.io/github/last-commit/davidbuenov/dbv-voice-transcrypt?label=last%20update)](https://github.com/davidbuenov/dbv-voice-transcrypt/commits/main)
[![Framework](https://img.shields.io/badge/framework-dbv--specs--ops-111827?logo=github&logoColor=white)](https://github.com/davidbuenov/dbv-specs-ops)

Una aplicación web moderna y segura diseñada para la transcripción y el análisis de audio de forma **100% local**. Ideal para reuniones corporativas, entrevistas, clases universitarias y notas de voz personales, donde la privacidad de la información es la máxima prioridad.

## 🌟 Características Principales

- **Privacidad Blindada**: Procesamiento de audio completamente local utilizando **WhisperX** (basado en OpenAI Whisper y faster-whisper). Tus grabaciones nunca salen de tu máquina.
- **Transcripción Segura**: Diseñado para manejar información sensible sin dependencias de la nube.
- **Multiproposito**: Optimizado para grabaciones largas (clases, juntas de trabajo, entrevistas) en formatos como `.wav` de 256MB+.
- **Reconocimiento de Locutores (Speaker Diarization)**: Identifica quién habla en cada momento mediante la integración opcional con Pyannote.
- **Interfaz "Estudio Técnico"**: Frontend plano y sin ruido visual (sin degradados, sin glassmorphism, sin dependencias de CDNs externas), con zona de arrastrar y soltar (Drag & Drop) y una experiencia de usuario fluida.
- **Operación Asíncrona**: Transcripción en segundo plano para mantener la productividad.
- **Agent Plugin (MCP)**: Servidor MCP propio (`agent-plugin/`) que expone la transcripción y el análisis como herramientas para agentes de IA (Claude Code, Claude Desktop, Cursor).

### 🧠 Análisis de Texto Multi-proveedor
- **Generación de Contenido**: Resúmenes ejecutivos, mapas mentales, extracción de acciones clave (TODOs) y formato inteligente — incluyendo plantillas específicas para transcripciones con diarización (perfilado de locutores, aportaciones por persona, asignación de tareas).
- **Modelos Locales Soportados**: Integración directa con **Gemma 4** (`llama-server`) para un procesamiento de texto completamente privado e independiente.
- **Modelos de Nube Soportados**: **Google Gemini** (3.6/3.5/3.1 Pro), **OpenAI** (GPT-5.6 Sol/Terra/Luna) y **Anthropic Claude** (Opus 5/Sonnet 5/Haiku 4.5) — cada uno con su propia API Key gestionada en el navegador.

## 🛠️ Tecnologías

- **Backend**: Python 3.x, FastAPI.
- **Frontend**: Vanilla JS, CSS puro, HTML5.
- **IA (Transcripción)**: WhisperX (Local, aceleración por GPU y CPU).
- **IA (Análisis)**: Gemma 4 Local / Google Gemini / OpenAI / Anthropic Claude.
- **Agent Plugin**: Servidor MCP (SDK oficial `mcp`) bajo el estándar Agent Plugins 1.0.0.

## 📂 Estructura del Proyecto

```text
/
├── backend/                # Servidor FastAPI y lógica de IA
│   ├── main.py             # Endpoints HTTP/WebSocket (orquestación)
│   ├── whisper_service.py  # Transcripción local con WhisperX
│   ├── llm_service.py      # Análisis de texto (Gemini / OpenAI / Claude / Gemma 4)
│   └── uploads/            # Audios subidos por la web (temporal, no versionado)
├── frontend/               # Interfaz de usuario (HTML, CSS, JS vanilla)
├── agent-plugin/           # Agent Plugin: servidor MCP para agentes de IA (Claude Code, Claude Desktop, Cursor)
│   ├── mcp_server.py       # Tools: transcribe_audio, analyze_transcription
│   └── skills/             # Guía de uso para agentes (SKILL.md)
├── gemma4/                 # Módulo independiente para lanzar Gemma 4 (Llama.cpp)
├── docs/                   # Documentación, especificaciones y arquitectura (SDD)
├── install.cmd             # Instalador (entorno virtual, dependencias, CUDA)
├── start.cmd               # Utilidad para arrancar backend y frontend
├── start_gemma.cmd         # Utilidad para arrancar el servidor local de Gemma 4
└── stop.cmd                # Utilidad para cerrar procesos de forma limpia
```

## 🧠 Metodología: Spec-Driven Development (SDD)

Este proyecto sigue la metodología **Spec-Driven Development (SDD)** utilizando el framework **dbv-specs-ops**: [https://github.com/davidbuenov/dbv-specs-ops](https://github.com/davidbuenov/dbv-specs-ops).

La documentación en `docs/` es la fuente única de verdad:

- `docs/SPECIFICATIONS.md`: Requisitos detallados y casos de uso.
- `docs/ARCHITECTURE.md`: Decisiones técnicas y stack tecnológico.
- `task.md`: Seguimiento del progreso y captura de contexto.

## 🚀 Inicio Rápido

1. Clona el repositorio.
2. Ejecuta el archivo **`install.cmd`** (haz doble clic). Esto preparará tu entorno, instalará las dependencias y asegurará que la tarjeta gráfica (NVIDIA CUDA) se configure correctamente.
3. **(Opcional) Reconocimiento de Locutores**: Si quieres que la aplicación distinga las diferentes voces (Speaker Diarization), necesitas un token gratuito de Hugging Face.
   - Renombra `backend/.env.example` a `backend/.env`.
   - Entra en [Hugging Face](https://huggingface.co/) y acepta los términos del modelo [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1).
   - Crea un token de acceso y pégalo en tu archivo `.env`.
   - *Nota: Si no haces este paso, la aplicación transcribirá el audio perfectamente, pero no separará el texto por locutores.*
4. Inicia la aplicación (servidor y frontend): Haz doble clic en **`start.cmd`**
5. Sirve el frontend y empieza a transcribir de forma segura.
6. *(Opcional)* Si quieres utilizar el LLM en local sin conexión a internet, arranca **`start_gemma.cmd`**. Para configurar esto por primera vez, **sigue las instrucciones en [gemma4/README.md](gemma4/README.md)**.
7. Usa `stop.cmd` al finalizar para liberar los recursos del sistema de Windows.

## 🤖 Agent Plugin (Servidor MCP)

Además de la interfaz web, la app expone la transcripción y el análisis como dos herramientas **MCP** (`transcribe_audio` y `analyze_transcription`) para que un agente de IA pueda usarlas directamente. Están definidas en `agent-plugin/mcp_server.py` — más detalle del catálogo de transformaciones en [`agent-plugin/skills/voice-transcrypt-analysis/SKILL.md`](agent-plugin/skills/voice-transcrypt-analysis/SKILL.md).

### Requisitos previos

- Haber ejecutado `install.cmd` al menos una vez (el MCP server reutiliza el mismo `venv` de `backend/`).
- Si quieres usar `analyze_transcription` con Gemini/OpenAI/Claude, copia `backend/.env.example` a `backend/.env` y rellena la(s) API key(s) que vayas a usar (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`). No hace falta ninguna key para `transcribe_audio` ni para analizar con `gemma-local`.

### Configurar Claude Desktop (Windows)

1. Cierra Claude Desktop si lo tienes abierto.
2. Abre (o crea si no existe) el archivo de configuración:
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```
3. Añade una entrada `voice-transcrypt` dentro de `"mcpServers"`, apuntando con **ruta absoluta** al Python del `venv` y a `mcp_server.py` (Claude Desktop no resuelve los placeholders `${PLUGIN_ROOT}` del estándar Agent Plugins, así que hay que escribir la ruta real de tu copia del proyecto):
   ```json
   {
     "mcpServers": {
       "voice-transcrypt": {
         "command": "D:\\Programacion\\github-davidbuenov\\dbv-voice-transcrypt\\backend\\venv\\Scripts\\python.exe",
         "args": ["D:\\Programacion\\github-davidbuenov\\dbv-voice-transcrypt\\agent-plugin\\mcp_server.py"]
       }
     }
   }
   ```
   Si el archivo ya tiene otras entradas en `"mcpServers"`, añade `"voice-transcrypt"` junto a ellas en vez de sobrescribir el archivo entero.
4. Guarda el archivo y vuelve a abrir Claude Desktop por completo (no basta con cerrar la ventana: si queda en la bandeja del sistema, ciérralo desde ahí antes de reabrirlo).
5. Verifica que se ha conectado: en una conversación nueva, el icono de herramientas (🔨) de la esquina inferior debe listar `voice-transcrypt` con sus dos tools. También puedes simplemente preguntarle a Claude: *"¿qué herramientas MCP tienes disponibles?"*

> ⚠️ **Si instalaste Claude Desktop desde la Microsoft Store**, la app corre en un contenedor (MSIX) que **virtualiza** `%APPDATA%`. Editar `%APPDATA%\Claude\claude_desktop_config.json` no tiene ningún efecto — ese fichero no lo lee nadie. La ruta real es:
> ```
> %LOCALAPPDATA%\Packages\Claude_<id-del-paquete>\LocalCache\Roaming\Claude\claude_desktop_config.json
> ```
> Para encontrar `<id-del-paquete>` en tu máquina:
> ```powershell
> Get-ChildItem "$env:LOCALAPPDATA\Packages" -Directory | Where-Object Name -like "Claude_*"
> ```
> Cómo saber si tienes la versión de Store: si `Get-Process Claude | Select Path` apunta a `C:\Program Files\WindowsApps\...`, es la de Store y aplica esta nota. Si apunta a algo bajo `AppData\Local\AnthropicClaude\` (instalador normal), usa la ruta estándar del paso 2 sin problema.

### Probarlo

1. Sube un audio desde la interfaz web normal (`start.cmd`) para que quede guardado en `backend/uploads/`.
2. En Claude Desktop, pide algo como: *"Transcribe el archivo backend/uploads/mi_audio.wav y luego hazme un resumen ejecutivo con Claude Sonnet 5"*. Claude debería encadenar `transcribe_audio` y después `analyze_transcription` (`provider="claude"`, `model="claude-sonnet-5"`) automáticamente.
3. Si algo falla, el mensaje de error de la tool es explícito (ej. variable de entorno que falta, o ruta fuera de `backend/uploads/`) — revísalo antes de reportar un bug.

---

## ✍️ Autores y Créditos / Authors & Credits

### 👤 Concebido y dirigido por / Conceived and directed by

#### David Bueno Vallejo

> "Idea original, visión de la metodología, diseño del sistema de documentos, pruebas y refinamiento."
> "Original idea, methodology vision, document system design, testing and refinement."

[![LinkedIn](https://img.shields.io/badge/LinkedIn-davidbueno-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/davidbueno/)
[![Website](https://img.shields.io/badge/Web-davidbuenov.com-6366f1?logo=google-chrome&logoColor=white)](https://davidbuenov.com)

### 🤖 Construido con / Built with AI Pair Programming

| Tool | Role |
|---|---|
| **[Antigravity](https://antigravity.google)** · *Google DeepMind* | Pair programming principal para arquitectura de prompts, documentación, refinamiento y validación del flujo del proyecto. |
| **[Claude Code](https://claude.com/claude-code)** · *Anthropic* | Migración del framework SDD, rediseño de interfaz, soporte multi-proveedor LLM, Agent Plugin (servidor MCP), auditoría de seguridad y ciclo `/ship`. |
