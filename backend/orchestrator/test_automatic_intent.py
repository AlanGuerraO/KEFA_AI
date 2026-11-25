import unittest
from orchestrator.automatic_intent import allows_automatic_creation


class AutomaticIntentTests(unittest.TestCase):
    def test_explicit_task_creation(self):
        for prompt in (
            'Crea una tarea llamada Estudiar',
            'Recuérdame entregar la tarea mañana',
            'KEFA, apunta un pendiente de la universidad',
            '¿Puedes crear una tarea llamada Comprar pan?',
            'Quiero que me anotes una tarea',
        ):
            with self.subTest(prompt=prompt):
                self.assertTrue(allows_automatic_creation(prompt, 'tasks.create'))

    def test_calendar_creation(self):
        for prompt in ('Agenda un evento mañana a las 5', 'Programa una reunión con mi equipo',
                       'Kefa, crea una cita el viernes', 'Necesito que agendes mi evento'):
            with self.subTest(prompt=prompt):
                self.assertTrue(allows_automatic_creation(prompt, 'calendar.create_event'))

    def test_questions_and_descriptions_are_not_commands(self):
        for prompt in ('¿Cómo puedo organizar mis tareas?', 'Tengo una tarea pendiente',
                       'Mañana estudiaré de 3 a 4', '¿Qué pasa si creo un evento?',
                       'Ayúdame a entender el calendario'):
            for tool in ('tasks.create', 'calendar.create_event'):
                with self.subTest(prompt=prompt, tool=tool):
                    self.assertFalse(allows_automatic_creation(prompt, tool))

    def test_mismatched_and_unsupported_tools_are_denied(self):
        self.assertFalse(allows_automatic_creation('Crea una tarea', 'calendar.create_event'))
        self.assertFalse(allows_automatic_creation('Agenda un evento', 'tasks.create'))
        self.assertFalse(allows_automatic_creation('Crea una tarea y un evento', 'calendar.create_event'))
        self.assertFalse(allows_automatic_creation('Elimina mi tarea', 'tasks.delete'))
