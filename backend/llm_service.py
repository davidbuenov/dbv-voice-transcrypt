# =============================================================================
# DBV VoiceTranscrypt — Aplicación web para la transcripción y análisis de audio de forma 100% local con Whisper y Gemma 4.
# Copyright (c) 2026 David Bueno Vallejo · https://github.com/davidbuenov
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops · https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

"""
Servicio de integración con LLMs (Large Language Models).

Responsabilidades:
  - Construir el prompt adecuado según el tipo de transformación solicitada.
  - Realizar la llamada al proveedor LLM (actualmente Gemini).
  - Retornar el texto generado o propagar excepciones al llamador.

Futuros proveedores (ej. Gemma 4 local) se añadirán aquí sin tocar main.py.
"""

from google import genai
import httpx

# Mapa de transformación → instrucción de sistema.
# Centralizado aquí para facilitar ajustes de prompts sin tocar la API.
PROMPT_TEMPLATES: dict[str, str] = {
    "summary": (
        "Genera un resumen ejecutivo profesional y conciso de la siguiente transcripción. "
        "Usa formato Markdown con un título y viñetas para los puntos principales:\n\n"
    ),
    "concepts": (
        "Extrae los conceptos clave, términos importantes o nombres propios de la siguiente "
        "transcripción, y ofrécelos como una lista tipo glosario en Markdown:\n\n"
    ),
    "actions": (
        "Revisa la siguiente transcripción e identifica todas las tareas, compromisos o "
        "'Action Items' mencionados. Formatéalos en una lista de Markdown con casillas de "
        "verificación (checkboxes):\n\n"
    ),
    "mindmap": (
        "Crea un esquema jerárquico o mapa mental estructurado en viñetas multinivel usando "
        "Markdown, que capture la estructura lógica de los temas discutidos en la "
        "transcripción:\n\n"
    ),
    "template": (
        "Transforma esta transcripción en un documento formal usando una 'Plantilla Inteligente'. "
        "Si parece una clase, formatea como apuntes; si es una reunión, como acta/minuta; "
        "si es una entrevista, como preguntas y respuestas. Usa Markdown enriquecido:\n\n"
    ),
    "full_content": (
        "Reescribe la siguiente transcripción para que sea fluida, gramaticalmente correcta y "
        "bien estructurada, pero SIN RESUMIR. Mantén toda la información original, detalles "
        "y matices. Organiza el texto en párrafos lógicos y usa subtítulos si es necesario para "
        "mejorar la legibilidad. El resultado debe ser un documento completo y profesional:\n\n"
    ),
    "qa": (
        "Analiza la siguiente transcripción e identifica todas las preguntas realizadas y las "
        "respuestas proporcionadas. Presenta la información en un formato de lista de Preguntas "
        "y Respuestas (Q&A) claro y fácil de leer en Markdown:\n\n"
    ),
    "followup": (
        "Basándote en la siguiente transcripción, redacta un email de seguimiento profesional. "
        "Debe incluir un saludo, un breve resumen de los temas tratados, una lista de los "
        "acuerdos o tareas pendientes (Action Items) y un cierre cordial. Usa Markdown:\n\n"
    ),
    "sentiment": (
        "Realiza un análisis de tono y sentimiento de la siguiente transcripción. Identifica "
        "la actitud predominante (constructiva, tensa, formal, etc.), los momentos clave de "
        "intercambio emocional y ofrece un breve resumen del clima de la sesión. Usa Markdown:\n\n"
    ),
}

FALLBACK_PROMPT = "Analiza y mejora el siguiente texto:\n\n"


def build_prompt(transformation: str) -> str:
    """Devuelve el prompt de sistema para el tipo de transformación dado.

    Si el tipo no está registrado, usa un prompt genérico de fallback
    en lugar de lanzar una excepción, para mayor resiliencia.
    """
    return PROMPT_TEMPLATES.get(transformation, FALLBACK_PROMPT)


def analyze_with_gemini(text: str, model: str, api_key: str, transformation: str, custom_prompt: str = "") -> str:
    """Llama a la API de Gemini y devuelve el texto generado.
    """
    client = genai.Client(api_key=api_key)
    
    # Construcción robusta del prompt
    if transformation == "custom" and custom_prompt:
        system_instruction = (
            "Eres un asistente experto en procesamiento de texto. "
            "Sigue EXCLUSIVAMENTE las siguientes instrucciones del usuario:\n\n"
            f"--- INSTRUCCIONES DEL USUARIO ---\n{custom_prompt}\n"
            "--- FIN DE INSTRUCCIONES ---\n\n"
            "Aplica estas instrucciones al siguiente texto:\n"
        )
    else:
        system_instruction = build_prompt(transformation)

    prompt = f"{system_instruction}\n\n--- TEXTO A PROCESAR ---\n{text}"

    response = client.models.generate_content(model=model, contents=prompt)
    return response.text




def analyze_with_gemma_local(text: str, model: str, transformation: str, custom_prompt: str = "") -> str:
    """Llama a un servidor local compatible con OpenAI (Llama.cpp, Ollama, etc).
    """
    if transformation == "custom" and custom_prompt:
        system_instruction = f"Instrucción específica: {custom_prompt}. Responde solo lo solicitado."
    else:
        system_instruction = build_prompt(transformation)
    
    url = "http://127.0.0.1:8080/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Procesa este texto según la instrucción de sistema:\n\n{text}"}
        ],
        "temperature": 0.3
    }


    
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except httpx.ConnectError:
        raise RuntimeError(
            "No se pudo conectar con el servidor local de Gemma 4. "
            "Asegúrate de que llama-server esté corriendo en http://127.0.0.1:8080. "
            "Sugerencia: Ejecuta 'start_gemma.cmd' en la raíz del proyecto."
        )
    except Exception as e:
        raise RuntimeError(f"Error en la comunicación con Gemma 4 Local: {str(e)}")
