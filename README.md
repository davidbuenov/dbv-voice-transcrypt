# 🎙️ DBV VoiceTranscrypt

Una aplicación web moderna y segura diseñada para la transcripción y el análisis de audio de forma **100% local**. Ideal para reuniones corporativas, entrevistas, clases universitarias y notas de voz personales, donde la privacidad de la información es la máxima prioridad.

## 🌟 Características Principales

- **Privacidad Blindada**: Procesamiento de audio completamente local utilizando **OpenAI Whisper**. Tus grabaciones nunca salen de tu máquina.
- **Transcripción Segura**: Diseñado para manejar información sensible sin dependencias de la nube.
- **Multiproposito**: Optimizado para grabaciones largas (clases, juntas de trabajo, entrevistas) en formatos como `.wav` de 256MB+.
- **Interfaz Premium**: Frontend limpio construido en Vanilla JS/CSS/HTML con zona de arrastrar y soltar (Drag & Drop) y una experiencia de usuario fluida.
- **Operación Asíncrona**: Transcripción en segundo plano para mantener la productividad.

### 🧠 Análisis de Texto (Fase 2 Completada)
- **Generación de Contenido**: Resúmenes ejecutivos, mapas mentales, extracción de acciones clave (TODOs) y formato inteligente.
- **Modelos Locales Soportados**: Integración directa con **Gemma 4** (`llama-server`) para un procesamiento de texto completamente privado e independiente.
- **Modelos de Nube Soportados**: Soporte completo para las últimas versiones de la API de **Google Gemini** (hasta Gemini 3.1 Pro Preview).

## 🛠️ Tecnologías

- **Backend**: Python 3.x, FastAPI.
- **Frontend**: Vanilla JS, CSS puro, HTML5.
- **IA (Transcripción)**: OpenAI Whisper (Local).
- **IA (Análisis)**: Módulo autónomo Gemma 4 Local / Integración Gemini API.

## 📂 Estructura del Proyecto

```text
/
├── backend/            # Servidor FastAPI y lógica de transcripción segura
├── frontend/           # Interfaz de usuario (HTML, CSS, JS)
├── audio/              # Directorio de trabajo para archivos locales
├── gemma4/             # Módulo independiente para lanzar Gemma 4 (Llama.cpp)
├── docs/               # Documentación, especificaciones y arquitectura
├── start.cmd           # Utilidad para arrancar backend y frontend
├── start_gemma.cmd     # Utilidad para arrancar el servidor local de Gemma 4
└── stop.cmd            # Utilidad para cerrar procesos de forma limpia
```

## 🧠 Metodología: Spec-Driven Development (SDD)

Este proyecto sigue la metodología **Spec-Driven Development (SDD)**. La documentación en `docs/` es la fuente única de verdad:

- `docs/SPECIFICATIONS.md`: Requisitos detallados y casos de uso.
- `docs/ARCHITECTURE.md`: Decisiones técnicas y stack tecnológico.
- `task.md`: Seguimiento del progreso y captura de contexto.

## 🚀 Inicio Rápido

1. Clona el repositorio.
2. Instala dependencias: `pip install -r backend/requirements.txt`
3. Inicia la aplicación (servidor y frontend): Haz doble clic en **`start.cmd`**
4. Sirve el frontend y empieza a transcribir de forma segura.
5. *(Opcional)* Si quieres utilizar el LLM en local sin conexión a internet, arranca **`start_gemma.cmd`**. Para configurar esto por primera vez, **sigue las instrucciones en [gemma4/README.md](gemma4/README.md)**.
6. Usa `stop.cmd` al finalizar para liberar los recursos del sistema de Windows.

---
> Creado por [David Bueno Vallejo](https://github.com/davidbuenov)
