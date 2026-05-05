# 🏗 Arquitectura Técnica: DBV VoiceTranscrypt

> **Fase:** `/plan` (Planificación Técnica)
> **Estado:** Validado
> **Última Revisión:** 2026-05-04

---

## 🛠 Stack Tecnológico

| Capa | Tecnología | Justificación |
| --- | --- | --- |
| **Lenguaje Backend** | Python 3.x | Ecosistema líder para IA y procesamiento de audio. |
| **Framework Backend** | FastAPI | Alto rendimiento asíncrono para subida de archivos y streaming de datos. |
| **Frontend** | Vanilla JS, CSS, HTML | Simplicidad, velocidad y control total sobre la estética "premium". |
| **Transcripción (MVP)** | OpenAI Whisper (Local) | Estándar de la industria para SOTA (State of the Art) ASR local. |
| **LLM (Fase 2)** | Gemma 4 (Local) / Gemini API | Opciones flexibles para análisis de texto y resúmenes. |

---

## 📂 Estructura de Directorios

```text
/
├── backend/
│   ├── main.py            # API y orquestación
│   ├── whisper_service.py # Lógica de IA (Whisper)
│   ├── llm_service.py     # Lógica de IA de texto (Gemma/Gemini)
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│   │   └── app.js
├── audio/                 # Almacenamiento local temporal de grabaciones
└── docs/                  # Documentación del ciclo de vida (SDD)
```

---

## 🔑 Decisiones Técnicas Clave

### Privacidad y Seguridad
- **Procesamiento Local:** El núcleo de la aplicación es la privacidad. Ningún audio sale del servidor local a menos que el usuario opte explícitamente por el resumen vía Gemini API en la Fase 2.
- **Inferencia Eficiente:** Uso de bibliotecas de Whisper optimizadas para CPU/GPU local.

### Experiencia de Usuario (UX)
- **Feedback en Tiempo Real:** Implementación de mecanismos para informar del progreso de la transcripción (porcentaje o pasos completados).
- **Diseño Moderno:** Uso de gradientes, micro-animaciones y layouts responsivos con CSS puro.

---

## ⚠️ Restricciones y Riesgos Técnicos

- **Limitación de Hardware:** Whisper requiere recursos considerables.
  - **Mitigación:** Permitir al usuario elegir entre diferentes tamaños de modelo (tiny, base, small) según su capacidad de hardware.
- **Tiempos de Procesamiento:** Los audios de larga duración pueden tardar varios minutos.
  - **Mitigación:** Sistema de colas o procesamiento asíncrono robusto en el backend.
