
"""Validación de herramientas antes de preparar su ejecución.

Conserva los controles de existencia, permisos y confirmación del catálogo.
Delega la validación de parámetros a ParameterValidator (KEFA-139).
No ejecuta acciones externas.
"""

from orchestrator.parameter_validation import ParameterValidator

from .catalog import get_tool
from .errors import (
    ConfirmationRequiredError,
    PermissionDeniedError,
    UnknownToolError,
    ValidationError,
)
from .permissions import is_allowed


def validate_tool_call(tool_name, parameters, granted_permissions=None,
                       confirmed=False):
    """Valida herramienta, parámetros, permisos y confirmación.

    Devuelve la definición de la herramienta si todas las comprobaciones pasan.
    No ejecuta la herramienta ni autoriza por sí sola una llamada a n8n.
    """
    if not isinstance(tool_name, str) or not tool_name.strip():
        raise UnknownToolError("El nombre de la herramienta no es válido.")

    tool = get_tool(tool_name)
    if tool is None:
        raise UnknownToolError(
            f"La herramienta '{tool_name}' no existe en el catálogo."
        )

    schema = tool.get("parameters")
    resultado = ParameterValidator.validate(parameters, schema)
    if not resultado.valid:
        raise ValidationError("; ".join(resultado.errors))

    if not is_allowed(tool, granted_permissions):
        raise PermissionDeniedError(
            f"El usuario no tiene los permisos necesarios para '{tool_name}'."
        )

    if tool["risk"]["requires_confirmation"] and not confirmed:
        raise ConfirmationRequiredError(
            f"La herramienta '{tool_name}' requiere confirmación explícita del usuario."
        )

    return tool
