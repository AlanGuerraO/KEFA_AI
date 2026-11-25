"""Servicio de texto para el analizador de intenciones de KEFA IA."""

import os

from config.gemini_client import GeminiClient, GeminiAPIError


class GeminiService:
    def __init__(self, client=None, model=None):
        self.client = client
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    def enviar_mensaje(self, mensaje):
        if not isinstance(mensaje, str) or not mensaje.strip():
            raise ValueError("El mensaje no puede estar vacío.")
        if self.client is None:
            self.client = GeminiClient()
        data = self.client.generate_content(model=self.model, prompt=mensaje, max_output_tokens=1024)
        parts = (data.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
        text = "\n".join(part["text"] for part in parts if isinstance(part, dict) and isinstance(part.get("text"), str))
        if not text.strip():
            raise GeminiAPIError("Gemini no devolvió texto válido.")
        return text
