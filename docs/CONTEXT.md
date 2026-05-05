# 🧠 DBV VoiceTranscrypt: Contexto del Proyecto

Este documento sirve como resumen de alto nivel para la recuperación rápida de contexto por parte de humanos y agentes de IA. Complementa a la documentación técnica detallada en `docs/`.

## 📋 Resumen Ejecutivo
**DBV VoiceTranscrypt** es una plataforma de **transcripción segura y local**. Su objetivo es permitir que profesionales (profesores, abogados, ejecutivos) transcriban y analicen audios sensibles sin que la información salga nunca de su entorno local.

## 🛠 Stack Tecnológico
- **Core:** Python 3.x + FastAPI.
- **Frontend:** Vanilla JS, CSS puro y HTML5 (Diseño Premium/Moderno).
- **IA de Voz:** OpenAI Whisper (Local).
- **IA de Texto:** Gemma 4 (Local) o Gemini API (Nube - opcional).

## 📐 Principios de Arquitectura
1. **Privacidad por diseño:** El procesamiento local es la prioridad absoluta.
2. **Spec-Driven Development (SDD):** El desarrollo se guía por las especificaciones en la carpeta `docs/`.
3. **Simplicidad:** Interfaz limpia (estilo Plaud Note Pro) sin sobrecarga de frameworks en el frontend.

## 📈 Estado y Hitos
- **Hito 1 (MVP):** Completado. Transcripción funcional con Whisper local y WebSockets para progreso en tiempo real. Interfaz Drag & Drop operativa.
- **Hito 2 (Análisis):** En planificación. Integración de LLMs para resúmenes y minutas automáticas.

## 📂 Guía de Documentación
- `docs/SPECIFICATIONS.md`: Requisitos y lógica de negocio.
- `docs/ARCHITECTURE.md`: Detalles técnicos e infraestructura.
- `task.md`: Estado actual de las tareas y snapshot del último avance.

---
*Este documento es una copia portátil del Knowledge Item del proyecto.*
