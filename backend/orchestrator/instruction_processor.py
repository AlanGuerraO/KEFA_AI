
import json

from prompts.initial_prompts import (
    get_system_prompt,
    get_intention_prompt,
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
    "intencion": "intención identificada",
    "herramienta": null,
    "parametros": {},
    "informacion_faltante": [],
    "requiere_confirmacion": false,
    "estado": "analizado"
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
            resultado = json.loads(respuesta)
        except (json.JSONDecodeError, TypeError) as error:
            raise ValueError(
                "Claude no devolvió un JSON válido"
            ) from error

        if not isinstance(resultado, dict):
            raise ValueError("La respuesta debe ser un objeto JSON")

        campos = {
            "intencion": str,
            "parametros": dict,
            "informacion_faltante": list,
            "requiere_confirmacion": bool,
            "estado": str,
        }

        for campo, tipo in campos.items():
            if campo not in resultado or not isinstance(
                resultado[campo], tipo
            ):
                raise ValueError(
                    f"Campo inválido o faltante: {campo}"
                )

        if not isinstance(
            resultado.get("herramienta"), (str, type(None))
        ):
            raise ValueError("Campo inválido: herramienta")

        return resultado
