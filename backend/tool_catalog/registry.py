"""Punto de entrada para integrar el catálogo con el futuro orquestador."""

from .errors import ToolExecutionError
from .validation import validate_tool_call


def prepare_tool_call(tool_name, parameters, granted_permissions=None,
                      confirmed=False):
    """Valida una propuesta y devuelve el payload seguro para n8n.

    Esta función deliberadamente no llama a n8n. La integración real se
    agregará cuando existan los workflows y credenciales correspondientes.
    """
    tool = validate_tool_call(
        tool_name,
        parameters,
        granted_permissions=granted_permissions,
        confirmed=confirmed,
    )

    try:
        return {
            "tool": tool["name"],
            "parameters": parameters,
            "execution": tool["execution"],
        }
    except (TypeError, KeyError) as exc:
        raise ToolExecutionError("No fue posible preparar la ejecución.") from exc
