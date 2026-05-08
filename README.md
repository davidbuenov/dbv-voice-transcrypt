# 🎙️ DBV VoiceTranscrypt

[![Release](https://img.shields.io/github/v/release/davidbuenov/dbv-voice-transcrypt?display_name=tag&sort=semver)](https://github.com/davidbuenov/dbv-voice-transcrypt/releases)
![Version](https://img.shields.io/badge/version-2.0.0-blue)
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
- **Interfaz Premium**: Frontend limpio construido en Vanilla JS/CSS/HTML con zona de arrastrar y soltar (Drag & Drop) y una experiencia de usuario fluida.
- **Operación Asíncrona**: Transcripción en segundo plano para mantener la productividad.

### 🧠 Análisis de Texto (Fase 2 Completada)
- **Generación de Contenido**: Resúmenes ejecutivos, mapas mentales, extracción de acciones clave (TODOs) y formato inteligente.
- **Modelos Locales Soportados**: Integración directa con **Gemma 4** (`llama-server`) para un procesamiento de texto completamente privado e independiente.
- **Modelos de Nube Soportados**: Soporte completo para las últimas versiones de la API de **Google Gemini** (hasta Gemini 3.1 Pro Preview).

## 🛠️ Tecnologías

- **Backend**: Python 3.x, FastAPI.
- **Frontend**: Vanilla JS, CSS puro, HTML5.
- **IA (Transcripción)**: WhisperX (Local, aceleración por GPU y CPU).
- **IA (Análisis)**: Módulo autónomo Gemma 4 Local / Integración Gemini API.

## 📂 Estructura del Proyecto

```text
/
├── backend/            # Servidor FastAPI y lógica de transcripción segura (WhisperX)
├── frontend/           # Interfaz de usuario (HTML, CSS, JS)
├── audio/              # Directorio de trabajo para archivos locales
├── gemma4/             # Módulo independiente para lanzar Gemma 4 (Llama.cpp)
├── docs/               # Documentación, especificaciones y arquitectura
├── start.cmd           # Utilidad para arrancar backend y frontend
├── start_gemma.cmd     # Utilidad para arrancar el servidor local de Gemma 4
└── stop.cmd            # Utilidad para cerrar procesos de forma limpia
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
