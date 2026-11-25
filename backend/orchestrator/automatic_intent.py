"""Segunda barrera para la creación automática de registros externos.

Gemini decide si conversar o proponer una herramienta. Esta comprobación
conservadora exige una orden de creación reconocible antes de invocar n8n.
No sustituye los permisos, validaciones y restricciones del catálogo.
"""
import re
import unicodedata

_CREATE = (
    r"(?:crea(?:me|r)?|crees|agrega(?:me|r)?|agregues|anota(?:me|r)?|anotes|apunta(?:me|r)?|apuntes|"
    r"registra(?:me|r)?|registres|agenda(?:me|r)?|agendes|programa(?:me|r)?|programes|"
    r"pon(?:me|er)?|recuerda(?:me|r)?|haz|anade(?:me|r)?|"
    r"crear|agendar|programar|registrar|recordar)"
)
_REQUEST = re.compile(
    r"^(?:(?:hola|oye|hey|kefa|por favor|favor de|buenas|asistente)[,\s]+)*"
    r"(?:(?:me\s+)?(?:puedes|podrias|podrias por favor|quiero|necesito|quisiera)\s+"
    r"(?:que\s+)?(?:me\s+)?)?"
    + _CREATE + r"\b",
    flags=re.IGNORECASE,
)
_QUESTION_ABOUT = re.compile(
    r"^(?:como|cuando|donde|por que|que|cuales?|explica|dime|ensename|ayudame a entender)\b",
    re.IGNORECASE,
)
_TASK = re.compile(r"\b(?:tarea(?:s)?|pendiente(?:s)?|recordatorio(?:s)?|google tasks)\b")
_CALENDAR = re.compile(r"\b(?:evento(?:s)?|cita(?:s)?|reunion(?:es)?|calendario|google calendar)\b")


def normalize_text(message):
    text = unicodedata.normalize("NFKD", message.casefold())
    return "".join(char for char in text if not unicodedata.combining(char)).strip(" \t\r\n¿?¡!")


def allows_automatic_creation(message, tool_name):
    """Exige intención explícita y evita invertir Tasks y Calendar.

    Frases descriptivas («tengo una tarea», «mañana estudio») o preguntas
    explicativas nunca deben producir efectos secundarios automáticamente.
    """
    if tool_name not in {"tasks.create", "calendar.create_event"}:
        return False
    if not isinstance(message, str):
        return False
    text = normalize_text(message)
    if _QUESTION_ABOUT.match(text) or not _REQUEST.match(text):
        return False
    task_hint = bool(_TASK.search(text))
    calendar_hint = bool(_CALENDAR.search(text))
    if task_hint and not calendar_hint and tool_name != "tasks.create":
        return False
    if calendar_hint and not task_hint and tool_name != "calendar.create_event":
        return False
    if task_hint and calendar_hint:
        return False  # Solicitud con dos destinos explícitos: pedir aclaración.
    return True
