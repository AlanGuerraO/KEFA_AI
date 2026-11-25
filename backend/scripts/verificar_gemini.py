"""Diagnóstico de Gemini sin imprimir claves. Desde /app: python scripts/verificar_gemini.py [--live]"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.gemini_client import GeminiClient, GeminiAPIError


def main():
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    key = os.getenv("GEMINI_API_KEY", "")
    configured = bool(key.strip()) and not key.lower().startswith(("changeme", "tu_clave", "your_"))
    print("Proveedor:", provider)
    print("Modelo Gemini:", model)
    print("GEMINI_API_KEY configurada:", configured)
    if provider != "gemini":
        print("Configura LLM_PROVIDER=gemini en el archivo .env")
        return 1
    if not configured:
        print("Crea una clave en https://aistudio.google.com/apikey y agrégala al .env")
        return 1
    if "--live" not in sys.argv:
        print("Configuración local lista. Para llamar realmente a la API agrega --live.")
        return 0
    try:
        response = GeminiClient().generate_content(model=model, prompt="Responde solamente: Hola desde Gemini", max_output_tokens=40)
        for candidate in response.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if isinstance(part.get("text"), str):
                    print("Respuesta Gemini:", part["text"][:200])
                    return 0
        print("Gemini respondió sin texto. Revisa el estado del modelo y sus restricciones.")
        return 2
    except (GeminiAPIError, ValueError) as exc:
        print("Diagnóstico:", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
