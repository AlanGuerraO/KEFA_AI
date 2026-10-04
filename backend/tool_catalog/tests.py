from django.test import SimpleTestCase

from .catalog import get_tool, list_tools
from .errors import (
    ConfirmationRequiredError,
    PermissionDeniedError,
    UnknownToolError,
    ValidationError,
)
from .validation import validate_tool_call


class ToolCatalogTests(SimpleTestCase):
    def test_catalog_contains_initial_tools(self):
        tools = list_tools()
        self.assertEqual(len(tools), 11)
        self.assertIsNotNone(get_tool("calendar.create_event"))
        self.assertIsNotNone(get_tool("notion.search"))

    def test_valid_calendar_call(self):
        tool = validate_tool_call(
            "calendar.create_event",
            {
                "title": "Reunión",
                "start": "2026-10-05T17:00:00-06:00",
                "end": "2026-10-05T18:00:00-06:00",
            },
            granted_permissions=["calendar:write"],
        )
        self.assertEqual(tool["risk"]["level"], "medium")

    def test_rejects_unknown_tool(self):
        with self.assertRaises(UnknownToolError):
            validate_tool_call("system.execute_shell", {}, [])

    def test_rejects_missing_parameter(self):
        with self.assertRaises(ValidationError):
            validate_tool_call(
                "tasks.create", {}, ["tasks:write"]
            )

    def test_rejects_unknown_parameter(self):
        with self.assertRaises(ValidationError):
            validate_tool_call(
                "tasks.create",
                {"title": "Tarea", "shell": "rm -rf /"},
                ["tasks:write"],
            )

    def test_rejects_invalid_datetime(self):
        with self.assertRaises(ValidationError):
            validate_tool_call(
                "calendar.create_event",
                {
                    "title": "Reunión",
                    "start": "mañana",
                    "end": "2026-10-05T18:00:00-06:00",
                },
                ["calendar:write"],
            )

    def test_rejects_missing_permission(self):
        with self.assertRaises(PermissionDeniedError):
            validate_tool_call(
                "calendar.get_events",
                {
                    "start": "2026-10-05T00:00:00-06:00",
                    "end": "2026-10-06T00:00:00-06:00",
                },
                ["calendar:write"],
            )

    def test_sensitive_tool_requires_confirmation(self):
        with self.assertRaises(ConfirmationRequiredError):
            validate_tool_call(
                "calendar.delete_event",
                {"event_id": "event-123"},
                ["calendar:write"],
            )

    def test_sensitive_tool_can_be_confirmed(self):
        tool = validate_tool_call(
            "tasks.delete",
            {"task_id": "task-123"},
            ["tasks:write"],
            confirmed=True,
        )
        self.assertTrue(tool["risk"]["requires_confirmation"])
