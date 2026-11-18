
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orchestrator.tool_calling_bridge import ToolCallingBridge
from orchestrator.decision_flow import DecisionType
from orchestrator.n8n_dispatch import (
    is_dispatch_enabled, dispatch_prepared_call,
    DispatchRejectedError, DispatchDisabledError,
)
from tool_catalog.n8n_client import N8NClientError


from orchestrator.confirmation_store import confirmation_store

from orchestrator.user_permissions import get_kefa_permissions


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def tool_calling(request):
    mensaje = request.data.get("mensaje")

    if not isinstance(mensaje, str) or not mensaje.strip():
        return Response(
            {"error": "El mensaje es obligatorio."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    ejecutar = request.data.get("ejecutar", False)
    if not isinstance(ejecutar, bool):
        return Response(
            {"error": "ejecutar debe ser booleano."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if ejecutar and not is_dispatch_enabled():
        return Response(
            {"error": "La ejecución en n8n está deshabilitada en el servidor."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    bridge = ToolCallingBridge()
    granted_permissions = get_kefa_permissions(request.user)

    try:
        decisiones = bridge.procesar(
            mensaje,
            granted_permissions=granted_permissions,
            confirmed=False,
            user_id=str(request.user.pk),
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
            "request_id": item.get("request_id"),
        })

    if not ejecutar:
        return Response({"resultados": resultados})

    # Para evitar ejecuciones parciales, no enviar nada si Claude propuso
    # múltiples acciones, una confirmación o un error.
    if len(decisiones) != 1 or decisiones[0]["decision"].decision != DecisionType.EXECUTE:
        return Response(
            {"error": "Se requiere una única acción autorizada y sin confirmación pendiente.",
             "resultados": resultados},
            status=status.HTTP_409_CONFLICT,
        )

    propuesta = decisiones[0]
    if propuesta.get("status") != "prepared":
        return Response(
            {"error": "La herramienta no está preparada."},
            status=status.HTTP_409_CONFLICT,
        )

    try:
        entrega = dispatch_prepared_call(
            propuesta.get("payload"),
            granted_permissions=granted_permissions,
        )
    except DispatchDisabledError:
        return Response(
            {"error": "La ejecución en n8n está deshabilitada."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except DispatchRejectedError:
        return Response(
            {"error": "Acción rechazada por las validaciones del servidor."},
            status=status.HTTP_403_FORBIDDEN,
        )
    except (N8NClientError, OSError, KeyError, ValueError):
        # Puede existir incertidumbre sobre la recepción ante cortes de red.
        # No reintentar automáticamente para evitar operaciones duplicadas.
        return Response(
            {"error": "No se pudo confirmar la recepción por n8n. Verifica antes de reintentar."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    resultados[0]["status"] = entrega["status"]
    resultados[0]["http_status"] = entrega["http_status"]
    return Response({"resultados": resultados})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirmar_accion(request):
    request_id = request.data.get("request_id")
    respuesta = request.data.get("respuesta")

    if not isinstance(request_id, str) or not request_id.strip():
        return Response(
            {"error": "El request_id es obligatorio."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(respuesta, str):
        return Response(
            {"error": "La respuesta debe ser texto."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    respuesta = respuesta.strip().lower()
    request_id = request_id.strip()

    if respuesta not in ("confirmar", "rechazar", "cancelar"):
        return Response(
            {"error": "Respuesta de confirmación inválida."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user_id = str(request.user.pk)

    if respuesta in ("rechazar", "cancelar"):
        solicitud = confirmation_store.get(request_id)

        if solicitud is None:
            return Response(
                {"error": "Solicitud inválida o vencida."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        consumida = confirmation_store.consume(
            request_id,
            user_id,
            tool_name=solicitud.tool_name,
            parameters=solicitud.parameters,
        )

        if consumida is None:
            return Response(
                {"error": "Solicitud inválida o no autorizada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "status": "cancelled",
                "request_id": request_id,
            },
            status=status.HTTP_200_OK,
        )

    # La confirmación aún NO autoriza ninguna acción.
    # No consumir la solicitud ni ejecutar herramientas.
    return Response(
        {
            "error": (
                "La confirmación aún no está habilitada. "
                "Falta validar y preparar la operación "
                "original de forma segura."
            )
        },
        status=status.HTTP_501_NOT_IMPLEMENTED,
    )


