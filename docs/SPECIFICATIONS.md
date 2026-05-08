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

## 🏗️ 4. Propuesta de Solución Técnica (Resumen)

- **Enfoque:** Backend en Python con FastAPI para manejar subidas asíncronas. Frontend "vanilla" modular y ligero. Uso de WhisperX para la lógica de IA de voz. Instalador automático robusto para compatibilidad de GPU.
- **Sistema de Diseño:** Ver `docs/DESIGN.md` para tokens de color, tipografía, componentes y filosofía visual "Deep Space".

## 🚫 5. Fuera de Alcance (Out of Scope)

- [x] Autenticación de usuarios (herramienta de uso personal/local).
- [x] Almacenamiento persistente en base de datos externa (se usa el sistema de archivos local).

## ⚠️ 6. Riesgos y Mitigación

- **Riesgo:** Consumo elevado de recursos (RAM/CPU) al procesar archivos grandes.
  - **Mitigación:** Uso del motor `faster-whisper` (incorporado en WhisperX) y formato `int8` automático en CPU para minimizar drásticamente el consumo de recursos frente al Whisper estándar.
- **Riesgo:** Confusión del usuario con la configuración de Pyannote.
  - **Mitigación:** Hacer la configuración de Hugging Face totalmente opcional y añadir un `install.cmd` a prueba de fallos.

## ❓ 7. Preguntas Abiertas

- Ninguna por el momento.