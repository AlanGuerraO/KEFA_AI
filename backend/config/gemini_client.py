"""Cliente mínimo de la API REST oficial de Gemini GenerateContent.

No añade un SDK ni envía secretos a React. La ejecución de herramientas queda
EXCLUSIVAMENTE en el backend después de validar permisos y parámetros.
"""

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GeminiAPIError(Exception):
    """Error seguro del proveedor; no incluye clave ni cuerpos sensibles."""

    def __init__(self, message, http_status=None):
        super().__init__(message)
        self.http_status = http_status


class GeminiClient:
    ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/"

    def __init__(self, api_key=None, timeout=30):
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "")
        if not self.api_key or self.api_key.strip().lower().startswith(("changeme", "tu_clave", "your_")):
            raise ValueError(
                "GEMINI_API_KEY no está configurada. Crea una clave en Google AI Studio "
                "y configúrala en el .env de la raíz."
            )
        self.timeout = timeout

    def generate_content(self, *, model, prompt, tools=None, system_instruction=None, max_output_tokens=1024):
        if not isinstance(model, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", model):
            raise ValueError("Identificador de modelo Gemini inválido.")
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_output_tokens},
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        if tools:
            payload["tools"] = [{"functionDeclarations": tools}]
            payload["toolConfig"] = {"functionCallingConfig": {"mode": "AUTO"}}
        request = Request(
            self.ENDPOINT + model + ":generateContent",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = json.load(response)
        except HTTPError as exc:
            messages = {
                400: "Gemini rechazó la solicitud o el modelo no admite el esquema enviado.",
                401: "La clave de Gemini no es válida.",
                403: "Gemini no autorizó esta clave, proyecto o región.",
                404: "El modelo de Gemini configurado no está disponible.",
                429: "Se alcanzó el límite de uso de Gemini; revisa la cuota gratuita.",
            }
            raise GeminiAPIError(messages.get(exc.code, "Gemini devolvió un error de servicio."), exc.code) from None
        except (URLError, TimeoutError, OSError):
            raise GeminiAPIError("No se pudo conectar con Gemini.") from None
        except (ValueError, TypeError):
            raise GeminiAPIError("Gemini devolvió una respuesta JSON inválida.") from None
        if not isinstance(data, dict):
            raise GeminiAPIError("Gemini devolvió una respuesta inesperada.")
        return data
