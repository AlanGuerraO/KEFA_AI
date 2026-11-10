
import re
import unicodedata


class IntentionExtractor:
    """Identifica la intención principal de una instrucción."""

    INTENCIONES = {
        "enviar_correo": ["enviar correo", "mandar correo", "enviar email"],
        "crear_tarea": ["crear tarea", "agregar tarea", "registrar tarea"],
        "consultar_tareas": ["consultar tareas", "mostrar tareas", "ver tareas"],
        "crear_evento": ["crear evento", "agendar reunion", "programar reunion"],
        "buscar_informacion": ["buscar informacion", "investigar", "consultar informacion"],
    }

    def normalizar(self, texto):
        texto = unicodedata.normalize("NFD", texto.lower())
        texto = "".join(
            caracter for caracter in texto
            if unicodedata.category(caracter) != "Mn"
        )
        return re.sub(r"\s+", " ", texto).strip()

    def extraer(self, instruccion):
        if not isinstance(instruccion, str) or not instruccion.strip():
            return {
                "intencion": "desconocida",
                "confianza": 0.0,
                "instruccion": "",
                "requiere_aclaracion": True,
            }

        texto = self.normalizar(instruccion)

        for intencion, expresiones in self.INTENCIONES.items():
            for expresion in expresiones:
                patron = r"(?<!\w)" + re.escape(expresion) + r"(?!\w)"
                if re.search(patron, texto):
                    return {
                        "intencion": intencion,
                        "confianza": 1.0,
                        "instruccion": instruccion,
                        "requiere_aclaracion": False,
                    }

        return {
            "intencion": "desconocida",
            "confianza": 0.0,
            "instruccion": instruccion,
            "requiere_aclaracion": True,
        }
