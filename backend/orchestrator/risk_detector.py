
"""KEFA-017: detección de riesgo y confirmación de herramientas."""

from dataclasses import dataclass

from tool_catalog.catalog import get_tool


@dataclass(frozen=True)
class RiskAssessment:
    tool_name: str
    risk_level: str
    requires_confirmation: bool


def assess_tool_risk(tool_name: str) -> RiskAssessment:
    """Consulta el catálogo autorizado para evaluar una herramienta."""

    tool = get_tool(tool_name)

    if tool is None:
        raise ValueError(
            f"La herramienta '{tool_name}' no está autorizada."
        )

    risk = tool["risk"]

    return RiskAssessment(
        tool_name=tool["name"],
        risk_level=risk["level"],
        requires_confirmation=risk["requires_confirmation"],
    )
