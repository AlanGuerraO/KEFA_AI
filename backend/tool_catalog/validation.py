"""Validación mínima y determinista de Tool Calling.

No se instala una dependencia externa de JSON Schema. El catálogo define un
subconjunto pequeño de reglas suficiente para el MVP y esta capa las aplica
antes de cualquier ejecución.
"""

from datetime import datetime

from .catalog import get_tool
from .errors import (
    ConfirmationRequiredError,
    PermissionDeniedError,
    UnknownToolError,
    ValidationError,
)
from .permissions import is_allowed


def _validate_property(name, value, schema):
    expected = schema.get("type")

    if expected == "string":
        if not isinstance(value, str):
            raise ValidationError(f"'{name}' debe ser texto.")
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise ValidationError(f"'{name}' no puede estar vacío.")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            raise ValidationError(f"'{name}' supera la longitud máxima permitida.")

    elif expected == "boolean":
        if not isinstance(value, bool):
            raise ValidationError(f"'{name}' debe ser booleano.")

    elif expected == "date-time":
        if not isinstance(value, str):
            raise ValidationError(f"'{name}' debe ser una fecha/hora en formato ISO 8601.")
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValidationError(
                f"'{name}' debe usar una fecha/hora ISO 8601 válida."
            ) from exc


def validate_tool_call(tool_name, parameters, granted_permissions=None,
                       confirmed=False):
    """Valida una propuesta de tool antes de permitir su ejecución.

    Retorna la definición validada de la tool. No ejecuta ninguna acción.
    """
    tool = get_tool(tool_name)
    if tool is None:
        raise UnknownToolError(f"La herramienta '{tool_name}' no existe en el catálogo.")

    if not isinstance(parameters, dict):
        raise ValidationError("Los parámetros deben ser un objeto/diccionario.")

    schema = tool["parameters"]
    required = set(schema.get("required", []))
    received = set(parameters)
    missing = required - received
    if missing:
        raise ValidationError(
            "Faltan parámetros requeridos: " + ", ".join(sorted(missing)) + "."
        )

    unknown = received - set(schema["properties"])
    if unknown:
        raise ValidationError(
            "Parámetros no permitidos: " + ", ".join(sorted(unknown)) + "."
        )

    for name, value in parameters.items():
        _validate_property(name, value, schema["properties"][name])

    if not is_allowed(tool, granted_permissions):
        raise PermissionDeniedError(
            f"El usuario no tiene los permisos necesarios para '{tool_name}'."
        )

    if tool["risk"]["requires_confirmation"] and not confirmed:
        raise ConfirmationRequiredError(
            f"La herramienta '{tool_name}' requiere confirmación explícita del usuario."
        )

    return tool
