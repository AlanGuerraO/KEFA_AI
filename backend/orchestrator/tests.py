import unittest

from orchestrator.action_log import ActionLogger
from orchestrator.confirmation import ConfirmationManager
from orchestrator.decision_flow import DecisionFlow, DecisionType
from orchestrator.error_handler import ErrorHandler
from orchestrator.input import OrchestratorInput
from orchestrator.output import OrchestratorOutput
from orchestrator.parameter_validation import ParameterValidator
from orchestrator.permission_control import PermissionController


class TestOrchestrator(unittest.TestCase):

    def test_input(self):
        data = OrchestratorInput(
            user_id="user-1",
            message="Crear una tarea",
            session_id="session-1",
            context={},
        )

        data.validate()

        result = data.to_dict()

        self.assertEqual(result["user_id"], "user-1")
        self.assertEqual(result["message"], "Crear una tarea")
        self.assertEqual(result["session_id"], "session-1")
        self.assertEqual(result["context"], {})

    def test_output_success(self):
        output = OrchestratorOutput.successful(
            message="Operación realizada correctamente.",
            action="create",
            tool="tasks.create",
            data={"id": 1},
        )

        result = output.to_dict()

        self.assertTrue(result["success"])
        self.assertEqual(
            result["message"],
            "Operación realizada correctamente.",
        )
        self.assertEqual(result["action"], "create")
        self.assertEqual(result["tool"], "tasks.create")
        self.assertEqual(result["data"], {"id": 1})

    def test_parameter_validation(self):
        schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                },
                "priority": {
                    "type": "integer",
                },
            },
            "required": ["title"],
        }

        parameters = {
            "title": "Terminar tarea",
            "priority": 1,
        }

        result = ParameterValidator.validate(
            parameters=parameters,
            schema=schema,
        )

        self.assertTrue(result.valid)
        self.assertEqual(result.errors, [])

    def test_permission_control(self):
        result = PermissionController.check(
            user_permissions=[
                "tasks.read",
                "tasks.write",
            ],
            required_permissions=[
                "tasks.write",
            ],
        )

        self.assertTrue(result.allowed)

    def test_confirmation_required(self):
        result = ConfirmationManager.check(
            requires_confirmation=True,
            confirmed=False,
            tool_name="tasks.delete",
        )

        self.assertFalse(result.allowed)
        self.assertTrue(result.requires_confirmation)

    def test_decision_flow_execute(self):
        flow = DecisionFlow()

        result = flow.decide(
            tool_name="tasks.create",
            tool_exists=True,
            parameters_valid=True,
            has_permission=True,
            requires_confirmation=False,
            confirmed=False,
        )

        self.assertEqual(
            result.decision,
            DecisionType.EXECUTE,
        )

    def test_error_handler(self):
        error = ErrorHandler.create(
            code="VALIDATION_ERROR",
            message="Parámetros inválidos",
        )

        result = ErrorHandler.to_dict(error)

        self.assertEqual(
            result["code"],
            "VALIDATION_ERROR",
        )

    def test_action_log(self):
        logger = ActionLogger()

        logger.log(
            user_id="user-1",
            action="create",
            tool_name="tasks.create",
            status="success",
        )

        records = logger.get_records()

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0]["status"],
            "success",
        )


if __name__ == "__main__":
    unittest.main()