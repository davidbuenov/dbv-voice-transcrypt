# 📋 Especificaciones: DBV VoiceTranscrypt

> **Fase:** `/spec` (Especificación)
> **Estado:** Validado
> **Última Revisión:** 2026-05-08 (Migración a WhisperX y soporte de Diarización)

---

## 🎯 1. Contexto y Objetivos

- **Problema:** Los usuarios necesitan transcribir grabaciones de audio largas y sensibles (clases universitarias, reuniones de empresa, entrevistas) de forma privada y segura. Los archivos suelen ser grandes (~256MB) y en formatos como `.wav`.
- **Objetivo (Éxito):** Crear una aplicación web local (**DBV VoiceTranscrypt**), moderna y fácil de usar (drag & drop). La aplicación transcribirá los audios de forma ultrarrápida usando **WhisperX** en local, garantizando la privacidad total y permitiendo opcionalmente distinguir a los diferentes hablantes (Diarización). En una segunda fase, permitirá generar resúmenes y minutas usando un LLM local (**Gemma 4**) o en la nube (**Gemini**).

## 👥 2. Usuarios y Escenarios

- **Perfil de Usuario:** Profesionales, profesores y usuarios que manejan información confidencial y requieren procesamiento local.
- **Escenarios Clave:**
  - *Escenario A (Reunión/Clase):* El usuario termina una sesión, arrastra el archivo de audio a la interfaz y la transcripción comienza en segundo plano de forma segura y local, diferenciando quién dice qué si se configuró el token.
  - *Escenario B (Análisis):* Una vez finalizada la transcripción, el usuario solicita un resumen o puntos clave para generar un documento de seguimiento.

## ✨ 3. Funciones Principales (Requisitos)

- [x] **Frontend Moderno:** Interfaz web premium con Vanilla JS, CSS y HTML. Diseño tipo "Glassmorphism" con zona de Drag & Drop intuitiva.
- [x] **Procesamiento de Audio:** Soporte para archivos pesados (256MB+) y diversos formatos (.wav, .mp3, etc.).
- [x] **Transcripción Local:** Integración con **WhisperX** ejecutándose localmente para máxima privacidad, velocidad (faster-whisper) y alineación a nivel de palabra.
- [x] **Reconocimiento de Locutores:** Soporte para Diarización opcional mediante `pyannote-audio` (configurado vía `.env`).
- [x] **Generación de Resúmenes (Fase 2):** Integración con Gemini API y Gemma 4 (local) completada con éxito.
- [ ] **Soporte Multi-proveedor LLM:** Añadir **OpenAI (GPT-5.6)** y **Anthropic Claude (familia Claude 5)** como proveedores adicionales de análisis, junto a Gemini (catálogo de modelos actualizado) y Gemma 4 local. El usuario elige proveedor y modelo desde el mismo selector que ya existe.
- [ ] **Agent Plugin (MCP Server):** Exponer la transcripción y el análisis como herramientas MCP invocables directamente desde agentes de IA (Claude Code, Claude Desktop, Cursor), sin pasar por la interfaz web.

## 🏗️ 4. Propuesta de Solución Técnica (Resumen)

- **Enfoque:** Backend en Python con FastAPI para manejar subidas asíncronas. Frontend "vanilla" modular y ligero. Uso de WhisperX para la lógica de IA de voz. Instalador automático robusto para compatibilidad de GPU.
- **Sistema de Diseño:** Ver `docs/DESIGN.md` para tokens de color, tipografía, componentes y filosofía visual "Estudio Técnico".

### Multi-proveedor LLM

