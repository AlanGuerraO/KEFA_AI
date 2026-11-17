
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Meta:
        permissions = [
            ("kefa_calendar_read", "KEFA: consultar calendario"),
            ("kefa_calendar_write", "KEFA: modificar calendario"),
            ("kefa_tasks_read", "KEFA: consultar tareas"),
            ("kefa_tasks_write", "KEFA: modificar tareas"),
            ("kefa_notion_read", "KEFA: consultar Notion"),
            ("kefa_notion_write", "KEFA: modificar Notion"),
        ]
