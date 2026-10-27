
import re


class ParameterExtractor:
    """Extrae parámetros de instrucciones del usuario."""

    def __init__(self):
        self.required_parameters = {
            "enviar_correo": ["destinatario", "asunto", "mensaje"],
            "crear_evento": ["titulo", "fecha", "hora"],
            "crear_tarea": ["titulo"],
        }

    def extract(self, instruction, intention):
        if not isinstance(instruction, str) or not instruction.strip():
            raise ValueError("La instrucción no puede estar vacía")

        if not isinstance(intention, str) or not intention.strip():
            raise ValueError("La intención no puede estar vacía")

        parameters = {}

        if intention == "enviar_correo":
            email = re.search(
                r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}",
                instruction
            )
            if email:
                parameters["destinatario"] = email.group()

            subject = re.search(
                r"\basunto\s*:\s*(.+?)(?=\s+mensaje\s*:|$)",
                instruction,
                re.IGNORECASE
            )
            if subject:
                parameters["asunto"] = subject.group(1).strip()

            message = re.search(
                r"\bmensaje\s*:\s*(.+)$",
                instruction,
                re.IGNORECASE | re.DOTALL
            )
            if message:
                parameters["mensaje"] = message.group(1).strip()

        elif intention == "crear_evento":
            title = re.search(
                r"(?:evento|reunión)\s*:\s*(.+?)(?=\s+fecha\s*:|$)",
                instruction,
                re.IGNORECASE
            )
            if title:
                parameters["titulo"] = title.group(1).strip()

            date = re.search(
                r"\bfecha\s*:\s*(\d{4}-\d{2}-\d{2})",
                instruction,
                re.IGNORECASE
            )
            if date:
                parameters["fecha"] = date.group(1)

            time = re.search(
                r"\bhora\s*:\s*(\d{1,2}:\d{2})",
                instruction,
                re.IGNORECASE
            )
            if time:
                parameters["hora"] = time.group(1)

        elif intention == "crear_tarea":
            title = re.search(
                r"\btarea\s*:\s*(.+)$",
                instruction,
                re.IGNORECASE
            )
            if title:
                parameters["titulo"] = title.group(1).strip()

        required = self.required_parameters.get(intention, [])

        missing = [
            parameter
            for parameter in required
            if not parameters.get(parameter)
        ]

        return {
            "intencion": intention,
            "parametros": parameters,
            "faltantes": missing,
            "completo": len(missing) == 0 and bool(required),
        }
