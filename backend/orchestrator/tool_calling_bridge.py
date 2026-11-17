
"""KEFA-016: puente entre Tool Calling y el orquestador."""

from services.tool_calling_service import ToolCallingService
from orchestrator.decision_flow import (
    DecisionType,
    OrchestratorDecision,
)


class ToolCallingBridge:
    def __init__(self, tool_service=None):
        self.tool_service = (
            tool_service if tool_service is not None
            else ToolCallingService()
        )

    def procesar(self, mensaje, granted_permissions=None,
                 confirmed=False):
        resultados = self.tool_service.procesar(
            mensaje,
            granted_permissions=granted_permissions,
            confirmed=confirmed,
        )

        decisiones = []

        for resultado in resultados:
            if resultado["type"] == "text":
                continue

            if resultado["type"] == "tool_call":
                payload = resultado["payload"]

                decisiones.append({
                    "decision": OrchestratorDecision(
                        decision=DecisionType.EXECUTE,
                        tool_name=payload["tool"],
                        reason="Herramienta validada y preparada.",
                    ),
                    "payload": payload,
                    "status": "prepared",
                })

            elif resultado["type"] == "error":
                code = resultado.get("code")

                decision_type = (
                    DecisionType.REQUEST_CONFIRMATION
                    if code == "ConfirmationRequiredError"
                    else DecisionType.REJECT
                )

                decisiones.append({
                    "decision": OrchestratorDecision(
                        decision=decision_type,
                        tool_name=resultado.get("tool"),
                        reason=resultado.get(
                            "message", "Error de Tool Calling."
                        ),
                    ),
                    "status": "not_prepared",
                })

        return decisiones
