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

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from openai import OpenAI
from anthropic import Anthropic
import httpx

# gemma4/ es un módulo autónomo con su propio .env (host/puerto de llama-server).
# Se carga explícitamente por ruta absoluta (relativa a este fichero, no al cwd)
# para que host/puerto de Gemma se resuelvan igual desde main.py (cwd=backend/)
# y desde agent-plugin/mcp_server.py (puede lanzarse desde cualquier cwd).
_GEMMA_ENV_PATH = Path(__file__).resolve().parent.parent / "gemma4" / ".env"
load_dotenv(_GEMMA_ENV_PATH)

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
    "mindmap": (
        "Crea un esquema jerárquico o mapa mental estructurado en viñetas multinivel usando "
        "Markdown, que capture la estructura lógica de los temas discutidos en la "
        "transcripción:\n\n"
    ),
    "speaker_profiling": (
        "Analiza esta transcripción e intenta deducir el rol, profesión o perfil psicológico de cada locutor "
        "(ej. Entrevistador/Candidato, Médico/Paciente, Profesor/Alumno) basándote en lo que dicen y cómo lo dicen. "
        "Dame un resumen de la personalidad o postura de cada uno en formato Markdown:\n\n"
    ),
    "speaker_contributions": (
        "Extrae las ideas principales o conclusiones que ha aportado CADA locutor por separado a lo largo de la "
        "transcripción. Estructúralo con viñetas agrupadas bajo el nombre de cada Speaker en formato Markdown:\n\n"
    ),
    "speaker_actions": (
        "Analiza el texto y crea una lista de 'Siguientes Pasos' o tareas pendientes. Especifica claramente "
        "qué tarea se ha acordado y QUÉ LOCUTOR (Speaker) se ha comprometido a hacerla. Usa Markdown con checkboxes:\n\n"
    ),
    "speaker_interview": (
        "Convierte esta transcripción en bruto en un artículo formato entrevista para una revista o un acta formal. "
        "Elimina las muletillas, mejora la cohesión y sustituye las etiquetas genéricas de SPEAKER por nombres "
        "lógicos si puedes deducirlos (ej. 'Entrevistador:' y 'Entrevistado:'). Usa formato Markdown:\n\n"
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


def _resolve_system_instruction(transformation: str, custom_prompt: str) -> str:
    """Devuelve la instrucción de sistema para (transformation, custom_prompt).

    Compartida por los proveedores basados en chat (Gemini, OpenAI, Claude),
    que usan la misma redacción robusta para el modo "custom".
    """
    if transformation == "custom" and custom_prompt:
        return (
            "Eres un asistente experto en procesamiento de texto. "
            "Sigue EXCLUSIVAMENTE las siguientes instrucciones del usuario:\n\n"
            f"--- INSTRUCCIONES DEL USUARIO ---\n{custom_prompt}\n"
            "--- FIN DE INSTRUCCIONES ---\n\n"
            "Aplica estas instrucciones al siguiente texto:\n"
        )
    return build_prompt(transformation)


def analyze_with_gemini(text: str, model: str, api_key: str, transformation: str, custom_prompt: str = "") -> str:
    """Llama a la API de Gemini y devuelve el texto generado.
    """
    client = genai.Client(api_key=api_key)
    system_instruction = _resolve_system_instruction(transformation, custom_prompt)
    prompt = f"{system_instruction}\n\n--- TEXTO A PROCESAR ---\n{text}"

    response = client.models.generate_content(model=model, contents=prompt)
    return response.text


def analyze_with_openai(text: str, model: str, api_key: str, transformation: str, custom_prompt: str = "") -> str:
    """Llama a la API de OpenAI (Chat Completions) y devuelve el texto generado.
    """
    system_instruction = _resolve_system_instruction(transformation, custom_prompt)

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content


def analyze_with_claude(text: str, model: str, api_key: str, transformation: str, custom_prompt: str = "") -> str:
    """Llama a la API de Anthropic (Claude) y devuelve el texto generado.
    """
    system_instruction = _resolve_system_instruction(transformation, custom_prompt)

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        # A diferencia de Gemini/OpenAI, la API de Claude exige max_tokens.
        # 8192 evita truncar transformaciones largas (full_content, mindmap)
        # sobre transcripciones extensas; Gemini/OpenAI no tienen tope explícito.
        max_tokens=8192,
        system=system_instruction,
        messages=[{"role": "user", "content": text}],
    )
    return response.content[0].text




def _gemma_local_base_url() -> str:
    """Host:puerto de llama-server, leídos de gemma4/.env (LLAMA_HOST/LLAMA_PORT).

    Si gemma4/.env no existe o no define estas variables, usa los mismos
    valores por defecto que gemma4/start_gemma.py (127.0.0.1:8080).
    """
    host = os.getenv("LLAMA_HOST", "127.0.0.1")
    port = os.getenv("LLAMA_PORT", "8080")
    return f"http://{host}:{port}"


def analyze_with_gemma_local(text: str, model: str, transformation: str, custom_prompt: str = "") -> str:
    """Llama a un servidor local compatible con OpenAI (Llama.cpp, Ollama, etc).
    """
    system_instruction = _resolve_system_instruction(transformation, custom_prompt)

    base_url = _gemma_local_base_url()
    url = f"{base_url}/v1/chat/completions"
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
            f"No se pudo conectar con el servidor local de Gemma 4. "
            f"Asegúrate de que llama-server esté corriendo en {base_url}. "
            f"Sugerencia: Ejecuta 'start_gemma.cmd' en la raíz del proyecto."
        )
    except Exception as e:
        raise RuntimeError(f"Error en la comunicación con Gemma 4 Local: {str(e)}")
