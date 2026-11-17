
"""KEFA-017: pruebas de permisos sin base de datos."""


import os
import unittest
from unittest.mock import Mock

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django
django.setup()

from orchestrator.user_permissions import (
    get_user_permissions,
    get_kefa_permissions,
)


class TestUserPermissions(unittest.TestCase):

    def crear_usuario(self, permisos=None, activo=True):
        usuario = Mock()
        usuario.is_authenticated = True
        usuario.is_active = activo
        usuario.get_all_permissions.return_value = set(
            permisos or []
        )
        return usuario

    def test_usuario_sin_permisos(self):
        usuario = self.crear_usuario()

        resultado = get_kefa_permissions(usuario)

        self.assertEqual(resultado, [])

    def test_usuario_con_permiso_calendario(self):
        usuario = self.crear_usuario([
            "users.kefa_calendar_read",
        ])

        resultado = get_kefa_permissions(usuario)

        self.assertEqual(resultado, ["calendar:read"])

    def test_usuario_con_varios_permisos(self):
        usuario = self.crear_usuario([
            "users.kefa_calendar_read",
            "users.kefa_tasks_write",
            "users.kefa_notion_read",
        ])

        resultado = get_kefa_permissions(usuario)

        self.assertEqual(
            resultado,
            [
                "calendar:read",
                "notion:read",
                "tasks:write",
            ],
        )

    def test_permiso_desconocido_no_autoriza(self):
        usuario = self.crear_usuario([
            "users.permiso_inventado",
        ])

        resultado = get_kefa_permissions(usuario)

        self.assertEqual(resultado, [])

    def test_usuario_inactivo(self):
        usuario = self.crear_usuario(
            ["users.kefa_calendar_write"],
            activo=False,
        )

        resultado = get_kefa_permissions(usuario)

        self.assertEqual(resultado, [])
        usuario.get_all_permissions.assert_not_called()

    def test_usuario_no_autenticado(self):
        usuario = self.crear_usuario([
            "users.kefa_calendar_write",
        ])
        usuario.is_authenticated = False

        resultado = get_kefa_permissions(usuario)

        self.assertEqual(resultado, [])
        usuario.get_all_permissions.assert_not_called()

    def test_usuario_nulo(self):
        resultado = get_kefa_permissions(None)

        self.assertEqual(resultado, [])

    def test_no_modificar_permisos_originales(self):
        permisos = {
            "users.kefa_calendar_read",
            "users.kefa_tasks_write",
        }
        usuario = self.crear_usuario(permisos)

        get_kefa_permissions(usuario)

        self.assertEqual(
            usuario.get_all_permissions.return_value,
            permisos,
        )

    def test_obtener_permisos_django(self):
        usuario = self.crear_usuario([
            "users.kefa_calendar_read",
        ])

        resultado = get_user_permissions(usuario)

        self.assertEqual(
            resultado,
            ["users.kefa_calendar_read"],
        )


if __name__ == "__main__":
    unittest.main()
