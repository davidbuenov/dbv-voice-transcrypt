# 🎨 Guía de Diseño: DBV VoiceTranscrypt

Este documento establece las normativas visuales y de UX del proyecto para evitar el "slop" de interfaces genéricas de IA y mantener un estándar **premium, limpio y funcional**.

> **Revisión 2026-08-09:** Se sustituye la estética anterior (glassmorphism + degradado índigo/violeta sobre azul-marino, Inter vía Google Fonts, iconos emoji + Font Awesome) por la dirección **"Estudio Técnico"**, porque el combo anterior es, en la práctica, la paleta más repetida en interfaces generadas por IA y se detecta de inmediato. Además dependía de dos CDNs externas, contradiciendo el principio "local-first" de este mismo documento.

## 1. Filosofía General
- **Local-first & Independencia:** Cero dependencias de red críticas en el frontend. Tipografía basada en la pila de fuentes del sistema (sin webfonts descargados); iconos como SVG inline propios (sin Font Awesome ni emojis).
- **Anti-AI-Slop:** Sin degradados decorativos, sin `backdrop-filter` generalizado, sin "glow shadows" en hover. Las superficies son planas, con bordes finos de 1px como único recurso de separación.
- **Estudio Técnico:** La app procesa audio con herramientas técnicas (WhisperX, diarización); la estética debe evocar una consola de estudio seria, no un dashboard de SaaS genérico.
- **Minimalismo Estructural:** El contenido principal (la transcripción y los controles) debe brillar por encima de elementos decorativos innecesarios.

## 2. Paleta de Colores
Sistema de variables CSS adaptable (Light / Dark), sin tintes azulados en los neutros y con un único acento (ámbar) usado con moderación — nunca como degradado.

**Dark (por defecto):**
| Token | Valor | Uso |
| --- | --- | --- |
| `--bg-color` | `#14151a` | Fondo base, gris carbón plano (no azulado) |
| `--surface-color` | `#1c1d24` | Paneles, tarjetas |
| `--surface-hover` | `#22232b` | Estado hover de superficies |
| `--border-color` | `#2a2b33` | Bordes por defecto |
| `--border-strong` | `#3a3c46` | Bordes en hover/focus |
| `--text-primary` | `#eef0f2` | Texto principal |
| `--text-secondary` | `#9a9ea6` | Texto secundario |
| `--accent` | `#e8a33d` | Ámbar — iconos, enlaces, bordes activos |
| `--accent-strong` | `#c9791a` | Ámbar oscuro — fondo de botones primarios |
| `--on-accent` | `#14151a` | Texto/icono sobre `--accent` |
| `--success` | `#3fb950` | Estados de éxito |
| `--error` | `#f85149` | Estados de error |

**Light:**
| Token | Valor | Uso |
| --- | --- | --- |
| `--bg-color` | `#f4f4f6` | Fondo base, gris neutro |
| `--surface-color` | `#ffffff` | Paneles, tarjetas |
| `--surface-hover` | `#f0f0f2` | Estado hover de superficies |
| `--border-color` | `#dfe0e4` | Bordes por defecto |
| `--border-strong` | `#c7c9d0` | Bordes en hover/focus |
| `--text-primary` | `#16171c` | Texto principal |
| `--text-secondary` | `#62656d` | Texto secundario |
| `--accent` | `#a15d12` | Ámbar oscurecido — mantiene 4.5:1 sobre blanco |
| `--accent-strong` | `#8a4e0f` | Fondo de botones primarios (texto blanco) |
| `--on-accent` | `#ffffff` | Texto/icono sobre `--accent-strong` |
| `--success` | `#1a7f37` | Estados de éxito |
| `--error` | `#cf222e` | Estados de error |

La consola de estado (`.status-console`) mantiene un fondo oscuro y texto monoespaciado en **ambos** temas — es un elemento deliberadamente "técnico" (terminal), no parte de la superficie general.

## 3. Tipografía
- **Fuente Principal:** Pila de sistema — `-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, Roboto, sans-serif`. Sin webfonts: evita la dependencia de Google Fonts y la firma visual de "Inter" tan asociada a interfaces generadas por IA.
- **Fuente Monoespaciada (consola):** `ui-monospace, "Cascadia Code", "Segoe UI Mono", Consolas, "Courier New", monospace`.
- Jerarquía:
  - `h1`: 1.3rem, bold, sin tracking negativo agresivo (las fuentes de sistema no lo necesitan).
  - `h2`: 1.1–1.4rem, semi-bold.
  - Párrafos: 1rem, line-height 1.7 para facilitar la lectura de transcripciones largas.

## 4. Componentes y Efectos Visuales
- **Superficies planas:** Sin `backdrop-filter`/glassmorphism. Bordes finos de 1px (`var(--border-color)`) en vez de sombras pesadas o blur.
- **Sin degradados:** Ningún fondo ni botón usa `linear-gradient`. El acento se aplica como color sólido.
- **Hover = cambio de borde/superficie, no elevación:** al pasar el ratón, los componentes cambian `border-color` a `--border-strong` y/o fondo a `--surface-hover`. No se usa `transform: translateY()` ni sombras de "glow".
- **Bordes redondeados moderados:** `8px` en botones/inputs, `10px` en tarjetas y paneles — nunca por encima de `12px`.
- **Iconos:** un único set de SVG lineal inline (trazo `1.75px`, `currentColor`), definido en `frontend/js/icons.js`. Prohibido usar emoji como icono funcional.
- **Consola / Logs:** fuente monoespaciada, fondo muy oscuro, colores semánticos (`--success` para éxito, `--error` para error), igual en ambos temas.

## 5. Checklist de Implementación UI (Junior-Designer Workflow)
Antes de dar por válido un nuevo componente en CSS/HTML, verificar:
- [ ] ¿Tiene estados `:hover` y `:active` sin usar `transform`/glow?
- [ ] ¿Usa solo colores sólidos (sin `linear-gradient`)?
- [ ] ¿Mantiene la coherencia de paddings (ej. múltiplos de `0.25rem` o `0.5rem`)?
- [ ] ¿Se adapta a pantallas pequeñas (diseño fluido / flexbox)?
- [ ] ¿El contraste texto/fondo es superior a 4.5:1?
- [ ] ¿Los iconos son SVG del set propio (`icons.js`), no emoji ni Font Awesome?
