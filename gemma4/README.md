# Gemma 4 Local Launcher

Este módulo independiente te permite lanzar el motor de **Gemma 4** (`llama-server`) en tu máquina local.
Ha sido diseñado para ser totalmente portable; puedes copiar esta carpeta `gemma4/` entera a otros proyectos que requieran un backend LLM local.

## Requisitos Previos

Necesitarás descargar los binarios del servidor y los archivos del modelo (que no se incluyen en Git por su enorme tamaño).

### 🚀 Instalación Automática (Recomendado)
Hemos simplificado todo el proceso. Solo tienes que ejecutar el siguiente archivo y el sistema descargará el motor `llama-server` y los modelos `GGUF` de 9B por ti:

1. Entra en la carpeta `gemma4/`.
2. Haz doble clic en: 🛠️ **`setup.cmd`**

---

### ¿Qué hace este proceso?

1. **Descarga llama-server**: Baja la última versión compilada para Windows con soporte CUDA (GPU) mediante `download_llama_server.py`.
2. **Descarga el Modelo Gemma 4**: Utiliza `setup_model.py` para bajar el archivo `gemma-4-E2B-it-Q4_K_M.gguf` y el proyector visual `mmproj-F16.gguf` desde HuggingFace Hub.


---

## ¿Cómo ejecutarlo?

Si estás integrando esto con **DBV VoiceTranscrypt**, simplemente vuelve a la carpeta principal del proyecto y haz doble clic en el archivo:
🚀 **`start_gemma.cmd`**

Si quieres lanzarlo directamente desde aquí:
```bash
python start_gemma.py
```

Por defecto, el servidor arranca en `http://127.0.0.1:8080/v1/chat/completions` (API compatible con OpenAI). `backend/llm_service.py` usa esa misma dirección para enviarle las peticiones de análisis.

## ⚙️ Configuración (opcional)

Si necesitas cambiar el puerto, el contexto o la distribución en GPU (por ejemplo, porque el 8080 ya está en uso o tu tarjeta tiene menos VRAM), copia `.env.example` a `.env` en esta misma carpeta y ajusta los valores. No contiene secretos — es configuración local de tu máquina. `start_gemma.py` y `backend/llm_service.py` leen el mismo fichero, así que solo hace falta cambiarlo aquí una vez.
