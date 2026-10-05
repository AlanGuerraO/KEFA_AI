from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ToolValidationResult:
    """
    Resultado de la validación de una herramienta.
    """

    valid: bool
    tool_name: Optional[str] = None
    tool: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ToolValidator:
    """
    Valida que una herramienta exista y pueda ser utilizada
    por el orquestador.
    """

    @staticmethod
    def validate(
        tool_name: str,
        catalog: Dict[str, Dict[str, Any]],
    ) -> ToolValidationResult:

        # Validar nombre
        if not tool_name or not isinstance(tool_name, str):
            return ToolValidationResult(
                valid=False,
                error="El nombre de la herramienta es obligatorio.",
            )

        # Buscar herramienta en el catálogo
        tool = catalog.get(tool_name)

        if tool is None:
            return ToolValidationResult(
                valid=False,
                tool_name=tool_name,
                error=f"La herramienta '{tool_name}' no existe.",
            )

        # Validar estado de la herramienta
        status = tool.get("status", "cataloged")

        if status not in ("cataloged", "active"):
            return ToolValidationResult(
                valid=False,
                tool_name=tool_name,
                tool=tool,
                error=f"La herramienta '{tool_name}' no está disponible.",
            )

        # Validar que tenga definición de parámetros
        if "parameters" not in tool:
            return ToolValidationResult(
                valid=False,
                tool_name=tool_name,
                tool=tool,
                error="La herramienta no tiene parámetros definidos.",
            )

        return ToolValidationResult(
            valid=True,
            tool_name=tool_name,
            tool=tool,
        )