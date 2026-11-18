"""KEFA-183: sin red; pruebas con clientes simulados."""
import os
import unittest
from unittest.mock import patch

from orchestrator.n8n_dispatch import (
    DispatchDisabledError, DispatchRejectedError, dispatch_prepared_call,
)


class N8NDispatchTests(unittest.TestCase):
    def setUp(self):
        self.call = {"tool": "tasks.create", "parameters": {"title": "Comprar materiales"},
                     "execution": {"method": "n8n"}}
        self.flag = patch.dict(os.environ, {"KEFA_N8N_EXECUTION_ENABLED": "true"})
        self.flag.start()
        self.addCleanup(self.flag.stop)

    @patch("orchestrator.n8n_dispatch.execute_n8n_tool")
    def test_accepts_valid_tool_with_permissions(self, sender):
        sender.return_value = {"status": "accepted", "http_status": 200}
        self.assertEqual(dispatch_prepared_call(self.call, granted_permissions=["tasks:write"]),
                         {"status": "accepted", "http_status": 200})
        sender.assert_called_once()

    @patch("orchestrator.n8n_dispatch.execute_n8n_tool")
    def test_rejects_missing_permissions(self, sender):
        with self.assertRaises(DispatchRejectedError):
            dispatch_prepared_call(self.call, granted_permissions=[])
        sender.assert_not_called()

    @patch("orchestrator.n8n_dispatch.execute_n8n_tool")
    def test_rejects_invalid_parameters(self, sender):
        self.call["parameters"] = {"title": "   "}
        with self.assertRaises(DispatchRejectedError):
            dispatch_prepared_call(self.call, granted_permissions=["tasks:write"])
        sender.assert_not_called()

    @patch("orchestrator.n8n_dispatch.execute_n8n_tool")
    def test_rejects_sensitive_tool_even_with_permission(self, sender):
        self.call = {"tool": "tasks.delete", "parameters": {"task_id": "123"}}
        with self.assertRaises(DispatchRejectedError):
            dispatch_prepared_call(self.call, granted_permissions=["tasks:write"])
        sender.assert_not_called()

    @patch("orchestrator.n8n_dispatch.execute_n8n_tool")
    def test_rejects_unknown_tool(self, sender):
        with self.assertRaises(DispatchRejectedError):
            dispatch_prepared_call({"tool": "shell.run", "parameters": {}},
                                   granted_permissions=["tasks:write"])
        sender.assert_not_called()

    @patch("orchestrator.n8n_dispatch.execute_n8n_tool")
    def test_rebuilds_execution_metadata_from_catalog(self, sender):
        sender.return_value = {"status": "accepted", "http_status": 202}
        self.call["execution"] = {"method": "shell", "command": "unsafe"}
        dispatch_prepared_call(self.call, granted_permissions=["tasks:write"])
        forwarded = sender.call_args.args[0]
        self.assertEqual(forwarded["execution"]["method"], "n8n")
        self.assertNotIn("command", forwarded["execution"])

    @patch("orchestrator.n8n_dispatch.execute_n8n_tool")
    def test_disabled_by_default_or_flag_false(self, sender):
        with patch.dict(os.environ, {"KEFA_N8N_EXECUTION_ENABLED": "false"}):
            with self.assertRaises(DispatchDisabledError):
                dispatch_prepared_call(self.call, granted_permissions=["tasks:write"])
        sender.assert_not_called()

    @patch("orchestrator.n8n_dispatch.execute_n8n_tool")
    def test_unconfirmed_response_is_not_success(self, sender):
        sender.return_value = {"status": "failed"}
        with self.assertRaises(DispatchRejectedError):
            dispatch_prepared_call(self.call, granted_permissions=["tasks:write"])


if __name__ == "__main__":
    unittest.main()