- **Backend (`llm_service.py`):** dos nuevas funciones `analyze_with_openai` y `analyze_with_claude`, con la misma firma que `analyze_with_gemini` (texto, modelo, api_key, transformation, custom_prompt). Usan los SDKs oficiales (`openai`, `anthropic`) — se añaden a `backend/requirements.txt`.
- **Catálogo de modelos (verificado por búsqueda web el 2026-08-09, sujeto a quedar obsoleto — ver Riesgos):**
  - **Gemini:** `gemini-3.6-flash` (GA), `gemini-3.5-flash` (GA), `gemini-3.5-flash-lite` (GA), `gemini-3.1-pro-preview` (Preview, razonamiento más potente).
  - **OpenAI:** `gpt-5.6-sol` (frontera), `gpt-5.6-terra` (equilibrado), `gpt-5.6-luna` (económico).
  - **Claude:** `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5-20251001`.
  - **Local:** `gemma-4` (sin cambios, vía `llama-server`).
- **Gestión de claves (frontend):** cada proveedor tiene su propia clave en `localStorage` (namespaced, ej. `openai_api_key`, `claude_api_key`), igual que ya ocurre hoy con `gemini_api_key`. El campo de API Key cambia de placeholder y valor guardado según el proveedor seleccionado. Gemma local sigue sin necesitar clave. Las claves nunca se persisten en el servidor.

### Agent Plugin (MCP Server)

- **Ubicación:** `agent-plugin/` en la raíz del proyecto — no `.well-known/`, porque `Agent Readiness (Web) = No` (este plugin es para consumo local desde IDEs, no para descubrimiento web público).
- **Tool 1 — `transcribe_audio(file_path)`:** reutiliza `backend/whisper_service.py` tal cual. Solo acepta rutas dentro de `backend/uploads/`, para que un agente no pueda pedir transcribir un archivo arbitrario del disco del usuario.
- **Tool 2 — `analyze_transcription(text, transformation, custom_prompt, provider, model)`:** reutiliza `backend/llm_service.py` (mismo catálogo `PROMPT_TEMPLATES`, ahora con 4 proveedores). `provider` = `"gemini"` / `"openai"` / `"claude"` / `"gemma-local"`.
- **Credenciales:** las API keys se leen de variables de entorno (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) — nunca como parámetro de la llamada MCP. Se reutiliza el mismo `.env` de `backend/` (decisión del usuario, prioriza simplicidad sobre portabilidad del plugin como paquete aislado). El error debe indicar explícitamente el nombre de la variable que falta.
- **Skill complementario:** `agent-plugin/skills/voice-transcrypt-analysis/SKILL.md` documentará el catálogo de transformaciones disponibles y el flujo recomendado (transcribe una vez → analiza N veces).

## 🚫 5. Fuera de Alcance (Out of Scope)

- [x] Autenticación de usuarios (herramienta de uso personal/local).
- [x] Almacenamiento persistente en base de datos externa (se usa el sistema de archivos local).
- [x] Exponer el MCP server en modo remoto (`streamable-http`/`sse`) — de momento solo `stdio` local.

## ⚠️ 6. Riesgos y Mitigación

- **Riesgo:** Consumo elevado de recursos (RAM/CPU) al procesar archivos grandes.
  - **Mitigación:** Uso del motor `faster-whisper` (incorporado en WhisperX) y formato `int8` automático en CPU para minimizar drásticamente el consumo de recursos frente al Whisper estándar.
- **Riesgo:** Confusión del usuario con la configuración de Pyannote.
  - **Mitigación:** Hacer la configuración de Hugging Face totalmente opcional y añadir un `install.cmd` a prueba de fallos.
- **Riesgo:** Los nombres/IDs de modelo de los 3 proveedores cloud quedan obsoletos con frecuencia (nuevas versiones cada pocas semanas).
  - **Mitigación:** Catálogo centralizado en un único lugar (`frontend/index.html` + lista de referencia en este documento) con fecha de verificación explícita, fácil de localizar y actualizar.
- **Riesgo:** Un agente MCP podría intentar transcribir archivos fuera del ámbito de la app.
  - **Mitigación:** `transcribe_audio` valida que la ruta resuelta esté dentro de `backend/uploads/`.
- **Riesgo:** Fuga de API keys si se pasaran por argumento de proceso en el MCP server.
  - **Mitigación:** solo por variable de entorno, nunca como parámetro de la tool.

## ❓ 7. Preguntas Abiertas

- Ninguna por el momento.