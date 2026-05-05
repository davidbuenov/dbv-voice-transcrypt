# Changelog - DBV VoiceTranscrypt

Todos los cambios notables en este proyecto serán documentados en este archivo. El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-05

### ✨ Características Principales
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
