
"""KEFA-016: puente entre Tool Calling y el orquestador."""

from services.tool_calling_service import ToolCallingService
from tool_catalog.n8n_client import execute_n8n_tool
from orchestrator.decision_flow import (
    DecisionType,
    OrchestratorDecision,
)
from orchestrator.confirmation_request import create_confirmation_request
from orchestrator.confirmation_store import confirmation_store


class ToolCallingBridge:
    def __init__(self, tool_service=None, n8n_executor=None):
        self.tool_service = (
            tool_service if tool_service is not None
            else ToolCallingService()
        )
        self.n8n_executor = (
            n8n_executor if n8n_executor is not None
            else execute_n8n_tool
        )

    def procesar(
        self,
        mensaje,
        granted_permissions=None,
        confirmed=False,
        user_id=None,
    ):
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

                # Solo se ejecutan llamadas que ya fueron preparadas
                # y validadas por ToolCallingService.
                ejecucion = self.n8n_executor(payload)

                decisiones.append({
                    "decision": OrchestratorDecision(
                        decision=DecisionType.EXECUTE,
                        tool_name=payload["tool"],
                        reason="Herramienta enviada a n8n.",
                    ),
                    "payload": payload,
                    "status": ejecucion.get("status", "accepted"),
                    "execution_result": ejecucion,
                })

            elif resultado["type"] == "error":
                code = resultado.get("code")
                tool_name = resultado.get("tool")
                parameters = resultado.get("parameters")

                if code == "ConfirmationRequiredError":
                    if not isinstance(user_id, str) or not user_id.strip():
                        raise ValueError(
                            "Se requiere un usuario autenticado para solicitar confirmación."
                        )
                    if not isinstance(tool_name, str) or not isinstance(parameters, dict):
                        raise ValueError(
                            "La solicitud de confirmación no contiene datos válidos."
                        )

                    solicitud = create_confirmation_request(
                        tool_name,
                        parameters,
                    )
                    confirmation_store.save(
                        solicitud,
                        user_id=user_id,
                    )

                decision_type = (
                    DecisionType.REQUEST_CONFIRMATION
                    if code == "ConfirmationRequiredError"
                    else DecisionType.REJECT
                )

                request_id = (
                    solicitud.request_id
                    if code == "ConfirmationRequiredError"
                    else None
                )

                decisiones.append({
                    "decision": OrchestratorDecision(
                        decision=decision_type,
                        tool_name=resultado.get("tool"),
                        reason=resultado.get(
                            "message",
                            "Error de Tool Calling.",
                        ),
                    ),
                    "status": "not_prepared",
                    "request_id": request_id,
                })

        return decisiones
