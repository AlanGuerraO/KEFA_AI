from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DecisionType(str, Enum):
    """
    Posibles decisiones que puede tomar el orquestador.
    """

    EXECUTE = "execute"
    REQUEST_CONFIRMATION = "request_confirmation"
    REJECT = "reject"


@dataclass
class OrchestratorDecision:
    """
    Representa la decisión tomada por el orquestador.
    """

    decision: DecisionType
    tool_name: Optional[str] = None
    reason: Optional[str] = None


class DecisionFlow:
    """
    Define el flujo básico de decisiones del orquestador.
    """

    def decide(
        self,
        tool_name: Optional[str],
        tool_exists: bool,
        parameters_valid: bool,
        has_permission: bool,
        requires_confirmation: bool,
        confirmed: bool = False,
    ) -> OrchestratorDecision:

        if not tool_name or not tool_exists:
            return OrchestratorDecision(
                decision=DecisionType.REJECT,
                tool_name=tool_name,
                reason="La herramienta solicitada no existe.",
            )

        if not parameters_valid:
            return OrchestratorDecision(
                decision=DecisionType.REJECT,
                tool_name=tool_name,
                reason="Los parámetros de la herramienta no son válidos.",
            )

        if not has_permission:
            return OrchestratorDecision(
                decision=DecisionType.REJECT,
                tool_name=tool_name,
                reason="El usuario no tiene permisos para ejecutar esta herramienta.",
            )

        if requires_confirmation and not confirmed:
            return OrchestratorDecision(
                decision=DecisionType.REQUEST_CONFIRMATION,
                tool_name=tool_name,
                reason="La acción requiere confirmación del usuario.",
            )

        return OrchestratorDecision(
            decision=DecisionType.EXECUTE,
            tool_name=tool_name,
            reason="La herramienta puede ejecutarse.",
        )