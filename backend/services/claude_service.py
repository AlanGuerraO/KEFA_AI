
from config.claude_client import get_claude_client


class ClaudeService:

    def __init__(self, client=None):
        self.client = client

    def enviar_mensaje(self, mensaje):
        if not mensaje or not mensaje.strip():
            raise ValueError("El mensaje no puede estar vacío")

        if self.client is None:
            self.client = get_claude_client()

        respuesta = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": mensaje
                }
            ]
        )

        return respuesta.content[0].text
