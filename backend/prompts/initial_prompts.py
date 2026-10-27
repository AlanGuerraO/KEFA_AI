
import json

# Prompt principal del sistema
SYSTEM_PROMPT = """
Eres KEFA IA, un asistente inteligente
que utiliza Claude de Anthropic.

Tus responsabilidades son:
1. Interpretar las solicitudes del usuario.
2. Identificar la intención principal.
3. Detectar los parámetros necesarios.
4. No inventar herramientas ni información.
5. Solicitar información cuando falten datos.
6. Respetar los permisos del usuario.
7. Solicitar confirmación cuando sea necesaria.
8. Responder de forma clara y precisa.

Debes responder únicamente en formato JSON.

Estructura de respuesta:
{
    "intencion": "nombre_de_la_intencion",
    "herramienta": null,
    "parametros": {},
    "estado": "completo",
    "mensaje": ""
}

Si faltan datos, utiliza estado "incompleto".
No ejecutes herramientas directamente.
"""

# Prompt para identificar intenciones
INTENTION_PROMPT = """
Analiza la siguiente solicitud:

{user_input}

Identifica:
- Intención del usuario.
- Herramienta solicitada.
- Parámetros necesarios.
- Información faltante.

No ejecutes ninguna herramienta.
Responde únicamente en formato JSON.
"""

# Prompt para extraer parámetros
PARAMETER_PROMPT = """
Analiza la siguiente instrucción:

{user_input}

Extrae los parámetros necesarios para realizar
la acción solicitada.

No inventes información faltante.

Si faltan parámetros, indica cuáles son.

Devuelve únicamente una respuesta JSON
con la estructura establecida.
"""


def get_system_prompt():
    return SYSTEM_PROMPT


def get_intention_prompt(user_input):
    if not isinstance(user_input, str) or not user_input.strip():
        raise ValueError("El mensaje no puede estar vacío")

    return INTENTION_PROMPT.format(
        user_input=user_input
    )


def get_parameter_prompt(user_input):
    if not isinstance(user_input, str) or not user_input.strip():
        raise ValueError("El mensaje no puede estar vacío")

    return PARAMETER_PROMPT.format(
        user_input=user_input
    )


def validate_response(response):
    data = json.loads(response)

    if not isinstance(data, dict):
        raise ValueError("La respuesta debe ser un objeto JSON")

    required_fields = [
        "intencion",
        "herramienta",
        "parametros",
        "estado",
        "mensaje"
    ]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Falta el campo: {field}")

    if not isinstance(data["parametros"], dict):
        raise ValueError("Los parámetros deben ser un objeto")

    if data["estado"] not in ["completo", "incompleto"]:
        raise ValueError("Estado no válido")

    return data
