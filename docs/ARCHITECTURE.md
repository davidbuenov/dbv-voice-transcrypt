# 🏗 Arquitectura Técnica: DBV VoiceTranscrypt

> **Fase:** `/plan` (Planificación Técnica)
> **Estado:** Validado
> **Última Revisión:** 2026-05-08 (Refactorización a WhisperX)

---

## 🛠 Stack Tecnológico

| Capa | Tecnología | Justificación |
| --- | --- | --- |
| **Lenguaje Backend** | Python 3.x | Ecosistema líder para IA y procesamiento de audio. |
| **Framework Backend** | FastAPI | Alto rendimiento asíncrono para subida de archivos y streaming de datos. |
| **Frontend** | Vanilla JS, CSS, HTML | Simplicidad, velocidad y control total sobre la estética "premium". |
| **Transcripción (MVP)** | WhisperX (faster-whisper) | Estándar superior (70x velocidad) con soporte de Diarización vía Pyannote. |
| **LLM (Fase 2)** | Gemma 4 (Local) / Gemini API | Opciones flexibles para análisis de texto y resúmenes. |

---

## 📂 Estructura de Directorios

```text
/
├── backend/
│   ├── main.py            # API y orquestación
│   ├── whisper_service.py # Lógica de IA (WhisperX en 3 fases: transcribe, align, diarize)
│   ├── llm_service.py     # Lógica de IA de texto (Gemma/Gemini)
│   ├── requirements.txt   # Dependencias de Python
│   └── .env               # (Opcional) Token de HuggingFace para la diarización
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│   │   └── app.js
├── audio/                 # Almacenamiento local temporal de grabaciones
├── install.cmd            # Instalador robusto con detección inteligente de Python y CUDA
└── docs/                  # Documentación del ciclo de vida (SDD)
```

---

## 🔑 Decisiones Técnicas Clave

### Privacidad y Seguridad
- **Procesamiento Local:** El núcleo de la aplicación es la privacidad. Ningún audio sale del servidor local. Incluso con la integración de Pyannote para la diarización, el token se usa únicamente para descargar los pesos matemáticos iniciales.
- **Inferencia Eficiente:** Uso de `faster-whisper` a través de WhisperX. Ajuste dinámico de precisión (`float16` en CUDA, `int8` en CPU) para garantizar que corra en cualquier máquina.

### Experiencia de Usuario (UX)
- **Instalación "Zero Config":** Creación de un `install.cmd` a prueba de fallos para entornos Windows que prioriza el repositorio oficial de CUDA sobre PyPI, evitando sobreescrituras en las dependencias.
- **Degradación Elegante:** Si el usuario no tiene el HF_TOKEN configurado, el sistema simplemente omite la separación por locutores sin lanzar errores.

---

## ⚠️ Restricciones y Riesgos Técnicos

- **Limitación de Hardware:** A pesar de la eficiencia de WhisperX, la VRAM sigue siendo un factor.
  - **Mitigación:** Instalador que fuerza el ecosistema CUDA para aprovechar las GPUs dedicadas (ej. NVIDIA Serie RTX) o decaimiento nativo a CPU en `int8`.
- **Tiempos de Procesamiento:** 
  - **Mitigación:** Sistema asíncrono con WebSockets que mantiene al usuario informado en cada fase de WhisperX (Descarga de audio -> Transcripción -> Alineación -> Diarización).
