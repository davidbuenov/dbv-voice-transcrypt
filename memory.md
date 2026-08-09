# 🧠 Memoria de Aprendizajes (AI Memory)

> Contexto y Decisiones. Conocimiento cualitativo: contexto activo, decisiones técnicas (ADRs), lecciones aprendidas y mapa de relaciones. Consulta este fichero al inicio de cada sesión.

---

## 🧭 Contexto Activo

- **Proyecto:** DBV VoiceTranscrypt — transcripción y análisis de audio 100% local con WhisperX, diarización opcional (pyannote-audio) y análisis LLM multi-proveedor (Gemini / OpenAI / Claude / Gemma 4), más un Agent Plugin (servidor MCP) para agentes de IA.
- **Estado:** v2.1.0 entregada (Hito 1 MVP, Hito 2 análisis LLM+diarización, Hito 3 multi-proveedor + MCP + rediseño "Estudio Técnico"). Ver `task.md` para el snapshot exacto.

---

## 🏗️ Log de Decisiones Técnicas

- **Motor de transcripción:** Se usa WhisperX (basado en `faster-whisper`) en vez de Whisper estándar, por velocidad y alineación a nivel de palabra.
- **Diarización opcional:** `pyannote-audio` se activa solo si el usuario configura un token de Hugging Face en `.env`; si no, se omite sin bloquear el flujo principal (degradación elegante).
- **"Estudio Técnico"** elegido como dirección visual definitiva (paleta plana carbón/ámbar, tipografía de sistema, sin gradientes/blur/emoji) frente a la alternativa "Manuscrito Editorial" que se descartó.
- **Carga de `gemma4/.env`:** `llm_service.py` la resuelve por ruta absoluta (relativa a `__file__`, no al cwd), porque el fichero lo comparten `backend/main.py` (cwd=`backend/`) y `agent-plugin/mcp_server.py` (cwd arbitrario, según lo lance el cliente MCP).
- **El MCP server reutiliza `backend/.env`** para las API keys en vez de tener un `.env` propio en `agent-plugin/` — decisión explícita del usuario, prioriza simplicidad de mantenimiento sobre portabilidad del plugin como paquete aislado.

---

## ⚠️ Lecciones Aprendidas

### 📅 Sesión: Integración de WhisperX (Mayo 2026)

**1. Empatía por el Ancho de Banda (El Caso PyTorch)**
- **Aprendizaje:** Nunca dejar la resolución de dependencias masivas (como PyTorch, que pesa ~2.5GB) a la libre interpretación de `pip` en Windows. Si no se fija una versión exacta, `pip` puede descargar una versión muy nueva (ej. 2.11.0), para luego darse cuenta de que una sub-dependencia exige otra (ej. 2.8.0), forzando una doble descarga que hace perder tiempo y datos al usuario.
- **Regla de Oro:** Al crear scripts de instalación automáticos para IA, fijar siempre las versiones exactas (`torch==2.8.0`) y usar el flag `--index-url` apuntando al repositorio de CUDA correcto (`cu126` en este caso) para hacer instalaciones "quirúrgicas" de una sola pasada.

**2. Higiene del Entorno de Python**
- **Aprendizaje:** Las mezclas de versiones de CPU y GPU en Windows a menudo dejan DLLs C++ huérfanas (`torchcodec`, `torchaudio`) que rompen librerías de terceros (como `transformers`), devolviendo errores crípticos como `TypeError: 'NoneType' object is not iterable` al importar.
- **Regla de Oro:** Los scripts de instalación automática (`install.cmd`) deben incluir una fase de "Limpieza Nuclear" (`pip uninstall -y torch torchvision torchaudio`) antes de reinstalar el core de la IA, asegurando un entorno impoluto.

**3. Piensa en el Usuario Final de GitHub**
- **Aprendizaje:** Lo que funciona en el ordenador del desarrollador no siempre funciona en el del usuario que clona el repo. Asumir que el comando `python` invoca a la versión correcta es un error.
- **Regla de Oro:** Programar instaladores inteligentes (Zero Config). Por ejemplo, preguntar a Windows si tiene el launcher oficial (`py -3.12`) y forzarlo, haciendo un "fallback" seguro si no existe.

