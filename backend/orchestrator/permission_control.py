from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PermissionResult:
    """
    Resultado de la validación de permisos.
    """

    allowed: bool
    missing_permission: Optional[str] = None
    error: Optional[str] = None


class PermissionController:
    """
    Controla si un usuario tiene los permisos necesarios
    para ejecutar una herramienta.
    """

    @staticmethod
    def check(
        user_permissions: List[str],
        required_permissions: List[str],
    ) -> PermissionResult:

        if not isinstance(user_permissions, list):
            return PermissionResult(
                allowed=False,
                error="Los permisos del usuario deben ser una lista.",
            )

        if not isinstance(required_permissions, list):
            return PermissionResult(
                allowed=False,
                error="Los permisos requeridos deben ser una lista.",
            )

        # Si la herramienta no requiere permisos especiales
        if not required_permissions:
            return PermissionResult(
                allowed=True,
            )

        # Comprobar cada permiso requerido
        for permission in required_permissions:
            if permission not in user_permissions:
                return PermissionResult(
                    allowed=False,
                    missing_permission=permission,
                    error=f"Falta el permiso requerido: {permission}",
                )

        return PermissionResult(
            allowed=True,
        )