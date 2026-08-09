# 🏗 Arquitectura Técnica: DBV VoiceTranscrypt

> **Fase:** `/plan` (Planificación Técnica)
> **Estado:** Validado
> **Última Revisión:** 2026-08-09 (Multi-proveedor LLM + Agent Plugin/MCP)

---

## 🛠 Stack Tecnológico

| Capa | Tecnología | Justificación |
| --- | --- | --- |
| **Lenguaje Backend** | Python 3.x | Ecosistema líder para IA y procesamiento de audio. |
| **Framework Backend** | FastAPI | Alto rendimiento asíncrono para subida de archivos y streaming de datos. |
| **Frontend** | Vanilla JS, CSS, HTML | Simplicidad, velocidad y control total sobre la estética "premium". |
| **Transcripción (MVP)** | WhisperX (faster-whisper) | Estándar superior (70x velocidad) con soporte de Diarización vía Pyannote. |
| **LLM (Fase 2)** | Gemma 4 (Local) / Gemini / OpenAI / Claude | Multi-proveedor: el usuario elige según coste, privacidad o calidad. Mismo contrato de función en `llm_service.py` para los 4. |
| **Agent Plugin (Fase 3)** | MCP SDK oficial (Python, `mcp`) | Expone `transcribe_audio` y `analyze_transcription` como tools invocables por agentes de IA vía stdio. |

---

## 📂 Estructura de Directorios

```text
/
├── backend/
│   ├── main.py            # API y orquestación
│   ├── whisper_service.py # Lógica de IA (WhisperX en 3 fases: transcribe, align, diarize)
│   ├── llm_service.py     # Lógica de IA de texto (Gemma/Gemini/OpenAI/Claude)
│   ├── requirements.txt   # Dependencias de Python
│   ├── uploads/           # Audios subidos por la web (también leídos por el MCP server)
│   └── .env               # Token de HuggingFace (diarización) + API keys para el MCP server
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│   │   ├── app.js
│   │   └── icons.js       # Set de iconos SVG propio (sin CDNs externas)
├── agent-plugin/           # Agent Plugin 1.0.0 (MCP server + skill), consumo local desde IDEs
│   ├── plugin.json
│   ├── mcp.json
│   ├── mcp_server.py       # Implementa transcribe_audio y analyze_transcription
│   └── skills/
│       └── voice-transcrypt-analysis/
│           └── SKILL.md
├── audio/                 # Almacenamiento local temporal de grabaciones
├── install.cmd            # Instalador robusto con detección inteligente de Python y CUDA
└── docs/                  # Documentación del ciclo de vida (SDD)
```

---

## 🔑 Decisiones Técnicas Clave

### Privacidad y Seguridad
- **Procesamiento Local:** El núcleo de la aplicación es la privacidad. Ningún audio sale del servidor local. Incluso con la integración de Pyannote para la diarización, el token se usa únicamente para descargar los pesos matemáticos iniciales.
- **Inferencia Eficiente:** Uso de `faster-whisper` a través de WhisperX. Ajuste dinámico de precisión (`float16` en CUDA, `int8` en CPU) para garantizar que corra en cualquier máquina.

### Experiencia de Usuario (UX)
- **Instalación "Zero Config":** Creación de un `install.cmd` a prueba de fallos para entornos Windows que prioriza el repositorio oficial de CUDA sobre PyPI, evitando sobreescrituras en las dependencias.
- **Degradación Elegante:** Si el usuario no tiene el HF_TOKEN configurado, el sistema simplemente omite la separación por locutores sin lanzar errores.

---

## 🔗 Integraciones Externas

| Servicio | Propósito | Notas / Límites |
| --- | --- | --- |
| Google Gemini API | Análisis de texto (resumen, diarización, etc.) | Clave introducida por el usuario en el navegador (`localStorage`), nunca en servidor. |
| OpenAI API | Análisis de texto (alternativa a Gemini) | Ídem, clave en `localStorage` namespaced (`openai_api_key`). |
| Anthropic API (Claude) | Análisis de texto (alternativa a Gemini) | Ídem, clave en `localStorage` namespaced (`claude_api_key`). |
| Hugging Face (Pyannote) | Diarización de locutores | Token opcional en `backend/.env`, solo para descargar pesos del modelo. |

