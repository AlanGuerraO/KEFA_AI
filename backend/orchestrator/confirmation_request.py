
"""KEFA-017: generación de solicitudes de confirmación."""

from dataclasses import dataclass
from uuid import uuid4

from orchestrator.risk_detector import assess_tool_risk


@dataclass(frozen=True)
class ConfirmationRequest:
    request_id: str
    tool_name: str
    parameters: dict
    risk_level: str
    message: str
    status: str = "pending"


def create_confirmation_request(
    tool_name: str,
    parameters: dict,
) -> ConfirmationRequest:
    """Crea una solicitud sin ejecutar la herramienta."""

    if not isinstance(parameters, dict):
        raise ValueError("Los parámetros deben ser un diccionario.")

    assessment = assess_tool_risk(tool_name)

    if not assessment.requires_confirmation:
        raise ValueError(
            "Esta herramienta no requiere confirmación."
        )

    return ConfirmationRequest(
        request_id=str(uuid4()),
        tool_name=tool_name,
        parameters=parameters.copy(),
        risk_level=assessment.risk_level,
        message=(
            f"La herramienta '{tool_name}' realizará una acción "
            "sensible. ¿Deseas confirmar esta operación?"
        ),
    )