**4. Privacidad y Fallbacks Elegantes**
- **Aprendizaje:** Funcionalidades avanzadas que dependen de Hugging Face (como Diarización con Pyannote) exigen tokens y acuerdos de licencia que pueden asustar o bloquear a usuarios menos técnicos.
- **Regla de Oro:** El sistema debe funcionar de manera impecable por defecto de forma 100% local sin necesidad de tokens. Si no hay token, simplemente se omite la funcionalidad premium y se sigue adelante (Degradación elegante).

### 📅 Sesión: Actualización a dbv-specs-ops v2.4.0 (Agosto 2026)

- **Aprendizaje:** El framework migró su modelo de instalación recomendado a una subcarpeta dedicada (`dbv-specs-ops/`) a partir de v2.0.0, pero `docs/UPGRADE_PROMPT.md` no migra automáticamente proyectos existentes de estructura plana a subcarpeta — solo actualiza el contenido de los ficheros de framework en su ubicación actual.
- **Decisión:** Este proyecto se mantiene en el esquema clásico (ficheros de framework en la raíz junto al código), por decisión explícita del usuario. `docs/MASTER_PROMPT.md` y `docs/ADOPTION_PROMPT.md` fueron editados a mano para eliminar referencias a rutas `dbv-specs-ops/...` y mantenerlos coherentes con esta estructura.

### 📅 Sesión: Multi-proveedor LLM + Agent Plugin MCP (Agosto 2026)

**1. Un servidor MCP stdio no tolera ni una línea de ruido en stdout**
- **Aprendizaje:** El canal `stdio` de MCP debe llevar exclusivamente mensajes JSON-RPC. El SDK reclama el descriptor stdout solo dentro de `mcp.run()`; cualquier `print()`/logging que ocurra **antes** (ej. al importar un módulo que carga un modelo ML como efecto secundario) corrompe el protocolo y el cliente falla al parsear.
- **Regla de Oro:** Envolver cualquier import "ruidoso" en `contextlib.redirect_stdout(sys.stderr)` antes de llamar a `mcp.run()`.

**2. Claude Desktop instalado desde Microsoft Store virtualiza `%APPDATA%`**
- **Aprendizaje:** La versión MSIX de Claude Desktop corre en contenedor; editar `%APPDATA%\Claude\claude_desktop_config.json` no tiene ningún efecto porque la app nunca lee esa ruta. El fichero real está en `%LOCALAPPDATA%\Packages\Claude_<id>\LocalCache\Roaming\Claude\claude_desktop_config.json`. Ya se había sufrido este mismo problema en otro proyecto del usuario.
- **Regla de Oro:** Antes de asumir que la configuración "estándar" de una app de Windows es la correcta, comprobar si el proceso corre desde `Program Files\WindowsApps\` (MSIX) — si es así, buscar la carpeta real en `AppData\Local\Packages\`.

**3. Anthropic exige `max_tokens`; Gemini/OpenAI no**
- **Aprendizaje:** A diferencia de Gemini/OpenAI (donde el límite de salida es opcional), la API de Claude exige `max_tokens` como parámetro obligatorio. Es fácil poner un valor conservador "para que funcione" y olvidarlo — truncando en silencio transformaciones largas.
- **Regla de Oro:** Cuando un proveedor exige un límite explícito que los demás no piden, dimensionarlo pensando en el peor caso de uso real de la app (aquí: transcripciones largas sin resumir), no en un valor por defecto arbitrario.

---

## 🗺️ Mapa de Relaciones

- `docs/SPECIFICATIONS.md` ↔ `docs/ARCHITECTURE.md` ↔ `docs/DESIGN.md` — el "qué", el "cómo" y el "aspecto" del producto.
- `task.md` — estado operativo cuantitativo (qué falta, snapshot de retomada).
- `memory.md` (este fichero) — contexto cualitativo (por qué se decidió algo, qué se aprendió).

---

## 🧹 Política de Mantenimiento

Mantén este fichero por debajo de ~200 líneas activas. Cuando crezca demasiado, consolida las lecciones antiguas y de baja relevancia en `memory.archive.md`, dejando aquí solo lo vigente.