> **Catálogo de modelos vigente (verificado 2026-08-09):** ver `docs/SPECIFICATIONS.md` sección 4. Estos IDs cambian con frecuencia — antes de asumir que un modelo sigue vigente, confirmar con una búsqueda actual en vez de fiarse de esta fecha.

## ⚠️ Restricciones y Riesgos Técnicos

- **Limitación de Hardware:** A pesar de la eficiencia de WhisperX, la VRAM sigue siendo un factor.
  - **Mitigación:** Instalador que fuerza el ecosistema CUDA para aprovechar las GPUs dedicadas (ej. NVIDIA Serie RTX) o decaimiento nativo a CPU en `int8`.
- **Tiempos de Procesamiento:** 
  - **Mitigación:** Sistema asíncrono con WebSockets que mantiene al usuario informado en cada fase de WhisperX (Descarga de audio -> Transcripción -> Alineación -> Diarización).

---

## 🤖 Agent Harness (Arnés del Agente)

### 1. Gestión de Contexto (Context Engineering)
- **Contexto Estático:** `CLAUDE.md`/`GEMINI.md`/`.windsurfrules`/`.github/copilot-instructions.md` (punteros a `docs/MASTER_PROMPT.md`) + `memory.md`, cargados al inicio de cada sesión de desarrollo.
- **Contexto Dinámico / Skills:** `agent-plugin/skills/voice-transcrypt-analysis/SKILL.md` — catálogo de transformaciones de `PROMPT_TEMPLATES` y flujo recomendado (transcribir una vez, analizar N veces), cargado bajo demanda por el agente consumidor.

### 2. Herramientas y MCP (Model Context Protocol)
- **Servidor MCP Propio:** `agent-plugin/mcp_server.py`, expone dos tools:
  - `transcribe_audio(file_path)` — ASR puro (WhisperX), sin coste de LLM.
  - `analyze_transcription(text, transformation, custom_prompt, provider, model)` — aplica un prompt sobre un texto ya transcrito.
- **Propósito:** permitir que un agente de IA (Claude Code, Claude Desktop, Cursor) transcriba y analice audio del usuario sin pasar por la interfaz web.
- **Configuración de Herramientas:** definida en `agent-plugin/mcp.json` bajo el estándar Agent Plugins 1.0.0, tipo `stdio`.

### 3. Entorno de Ejecución (Sandboxing)
- **Aislamiento:** el servidor MCP corre dentro del mismo `venv` de `backend/` (reutiliza `whisper_service.py`/`llm_service.py` directamente, sin duplicar dependencias).
- **Límites de Ejecución:** `transcribe_audio` rechaza cualquier ruta fuera de `backend/uploads/` (path traversal). Sin límite de tokens propio — delega en los límites de cada proveedor LLM.
- **Aislamiento del Plugin:** variables `${PLUGIN_ROOT}`/`${PLUGIN_DATA}` soportadas en `mcp.json`, pero las API keys se resuelven desde `backend/.env` (decisión explícita del usuario: prioriza simplicidad de mantenimiento sobre portabilidad total del plugin como paquete aislado).

### 4. Guardrails Deterministas de Seguridad
- **Filtros de Código:** ninguna API key se acepta como parámetro de tool ni se loguea; solo variables de entorno.
- **Políticas de Commit/Push:** `backend/.env` ya está en `.gitignore`; no se introduce ningún fichero nuevo con secretos.

### 5. Interfaz Externa para Agentes (Agent Readiness)
- **No aplica.** `Agent Readiness (Web)` = No en `project.config.md` — esta aplicación es 100% local y no expone una API pública para descubrimiento por agentes externos. El Agent Plugin vive en `agent-plugin/` (raíz del proyecto), no en `.well-known/agent-plugin/`.
