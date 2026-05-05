# 📋 Especificaciones: DBV VoiceTranscrypt

> **Fase:** `/spec` (Especificación)
> **Estado:** Validado
> **Última Revisión:** 2026-05-04 (Actualización de nombre y alcance)

---

## 🎯 1. Contexto y Objetivos

- **Problema:** Los usuarios necesitan transcribir grabaciones de audio largas y sensibles (clases universitarias, reuniones de empresa, entrevistas) de forma privada y segura. Los archivos suelen ser grandes (~256MB) y en formatos como `.wav`.
- **Objetivo (Éxito):** Crear una aplicación web local (**DBV VoiceTranscrypt**), moderna y fácil de usar (drag & drop). La aplicación transcribirá los audios usando **Whisper** en local para garantizar la privacidad total. En una segunda fase, permitirá generar resúmenes y minutas usando un LLM local (**Gemma 4**) o en la nube (**Gemini**).

## 👥 2. Usuarios y Escenarios

- **Perfil de Usuario:** Profesionales, profesores y usuarios que manejan información confidencial y requieren procesamiento local.
- **Escenarios Clave:**
  - *Escenario A (Reunión/Clase):* El usuario termina una sesión, arrastra el archivo de audio a la interfaz y la transcripción comienza en segundo plano de forma segura y local.
  - *Escenario B (Análisis):* Una vez finalizada la transcripción, el usuario solicita un resumen o puntos clave para generar un documento de seguimiento.

## ✨ 3. Funciones Principales (Requisitos)

- [x] **Frontend Moderno:** Interfaz web premium con Vanilla JS, CSS y HTML. Diseño tipo "Glassmorphism" con zona de Drag & Drop intuitiva.
- [x] **Procesamiento de Audio:** Soporte para archivos pesados (256MB+) y diversos formatos (.wav, .mp3, etc.).
- [x] **Transcripción Local:** Integración con el modelo OpenAI Whisper ejecutándose localmente para máxima privacidad.
- [x] **Generación de Resúmenes (Fase 2):** Integración con Gemini API y Gemma 4 (local) completada con éxito.

## 🏗️ 4. Propuesta de Solución Técnica (Resumen)

- **Enfoque:** Backend en Python con FastAPI para manejar subidas asíncronas. Frontend "vanilla" modular y ligero. Uso de Whisper para la lógica de IA de voz.
- **Sistema de Diseño:** Ver `docs/DESIGN.md` para tokens de color, tipografía, componentes y filosofía visual "Deep Space".

## 🚫 5. Fuera de Alcance (Out of Scope)

- [x] Autenticación de usuarios (herramienta de uso personal/local).
- [x] Almacenamiento persistente en base de datos externa (se usa el sistema de archivos local).

## ⚠️ 6. Riesgos y Mitigación

- **Riesgo:** Consumo elevado de recursos (RAM/CPU) al procesar archivos grandes.
  - **Mitigación:** Gestión eficiente de archivos en disco y optimización de la carga del modelo Whisper.
- **Riesgo:** Tiempos de espera prolongados.
  - **Mitigación:** Feedback visual constante y notificaciones de progreso en la interfaz.

## ❓ 7. Preguntas Abiertas

- Ninguna por el momento.