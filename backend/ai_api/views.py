
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orchestrator.tool_calling_bridge import ToolCallingBridge


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def tool_calling(request):
    mensaje = request.data.get("mensaje")

    if not isinstance(mensaje, str) or not mensaje.strip():
        return Response(
            {"error": "El mensaje es obligatorio."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # No aceptar permisos ni confirmaciones enviados
    # directamente por el cliente.
    bridge = ToolCallingBridge()

    try:
        decisiones = bridge.procesar(
            mensaje,
            granted_permissions=[],
            confirmed=False,
        )
    except Exception:
        return Response(
            {"error": "No se pudo procesar la instrucción."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    resultados = []

    for item in decisiones:
        decision = item["decision"]

        resultados.append({
            "decision": decision.decision.value,
            "tool": decision.tool_name,
            "reason": decision.reason,
            "status": item["status"],
        })

    return Response({"resultados": resultados})
