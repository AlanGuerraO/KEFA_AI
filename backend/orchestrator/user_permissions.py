
"""KEFA-017: obtención segura de permisos del usuario."""

from django.contrib.auth.models import AnonymousUser


def get_user_permissions(user):
    """
    Obtiene permisos desde Django, nunca desde el cliente.

    Devuelve una lista de permisos autorizados.
    """

    if (
        user is None
        or isinstance(user, AnonymousUser)
        or not getattr(user, "is_authenticated", False)
        or not getattr(user, "is_active", False)
    ):
        return []

    return sorted(user.get_all_permissions())


# Correspondencia explícita entre permisos Django y KEFA.
# Los permisos Django deben estar registrados y asignados
# por un administrador del servidor.

KEFA_PERMISSION_MAP = {
    "users.kefa_calendar_read": "calendar:read",
    "users.kefa_calendar_write": "calendar:write",
    "users.kefa_tasks_read": "tasks:read",
    "users.kefa_tasks_write": "tasks:write",
    "users.kefa_notion_read": "notion:read",
    "users.kefa_notion_write": "notion:write",
}


def get_kefa_permissions(user):
    """
    Traduce permisos Django expresamente autorizados
    a los permisos que utiliza el catálogo KEFA.

    No acepta permisos enviados por el cliente.
    """
    django_permissions = set(get_user_permissions(user))

    return sorted({
        kefa_permission
        for django_permission, kefa_permission
        in KEFA_PERMISSION_MAP.items()
        if django_permission in django_permissions
    })

