
from prompts.initial_prompts import (
    get_system_prompt,
    get_intention_prompt,
    validate_response,
)
from services.claude_service import ClaudeService


class InstructionProcessor:

    def __init__(self, claude_service=None):
        self.claude_service = claude_service or ClaudeService()

    def procesar_instruccion(self, instruccion):
        if not isinstance(instruccion, str) or not instruccion.strip():
            raise ValueError("La instrucción no puede estar vacía")

        prompt = (
            get_system_prompt()
            + "\n\n"
            + get_intention_prompt(instruccion)
            + """

Devuelve únicamente un objeto JSON válido con esta estructura:

{
    "intencion": "crear_tarea",
    "herramienta": "tasks.create",
    "parametros": {},
    "informacion_faltante": ["title"],
    "requiere_confirmacion": false,
    "estado": "incompleto",
    "mensaje": "¿Qué título tendrá la tarea?"

}

Reglas:
- No ejecutes herramientas.
- No inventes información ni herramientas.
- Usa null si no se identifica una herramienta.
- Los parámetros deben ser un objeto JSON.
- La información faltante debe ser una lista.
- No incluyas texto fuera del JSON.
"""
        )

        respuesta = self.claude_service.enviar_mensaje(prompt)
        try:
            return validate_response(respuesta)
        except (ValueError, TypeError) as error:
            raise ValueError(
                f"Respuesta inválida de Claude: {error}"
            ) from error