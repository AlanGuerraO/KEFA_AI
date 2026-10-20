
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

def get_claude_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError(
            "No se encontró ANTHROPIC_API_KEY. "
            "Configúrala en el archivo .env."
        )

    return Anthropic(api_key=api_key)


