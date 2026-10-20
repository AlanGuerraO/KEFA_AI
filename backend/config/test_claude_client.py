
import os
import unittest
from unittest.mock import patch

from config.claude_client import get_claude_client


class TestClaudeClient(unittest.TestCase):

    def test_sin_api_key(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            with self.assertRaises(ValueError):
                get_claude_client()

    def test_con_api_key(self):
        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY": "clave-de-prueba"}
        ):
            cliente = get_claude_client()
            self.assertIsNotNone(cliente)


if __name__ == "__main__":
    unittest.main()
