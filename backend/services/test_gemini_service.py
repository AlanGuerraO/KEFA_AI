import json
import os
import unittest
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from config.gemini_client import GeminiAPIError, GeminiClient
from services.gemini_service import GeminiService
from services.tool_calling_service import ToolCallingService, build_gemini_tools
from orchestrator.tool_calling_bridge import ToolCallingBridge
from orchestrator.decision_flow import DecisionType


class TestGeminiAPIClient(unittest.TestCase):
    def test_missing_key_is_clearly_reported(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "changeme-gemini-api-key"}):
            with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY"):
                GeminiClient()

    @patch("config.gemini_client.urlopen")
    def test_sends_api_key_in_header_and_declared_tools(self, opener):
        response = {"candidates": [{"content": {"parts": [{"text": "Hola"}]}}]}
        cm = Mock()
        cm.read.return_value = json.dumps(response).encode()
        opener.return_value.__enter__.return_value = cm
        api = GeminiClient(api_key="fake-key")
        result = api.generate_content(model="gemini-3.5-flash-lite", prompt="Hola", tools=[{"name": "say_hi"}])
        self.assertEqual(result, response)
        request = opener.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(request.get_header("X-goog-api-key"), "fake-key")
        self.assertNotIn("fake-key", request.full_url)
        self.assertEqual(body["tools"][0]["functionDeclarations"][0]["name"], "say_hi")
        self.assertEqual(body["toolConfig"]["functionCallingConfig"]["mode"], "AUTO")
        self.assertEqual(body["contents"][0]["parts"][0]["text"], "Hola")

    @patch("config.gemini_client.urlopen")
    def test_rate_limited_omits_secret(self, opener):
        opener.side_effect = HTTPError("safe-url", 429, "Limited", {}, BytesIO(b'secret response'))
        with self.assertRaises(GeminiAPIError) as ctx:
            GeminiClient(api_key="secret-key").generate_content(model="gemini-3.5-flash-lite", prompt="Hola")
        self.assertEqual(ctx.exception.http_status, 429)
        self.assertNotIn("secret", str(ctx.exception))

    def test_refuses_invalid_model(self):
        with self.assertRaises(ValueError):
            GeminiClient(api_key="fake").generate_content(model="../../evil", prompt="Hola")


class TestGeminiToolCalling(unittest.TestCase):
    def fake_service(self, response):
        client = Mock()
        client.generate_content.return_value = response
        return ToolCallingService(client=client, provider="gemini")

    def test_only_actual_mvp_tools_are_advertised(self):
        tools, mapping = build_gemini_tools()
        self.assertEqual(set(mapping.values()), {"tasks.create", "calendar.create_event"})
        self.assertEqual(tools[0]["parameters"]["type"], "OBJECT")
        self.assertEqual(mapping["tasks__create"], "tasks.create")

    def test_task_is_prepared_but_not_executed(self):
        svc = self.fake_service({"candidates": [{"content": {"parts": [{"functionCall": {
            "name": "tasks__create", "args": {"title": "Estudiar"}}}]}}]})
        result = svc.procesar("Crea una tarea", granted_permissions=["tasks:write"])
        self.assertEqual(result[0]["type"], "tool_call")
        self.assertEqual(result[0]["status"], "prepared")
        self.assertEqual(result[0]["payload"]["tool"], "tasks.create")

    def test_unknown_tool_is_rejected(self):
        svc = self.fake_service({"candidates": [{"content": {"parts": [{"functionCall": {
            "name": "shell_exec", "args": {}}}]}}]})
        self.assertEqual(svc.procesar("Haz lo que sea")[0]["code"], "unknown_tool")

    def test_no_permissions_is_rejected(self):
        svc = self.fake_service({"candidates": [{"content": {"parts": [{"functionCall": {
            "name": "tasks__create", "args": {"title": "Estudiar"}}}]}}]})
        self.assertEqual(svc.procesar("Crea tarea", granted_permissions=[])[0]["code"], "PermissionDeniedError")

    def test_text_response_reaches_bridge(self):
        svc = self.fake_service({"candidates": [{"content": {"parts": [{"text": "Necesito la hora de finalización."}]}}]})
        result = ToolCallingBridge(tool_service=svc).procesar("Agenda una reunión", granted_permissions=[])
        self.assertEqual(result[0]["decision"].decision, DecisionType.RESPOND)
        self.assertEqual(result[0]["status"], "response")
        self.assertIn("hora de finalización", result[0]["message"])

    def test_missing_candidates_is_safe(self):
        svc = self.fake_service({"candidates": []})
        self.assertEqual(svc.procesar("Hola")[0]["code"], "no_candidates")

    def test_invalid_arguments_are_rejected(self):
        svc = self.fake_service({"candidates": [{"content": {"parts": [{"functionCall": {
            "name": "tasks__create", "args": "BAD"}}]}}]})
        self.assertEqual(svc.procesar("Crea tarea")[0]["code"], "invalid_function_call")

    def test_provider_api_error_has_guidance(self):
        client = Mock()
        client.generate_content.side_effect = GeminiAPIError("Se alcanzó el límite de uso de Gemini.", 429)
        with self.assertRaises(GeminiAPIError) as context:
            ToolCallingService(client=client, provider="gemini").procesar("Hola")
        self.assertEqual(context.exception.http_status, 429)
        self.assertIn("límite", str(context.exception))

    def test_text_service(self):
        client = Mock()
        client.generate_content.return_value = {"candidates": [{"content": {"parts": [{"text": "Hola"}]}}]}
        self.assertEqual(GeminiService(client=client).enviar_mensaje("Saluda"), "Hola")


if __name__ == "__main__":
    unittest.main()
