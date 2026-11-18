"""Pruebas locales de validación de parámetros para KEFA-139."""

import unittest

from orchestrator.parameter_validation import ParameterValidator


TASK_SCHEMA = {
    "type": "object",
    "required": ["title"],
    "properties": {
        "title": {"type": "string", "minLength": 1},
        "notes": {"type": "string"},
        "due": {"type": "date-time"},
    },
    "additionalProperties": False,
}

EVENT_SCHEMA = {
    "type": "object",
    "required": ["title", "start", "end"],
    "properties": {
        "title": {"type": "string", "minLength": 1},
        "start": {"type": "date-time"},
        "end": {"type": "date-time"},
        "description": {"type": "string"},
    },
    "additionalProperties": False,
}


class TestParameterValidation(unittest.TestCase):
    def test_tarea_valida(self):
        result = ParameterValidator.validate({"title": "Comprar materiales"}, TASK_SCHEMA)
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(result.errors, [])

    def test_titulo_obligatorio_faltante(self):
        result = ParameterValidator.validate({}, TASK_SCHEMA)
        self.assertFalse(result.valid)
        self.assertTrue(any("title" in e for e in result.errors))

    def test_titulo_solo_espacios(self):
        result = ParameterValidator.validate({"title": "   "}, TASK_SCHEMA)
        self.assertFalse(result.valid)
        self.assertTrue(any("vacío" in e for e in result.errors))

    def test_tipo_incorrecto(self):
        result = ParameterValidator.validate({"title": 123}, TASK_SCHEMA)
        self.assertFalse(result.valid)
        self.assertTrue(any("tipo inválido" in e for e in result.errors))

    def test_parametro_desconocido(self):
        result = ParameterValidator.validate({"title": "Compra", "delete": True}, TASK_SCHEMA)
        self.assertFalse(result.valid)
        self.assertTrue(any("no permitido" in e for e in result.errors))

    def test_fecha_invalida(self):
        result = ParameterValidator.validate({"title": "Compra", "due": "mañana"}, TASK_SCHEMA)
        self.assertFalse(result.valid)
        self.assertTrue(any("ISO 8601" in e for e in result.errors))

    def test_fecha_sin_zona_horaria(self):
        result = ParameterValidator.validate({"title": "Compra", "due": "2026-11-20T12:00:00"}, TASK_SCHEMA)
        self.assertFalse(result.valid)

    def test_evento_valido(self):
        result = ParameterValidator.validate({
            "title": "Reunión KEFA",
            "start": "2026-11-20T10:00:00-06:00",
            "end": "2026-11-20T11:00:00-06:00",
        }, EVENT_SCHEMA)
        self.assertTrue(result.valid, result.errors)

    def test_evento_fin_antes_inicio(self):
        result = ParameterValidator.validate({
            "title": "Reunión KEFA",
            "start": "2026-11-20T11:00:00-06:00",
            "end": "2026-11-20T10:00:00-06:00",
        }, EVENT_SCHEMA)
        self.assertFalse(result.valid)
        self.assertTrue(any("posterior" in e for e in result.errors))

    def test_evento_inicio_igual_fin(self):
        result = ParameterValidator.validate({
            "title": "Reunión KEFA",
            "start": "2026-11-20T10:00:00-06:00",
            "end": "2026-11-20T10:00:00-06:00",
        }, EVENT_SCHEMA)
        self.assertFalse(result.valid)

    def test_esquema_invalido(self):
        result = ParameterValidator.validate({"title": "Compra"}, {"required": "title"})
        self.assertFalse(result.valid)

    def test_parametros_no_son_diccionario(self):
        result = ParameterValidator.validate(["Compra"], TASK_SCHEMA)
        self.assertFalse(result.valid)


if __name__ == "__main__":
    unittest.main()
