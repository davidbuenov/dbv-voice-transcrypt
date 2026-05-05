# 🎨 Guía de Diseño: DBV VoiceTranscrypt

Este documento establece las normativas visuales y de UX del proyecto para evitar el "slop" de interfaces genéricas de IA y mantener un estándar **premium, limpio y funcional**, fuertemente inspirado en filosofías como *Open Design* y productos como *Plaud AI*.

## 1. Filosofía General
- **Local-first & Independencia:** Todo debe funcionar sin dependencias de red externas críticas en el frontend (ej. fuentes empaquetadas o con graceful degradation, librerías JS/CSS locales).
- **Anti-AI-Slop:** Cada componente debe tener intención. No más diseños caóticos generados por LLMs. Se debe revisar rigurosamente:
  - Contrastes adecuados.
  - Paginación, alineaciones y "whitespace" consistentes.
  - Estados interactivos (hover, active, disabled) en todos los elementos clicables.
- **Minimalismo Estructural:** El contenido principal (la transcripción y los controles) debe brillar por encima de elementos decorativos innecesarios.

## 2. Paleta de Colores
Utilizamos un sistema de variables CSS adaptable (Light / Dark mode):
- **Fondo Base (Dark):** `#0f1115` - Un tono profundo, no completamente negro, para reducir la fatiga visual.
- **Superficies (Dark):** `#1a1d24` - Para paneles y tarjetas, creando profundidad.
- **Acento Primario:** `#5b6cf9` - Un azul vibrante que denota acción e inteligencia, sin ser el clásico "azul Bootstrap". Hover: `#4a59e3`.
- **Textos:** `#f0f0f0` (Primario) y `#9ba1a6` (Secundario).

## 3. Tipografía
- **Fuente Principal:** `Inter` (o fuentes de sistema `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto` como *fallback* local absoluto).
- Jerarquía clara:
  - `h1`: 1.25rem, bold (Para branding).
  - `h2`: 1.125rem - 1.5rem, semi-bold (Secciones).
  - Párrafos: 1rem, line-height 1.7 para facilitar la lectura de transcripciones largas.

## 4. Efectos Visuales y Componentes
- **Glassmorphism:** Uso sutil de fondos translúcidos (`rgba(26, 29, 36, 0.7)`) con desenfoque (`backdrop-filter: blur(10px)`) para elementos superpuestos como cabeceras.
- **Bordes y Sombras:** Bordes finos (`1px solid var(--border-color)`) en lugar de sombras pesadas. Bordes redondeados (`12px` a `16px` para contenedores grandes, `8px` para botones).
- **Consola / Logs:** Para elementos tipo "terminal" (estado técnico), utilizar fuente `monospace`, fondo muy oscuro, con un padding interno generoso y colores semánticos (verde para éxito, rojo para error) para mantener un contraste visual con el diseño limpio del resto de la app.

## 5. Checklist de Implementación UI (Junior-Designer Workflow)
Antes de dar por válido un nuevo componente en CSS/HTML, verificar:
- [ ] ¿Tiene estados `:hover` y `:active`?
- [ ] ¿Mantiene la coherencia de paddings (ej. múltiplos de `0.25rem` o `0.5rem`)?
- [ ] ¿Se adapta a pantallas pequeñas (diseño fluido / flexbox)?
- [ ] ¿El contraste texto/fondo es superior a 4.5:1?
- [ ] ¿Los iconos (SVGs) tienen un tamaño consistente y escalan adecuadamente con el texto?
