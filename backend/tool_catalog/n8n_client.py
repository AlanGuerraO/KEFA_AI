

import base64
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class N8NClientError(Exception):
    """Error al comunicarse con n8n."""


def _parse_response_body(response_body):
    """Convierte JSON cuando sea posible y conserva el texto original."""
    if not response_body:
        return None

    try:
        return json.loads(response_body)
    except (json.JSONDecodeError, TypeError):
        return response_body


def execute_n8n_tool(prepared_call):
    """
    Envía a n8n una llamada previamente validada
    mediante prepare_tool_call().

    Una respuesta HTTP exitosa significa que n8n recibió
    la solicitud, no necesariamente que terminó la ejecución.
    """

    if not isinstance(prepared_call, dict):
        raise ValueError("La llamada preparada debe ser un diccionario")

    tool = prepared_call.get("tool")
    parameters = prepared_call.get("parameters")
    execution = prepared_call.get("execution")

    if (
        not isinstance(tool, str)
        or not isinstance(parameters, dict)
        or not isinstance(execution, dict)
        or execution.get("method") != "n8n"
    ):
        raise ValueError("La llamada preparada no es válida para n8n")

    webhook_url = os.environ["N8N_WEBHOOK_URL"]
    username = os.environ["N8N_BASIC_AUTH_USER"]
    password_file = os.environ["N8N_BASIC_AUTH_PASSWORD_FILE"]

    password = Path(password_file).read_text(
        encoding="utf-8"
    ).rstrip("\r\n")

    if not password:
        raise N8NClientError("La contraseña de n8n está vacía")

    credentials = base64.b64encode(
        f"{username}:{password}".encode("utf-8")
    ).decode("ascii")

    payload = json.dumps({
        "tool": tool,
        "parameters": parameters,
    }).encode("utf-8")

    request = Request(
        webhook_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {credentials}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=15) as response:
            response_body = response.read().decode("utf-8")
            parsed_response = _parse_response_body(response_body)

            return {
                "status": "accepted",
                "http_status": response.status,
                "response": parsed_response,
            }

    except HTTPError as error:
        raise N8NClientError(
            f"n8n respondió con HTTP {error.code}"
        ) from error

    except URLError as error:
        raise N8NClientError(
            "No fue posible conectar con n8n"
        ) from error
