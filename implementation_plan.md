# Plan de Implementación: Fase 2 - Análisis con IA, Consola de Estado y Diseño

Este documento detalla los pasos para implementar la Fase 2 de DBV VoiceTranscrypt, inspirándonos en las capacidades de Plaud AI para el procesamiento de texto y en Open Design para establecer un estándar visual premium que huya del "diseño estándar generado por IA".

## User Review Required

> [!IMPORTANT]
> **Uso de Librerías Externas en el Frontend:** Para renderizar correctamente las respuestas estructuradas de Gemini (que vendrán en formato Markdown), propongo incluir `marked.js` vía CDN en el frontend. Al ser un proyecto "Vanilla JS", esto mantendrá la ligereza sin necesidad de bundlers. ¿Estás de acuerdo?  No me parece correcto vincular con un CDN, no es buena práctica. Quizas es mejor incluirlo en nuestro servidor o desarrollar lo que haga falta en javascript. quiero independencia de la red y poder ejecutarlo sin internet (si quisiera usar un modelo local)
>
> **SDK de Gemini en el Backend:** Se añadirá `google-generativeai` a los `requirements.txt` del backend para gestionar las peticiones a Gemini de forma segura y estructurada.

## Open Questions

> [!NOTE]
> 1. **Consola de Estado:** ¿Prefieres que la consola con el log de estado reemplace por completo a la barra de progreso actual, o que ambas coexistan (por ejemplo, barra de progreso general y debajo una cajita de texto tipo terminal que vaya añadiendo líneas)? ambas
> 2. **Almacenamiento de API Key:** Se guardará en el `localStorage` del navegador del usuario por seguridad. El backend solo la recibirá en la petición temporal para hacer la llamada a Gemini. ¿Te parece correcto este enfoque de privacidad? correcto.

## Proposed Changes

---

### Documentación y Estándares de Diseño

Crearemos un nuevo documento para evitar interfaces genéricas y mantener el estándar premium.

#### [NEW] docs/DESIGN.md
- Se redactará un documento con las directrices visuales inspiradas en *Open Design*.
- Incluirá reglas sobre tipografía (Inter), paletas de colores (Dark/Light mode, colores de acento no genéricos), uso de Glassmorphism, micro-interacciones (hover states, transiciones fluidas) y un "checklist anti-AI-slop" para asegurar que los componentes tengan padding, contraste y jerarquía consistentes.

---

### Frontend (Interfaz y Lógica)

Actualización de la UI para soportar la consola de estado y las opciones de procesamiento con IA.

#### [MODIFY] frontend/index.html
- **Consola de Estado:** Añadir un contenedor tipo terminal (`<div id="status-console">`) debajo o en lugar de la barra de progreso.
- **Panel de IA (Fase 2):** Añadir una nueva sección dentro de los resultados que contenga:
  - Input para la **API Key de Gemini** (con botón para guardar/borrar del LocalStorage).
  - Selector de **Modelos** (Gemini 1.5 Flash, Gemini 1.5 Pro, etc. con espacio futuro para Gemma 4 Local).
  - Botonera o Grid con las **Opciones de Transformación** (Inspirado en Plaud AI):
    - 📄 *Resumen Ejecutivo*
    - 📝 *Lista de Conceptos Clave*
    - ✅ *Action Items (Tareas pendientes)*
    - 🧠 *Mapa Mental / Estructura*
    - 📋 *Plantilla Inteligente (Clase / Reunión / Entrevista)*
  - Contenedor para renderizar el resultado del LLM.

#### [MODIFY] frontend/css/style.css
- Estilos para la nueva consola de estado (fondo oscuro, fuente monospace, texto verde/azul para denotar progreso).
- Estilos para el panel de IA, manteniendo el "Glassmorphism" y asegurando que los botones de opciones de transformación parezcan "Premium" (iconos SVG, hover con gradientes sutiles).

#### [MODIFY] frontend/js/app.js
- **Lógica de la Consola:** Modificar `uploadFile` y `startTranscriptionWS` para que hagan un `append` de mensajes (`console.innerHTML += ...`) en lugar de sobrescribir un texto único.
- **Lógica de IA:**
  - Leer/Guardar API Key en `localStorage`.
  - Capturar el texto transcrito y enviarlo junto con la API Key, el modelo y el tipo de transformación elegido al nuevo endpoint del backend.
  - Mostrar un estado de "Cargando IA..." y finalmente renderizar el resultado (usando Marked.js si se aprueba).

---

### Backend (Integración con LLMs)

El backend actuará como puente seguro para llamar a la API de Gemini.

#### [MODIFY] backend/requirements.txt
- Añadir `google-generativeai`.

#### [MODIFY] backend/main.py
- Crear un nuevo router/endpoint `POST /api/analyze`.
- Este endpoint recibirá: `transcription_text`, `ai_provider` (gemini), `model` (flash/pro), `api_key` y `transformation_type`.
- Implementar la lógica del sistema de prompts dependiendo de la opción elegida (ej. si elige "Action Items", el system prompt le pedirá a Gemini que extraiga solo tareas con asignados y fechas en formato Markdown).

## Verification Plan

### Automated Tests
- Arrancar el backend e instalar nuevas dependencias (`pip install -r requirements.txt`).
- Verificar que el endpoint de subida de archivos sigue funcionando y que la consola muestra los logs secuenciales correctamente.

### Manual Verification
- Subir un audio corto de prueba.
- Verificar que la consola terminal actualiza su estado en tiempo real.
- Introducir una API Key de Gemini real.
- Seleccionar "Action Items" y comprobar que Gemini devuelve un listado formateado correctamente.
- Recargar la página para asegurar que la API Key se ha guardado en el LocalStorage y no es necesario volver a introducirla.
