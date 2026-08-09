# Voice Transcrypt — Transcripción y Análisis

Este skill documenta cómo usar las tools MCP `transcribe_audio` y
`analyze_transcription` del servidor `voice-transcrypt` para transcribir y
analizar audio local sin pasar por la interfaz web.

## Flujo recomendado

1. Transcribe el audio **una sola vez** con `transcribe_audio(file_path)`.
   - `file_path` debe apuntar a un fichero ya existente dentro de `backend/uploads/`.
   - No requiere ninguna API key: es reconocimiento de voz puro (WhisperX).
2. Analiza el texto resultante **tantas veces como necesites** con
   `analyze_transcription`, sin repetir la transcripción (que es el paso caro).

## Catálogo de transformaciones (`transformation`)

| Valor | Qué hace |
| --- | --- |
| `summary` | Resumen ejecutivo profesional |
| `concepts` | Glosario de conceptos clave |
| `mindmap` | Esquema jerárquico de los temas tratados |
| `speaker_profiling` | Perfil/rol de cada locutor (requiere transcripción con diarización, etiquetas `[SPEAKER_XX]`) |
| `speaker_contributions` | Ideas principales aportadas por cada locutor |
| `speaker_actions` | Lista de tareas asignadas por locutor |
| `speaker_interview` | Reescribe la transcripción en formato entrevista |
| `template` | Plantilla inteligente (apuntes / acta / Q&A según el contenido) |
| `full_content` | Reescritura fluida y completa, sin resumir |
| `qa` | Preguntas y respuestas detectadas |
| `followup` | Email de seguimiento con acuerdos y tareas |
| `sentiment` | Análisis de tono y sentimiento |
| `custom` | Prompt libre — usa el parámetro `custom_prompt` en vez de `transformation` predefinida |

## Proveedores (`provider` / `model`)

| provider | Variable de entorno requerida | Modelos de ejemplo |
| --- | --- | --- |
| `gemini` | `GEMINI_API_KEY` | `gemini-3.6-flash`, `gemini-3.1-pro-preview` |
| `openai` | `OPENAI_API_KEY` | `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` |
| `claude` | `ANTHROPIC_API_KEY` | `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5-20251001` |
| `gemma-local` | ninguna (requiere `llama-server` corriendo en `127.0.0.1:8080`) | `gemma-4` |

Las variables de entorno se leen de `backend/.env` — el mismo fichero que usa
la aplicación web, no uno separado para el plugin.

## Ejemplo de uso

```
transcribe_audio(file_path="backend/uploads/reunion.wav")
→ "[SPEAKER_00]: Hola a todos...\n\n[SPEAKER_01]: Buenas..."

analyze_transcription(
  text="<texto anterior>",
  transformation="speaker_actions",
  provider="claude",
  model="claude-sonnet-5",
)
→ Lista de tareas asignadas por locutor en Markdown.
```
