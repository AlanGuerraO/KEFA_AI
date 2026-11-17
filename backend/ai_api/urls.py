
from django.urls import path
from .views import tool_calling, confirmar_accion

urlpatterns = [
    path(
        "tool-calling/",
        tool_calling,
        name="tool-calling",
    ),
    path(
        "confirmar-accion/",
        confirmar_accion,
        name="confirmar-accion",
    ),
]
