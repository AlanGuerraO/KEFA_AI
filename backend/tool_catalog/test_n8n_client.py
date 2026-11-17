import unittest
from unittest.mock import patch, mock_open, MagicMock
from urllib.error import HTTPError

from tool_catalog.n8n_client import (
    execute_n8n_tool,
    N8NClientError,
)


class N8NClientTests(unittest.TestCase):

    def setUp(self):
        self.call = {
            "tool": "tasks.create",
            "parameters": {"title": "Prueba"},
            "execution": {"method": "n8n"},
        }

        self.environment = {
            "N8N_WEBHOOK_URL": "http://n8n:5678/webhook/test",
            "N8N_BASIC_AUTH_USER": "test_user",
            "N8N_BASIC_AUTH_PASSWORD_FILE": "/run/secrets/test",
        }

    def test_rejects_invalid_call(self):
        with self.assertRaises(ValueError):
            execute_n8n_tool({"tool": "tasks.create"})

    @patch("tool_catalog.n8n_client.urlopen")
    @patch(
        "pathlib.Path.read_text",
        return_value="test_password",
    )
    def test_successful_request(self, mock_secret, mock_urlopen):
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"message":"Workflow was started"}'
        mock_urlopen.return_value.__enter__.return_value = response

        with patch.dict("os.environ", self.environment):
            result = execute_n8n_tool(self.call)

        self.assertEqual(result["http_status"], 200)
        self.assertEqual(result["status"], "accepted")
        mock_urlopen.assert_called_once()

    @patch("tool_catalog.n8n_client.urlopen")
    @patch(
        "pathlib.Path.read_text",
        return_value="test_password",
    )
    def test_http_error(self, mock_secret, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            "http://n8n:5678",
            403,
            "Forbidden",
            None,
            None,
        )

        with patch.dict("os.environ", self.environment):
            with self.assertRaises(N8NClientError):
                execute_n8n_tool(self.call)


if __name__ == "__main__":
    unittest.main()