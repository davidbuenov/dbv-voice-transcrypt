// =============================================================================
// DBV VoiceTranscrypt — Aplicación web para la transcripción y análisis de audio de forma 100% local con Whisper y Gemma 4.
// Copyright (c) 2026 David Bueno Vallejo · https://github.com/davidbuenov
// Licensed under the MIT License. See LICENSE for details.
// Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
// =============================================================================
//
// Set de iconos SVG lineal propio (ver docs/DESIGN.md). Sustituye a Font Awesome
// para los elementos generados dinámicamente por app.js, evitando dependencias
// de red externas.

const Icons = (() => {
    const paths = {
        'file-audio': '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="14 3 14 9 20 9"></polyline><polyline points="8 15 9.5 12 11 16 12.5 11 14 15"></polyline>',
        'loader': '<path d="M12 3a9 9 0 1 0 9 9"></path>',
        'check-circle': '<circle cx="12" cy="12" r="9"></circle><polyline points="8 12.5 11 15.5 16 9"></polyline>',
        'chevron-up': '<polyline points="6 15 12 9 18 15"></polyline>',
        'chevron-down': '<polyline points="6 9 12 15 18 9"></polyline>',
        'x': '<line x1="6" y1="6" x2="18" y2="18"></line><line x1="6" y1="18" x2="18" y2="6"></line>',
    };

    function svg(name, size = 16) {
        const inner = paths[name];
        if (!inner) return '';
        const spin = name === 'loader' ? ' icon-spin' : '';
        return `<svg class="icon-svg${spin}" viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">${inner}</svg>`;
    }

    return { svg };
})();
