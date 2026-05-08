# Rediseño de Prompts de Análisis IA y Soporte para Diarización

Este plan implementa la **Opción A** discutida: agrupar los botones de la Fase 2 (LLM) en bloques lógicos para mejorar la UX y añadir los nuevos prompts específicos que explotan las marcas de Diarización (`[SPEAKER_00]`).

## User Review Required

- Revisa los nombres y categorías propuestos en la sección de frontend. ¿Te encajan los textos e iconos elegidos? si

## Open Questions

- ¿Quieres mantener todos los botones anteriores (Plantilla Inteligente, Email de Seguimiento, etc.) o eliminamos alguno que consideres redundante ahora que tenemos los de Diarización? si podríamos quitar por ejemplo actions items.

## Proposed Changes

---

### Backend Logic

#### [MODIFY] `backend/llm_service.py`
Se añadirán 4 nuevas plantillas al diccionario `PROMPT_TEMPLATES`:
1. `speaker_profiling`: Análisis psicológico/rol de cada locutor.
2. `speaker_contributions`: Ideas clave extraídas por cada locutor.
3. `speaker_actions`: Tareas y compromisos asignados por locutor.
4. `speaker_interview`: Limpieza y formateo a formato Entrevista (Pregunta/Respuesta).

---

### Frontend UI

#### [MODIFY] `frontend/index.html`
Se rediseñará la estructura dentro del contenedor `.ai-options`. 
- Se creará un div `<div class="prompt-category">` para **Análisis General**.
- Se creará un div `<div class="prompt-category">` para **Análisis por Locutores (Diarización)**.
- El botón de **Prompt Personalizado** se mantendrá como una categoría independiente o al final.

#### [MODIFY] `frontend/css/style.css`
Se añadirán estilos muy sutiles para los títulos de las categorías (`.prompt-category-title`) para que se integren armónicamente con el diseño *Glassmorphism* (texto semitransparente, línea separadora muy fina).

## Verification Plan

### Manual Verification
- Cargar la interfaz web y comprobar que los botones no abruman gracias a la categorización.
- Ejecutar un análisis usando uno de los nuevos botones de Diarización en el audio que acabas de transcribir para verificar que la IA de Gemini interpreta correctamente las etiquetas `[SPEAKER_00]`.
