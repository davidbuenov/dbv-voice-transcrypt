# Changelog - DBV VoiceTranscrypt

Todos los cambios notables en este proyecto serán documentados en este archivo. El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Sin publicar]

## [2.1.0] - 2026-08-09

### 🔒 Code Simplify + Auditoría de Seguridad
- **Security fix:** `/upload` y el WebSocket `/ws/transcribe` usaban el nombre de fichero enviado por el cliente sin sanear (`os.path.join(UPLOAD_DIR, filename)`), permitiendo en teoría un path traversal (`../../`) o una ruta absoluta para escribir/leer fuera de `backend/uploads/`. Se añade `_uploaded_file_path()`, que aplica `os.path.basename()` antes de unir la ruta, usado en ambos puntos.
- **Fixed:** `analyze_with_claude` no fijaba `max_tokens` explícito de forma generosa (4096), truncando transformaciones largas (`full_content`, `mindmap`) sobre transcripciones extensas. Subido a 8192.
- **Fixed:** `analyze_with_gemma_local` construía su propio texto de "prompt personalizado" en vez de reutilizar `_resolve_system_instruction`, dando un comportamiento distinto al mismo `custom_prompt` según el proveedor. Unificado.
- **Fixed:** `/api/analyze` invocaba los SDKs de Gemini/OpenAI/Claude/Gemma (síncronos, bloqueantes) directamente dentro del handler `async`, congelando el event loop de FastAPI durante toda la llamada de red — lo que también bloqueaba los mensajes de progreso del WebSocket de transcripción para otras sesiones. Ahora se ejecutan en el threadpool de FastAPI (`run_in_threadpool`).
- Pequeña limpieza de duplicación en `frontend/js/app.js` (`handleAiAnalysis` ahora reutiliza el helper `currentProvider()`).
- Auditoría de seguridad del checklist obligatorio de esta fase: sin credenciales hardcodeadas, dependencias (`openai`, `anthropic`, `mcp`) verificadas como paquetes oficiales reales en PyPI, `.env` reales confirmados fuera de git.
- 6 tests nuevos (path traversal en upload, límites y dispatch). **25/25 tests pasan** (17 backend + 8 agent-plugin).

### ✨ Soporte Multi-proveedor LLM
- Añadido soporte para **OpenAI (GPT-5.6 Sol/Terra/Luna)** y **Anthropic Claude (Opus 5/Sonnet 5/Haiku 4.5)** como proveedores de análisis, junto a Gemini y Gemma 4 local.
- Catálogo de modelos Gemini actualizado a la generación 3.x vigente (`gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-pro-preview`).
- Cada proveedor guarda su propia API Key en `localStorage` (namespaced), evitando enviar la clave de un proveedor a otro al cambiar de modelo.

### 🤖 Agent Plugin (MCP Server)
- Nuevo servidor MCP en `agent-plugin/` (estándar Agent Plugins 1.0.0) con dos herramientas para agentes de IA: `transcribe_audio` (WhisperX puro, sin LLM) y `analyze_transcription` (aplica cualquier prompt del catálogo sobre un texto ya transcrito, en los 4 proveedores).
- `transcribe_audio` restringe las rutas admitidas a `backend/uploads/` para evitar que un agente transcriba archivos arbitrarios del sistema.
- Skill `voice-transcrypt-analysis` documentando el catálogo de transformaciones y el flujo recomendado.
- `backend/.env.example` documenta las 3 variables (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) que usa el MCP server; la interfaz web sigue sin necesitarlas (clave en `localStorage` del navegador).
- **Fixed:** los `print()`/logging que dispara la carga del modelo WhisperX al importar `whisper_service` corrompían el canal `stdio` de MCP (que debe llevar solo JSON-RPC) porque ocurrían antes de que el SDK tomara el control de stdout; se corrige redirigiendo esa ventana de arranque a stderr.
- **Fixed:** un `.env` sin rellenar (copiado tal cual de `.env.example`) se aceptaba como API Key válida y producía un error de autenticación confuso del proveedor en vez de avisar de que falta configurar la variable.

