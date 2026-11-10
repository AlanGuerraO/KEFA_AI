
import unittest
import json

from prompts.initial_prompts import (
    get_system_prompt,
    get_intention_prompt,
    get_parameter_prompt,
    validate_response
)


class TestInitialPrompts(unittest.TestCase):

    def test_system_prompt(self):
        prompt = get_system_prompt()
        self.assertIn("KEFA IA", prompt)

    def test_intention_prompt(self):
        prompt = get_intention_prompt(
            "Crea una tarea para mañana"
        )
        self.assertIn("Crea una tarea", prompt)

    def test_parameter_prompt(self):
        prompt = get_parameter_prompt(
            "Agenda una reunión el lunes"
        )
        self.assertIn("lunes", prompt)

    def test_empty_message(self):
        with self.assertRaises(ValueError):
            get_intention_prompt("")

    def test_json_response(self):
        response = json.dumps({
            "intencion": "crear_tarea",
            "herramienta": None,
            "parametros": {"fecha": "mañana"},
            "estado": "completo",
            "mensaje": ""
        })

        result = validate_response(response)

        self.assertEqual(result["estado"], "completo")


if __name__ == "__main__":
    unittest.main()