### 🔧 Configuración de Gemma 4 Local
- **Fixed:** `gemma4/.env` (host, puerto, contexto, capas de GPU, flash attention) existía pero no lo leía nadie — `gemma4/start_gemma.py` tenía esos valores hardcodeados y `backend/llm_service.py` tenía la URL fija a `127.0.0.1:8080`. Ahora ambos leen el mismo `gemma4/.env`, así que cambiarlo ahí (por ejemplo, para liberar el puerto 8080 o ajustar `LLAMA_N_GPU_LAYERS` a tu VRAM) surte efecto de verdad en los dos sitios.
- Añadido `gemma4/.env.example` documentando las 5 variables (sin secretos, pero configuración específica de cada máquina — se mantiene fuera de git como `backend/.env`).

### 🎨 Rediseño de Interfaz ("Estudio Técnico")
- Sustituido el sistema visual anterior (glassmorphism, degradado índigo/violeta, Inter vía Google Fonts, iconos emoji + Font Awesome) por una estética plana sin dependencias de red: fondo carbón/gris neutro, acento ámbar único, tipografía de sistema y un set propio de iconos SVG lineales (`frontend/js/icons.js`).
- Actualizado `docs/DESIGN.md` como fuente de verdad de la nueva paleta y normas de componentes.
- **Fixed:** el spinner de "Analizando..." (`.loader`) no tenía estilos definidos y era invisible; ahora usa una animación CSS propia.

## [2.0.0] - 2026-05-08

### ✨ Nuevas Características
- **Reconocimiento de Locutores (Speaker Diarization)**: Integración con Pyannote Audio para identificar y etiquetar quién está hablando en cada momento (configurable vía token de Hugging Face en `.env`).
- **Motor WhisperX (faster-whisper)**: Refactorización completa del backend, sustituyendo el modelo estándar de OpenAI Whisper por WhisperX, lo que permite transcripciones hasta 70x más rápidas manteniendo la ejecución 100% local.
- **Pipeline de 3 Fases**: La transcripción ahora se divide en Transcripción inicial, Alineación a nivel de palabra y Diarización, enviando feedback en tiempo real al frontend vía WebSockets en cada etapa.

### 🛠️ Infraestructura
- **Instalador Inteligente (`install.cmd`)**: Nuevo script "Zero Config" que detecta la versión de Python, gestiona entornos virtuales y fuerza la instalación del ecosistema NVIDIA CUDA más puntero (`cu126`) evitando conflictos con las dependencias genéricas de PyPI.
- **Optimización de Memoria**: Limpieza automática de la VRAM (Garbage Collection y CUDA empty_cache) entre las fases de procesamiento para soportar modelos más grandes en tarjetas gráficas estándar.

## [1.0.0] - 2026-05-05
- **Transcripción Local Multi-archivo**: Soporte completo para procesar múltiples audios en una sola sesión usando **OpenAI Whisper**.
- **Aceleración GPU (CUDA)**: Detección automática y uso de la tarjeta gráfica para transcripciones ultra rápidas.
- **Gestión de Sesiones**: Interfaz dinámica para añadir, eliminar y reordenar archivos manualmente antes del procesamiento.
- **Inteligencia Híbrida**: Integración con **Google Gemini** (Cloud) y **Gemma 4** (Local via llama-server).
- **Panel de Análisis Avanzado**: 8 modos predefinidos (Resumen, Acciones, Q&A, Email de Seguimiento, Tono/Sentimiento, etc.).
- **Prompt Personalizado**: Opción de enviar instrucciones específicas a la IA con una UI dedicada.
- **Módulo Gemma 4 Autónomo**: Carpeta `gemma4/` desacoplada con scripts de descarga (`setup.cmd`) y lanzadores independientes.

### 🎨 UI/UX (Deep Space System)
- Interfaz moderna basada en **Glassmorphism** y modo oscuro.
- Consola de estado en tiempo real para monitorizar el progreso de la IA y el servidor.
- Feedback dinámico de modelos y bypass de API Key para inferencia local.

### 🛠️ Infraestructura
- **Estandarización v1.3.0**: Aplicación del framework `dbv-specs-ops` con cabeceras de autoría y licencias en todo el código.
- **Entorno Robusto**: Configuración optimizada para **Python 3.12** con gestión de dependencias estricta.

### 🚀 Otros
- Scripts de utilidad: `start.cmd`, `stop.cmd` y `start_gemma.cmd`.
- Documentación completa siguiendo el estándar SDD.

---
*Creado por David Bueno Vallejo (@davidbuenov)*
