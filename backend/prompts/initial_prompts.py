
import json

# Prompt principal del sistema

SYSTEM_PROMPT = """
Eres KEFA IA, un asistente inteligente que utiliza el proveedor de IA configurado.

Tu responsabilidad es interpretar las instrucciones
del usuario y preparar acciones para el sistema.

HERRAMIENTAS PERMITIDAS DEL MVP:

1. tasks.create
   Crear una tarea.
   Parámetro obligatorio: title.
   Parámetros opcionales: notes, due.

2. calendar.create_event
   Crear un evento.
   Parámetros obligatorios: title, start, end.
   Parámetro opcional: description.

REGLAS:

- No inventes información.
- No propongas herramientas no permitidas.
- No ejecutes acciones directamente.
- Identifica los parámetros faltantes.
- Si falta información, solicítala.
- No afirmes que una acción fue ejecutada.
- Las fechas relativas requieren contexto temporal.
- La validación definitiva corresponde al backend.
- Responde únicamente con un objeto JSON válido.

FORMATO DE RESPUESTA:

{
    "intencion": "crear_tarea",
    "herramienta": "tasks.create",
    "parametros": {},
    "informacion_faltante": [],
    "requiere_confirmacion": false,
    "estado": "analizado",
    "mensaje": ""
}

INTENCIONES PERMITIDAS:
crear_tarea, crear_evento, no_soportada, desconocida.

ESTADOS PERMITIDOS:
analizado, incompleto, no_soportado.

Si la intención no está soportada,
utiliza herramienta null y estado no_soportado.

Si faltan datos obligatorios,
utiliza estado incompleto e indica
los campos en informacion_faltante.

No agregues texto fuera del JSON.
"""


# Prompt para identificar intenciones
INTENTION_PROMPT = """
Analiza la siguiente solicitud:

{user_input}

Identifica:
- Intención del usuario.
- Herramienta solicitada.
- Parámetros necesarios.
- Información faltante.

No ejecutes ninguna herramienta.
Responde únicamente en formato JSON.
"""

# Prompt para extraer parámetros
PARAMETER_PROMPT = """
Analiza la siguiente instrucción:

{user_input}

Extrae los parámetros necesarios para realizar
la acción solicitada.

No inventes información faltante.

Si faltan parámetros, indica cuáles son.

Devuelve únicamente una respuesta JSON
con la estructura establecida.
"""


def get_system_prompt():
    return SYSTEM_PROMPT


def get_intention_prompt(user_input):
    if not isinstance(user_input, str) or not user_input.strip():
        raise ValueError("El mensaje no puede estar vacío")

    return INTENTION_PROMPT.format(
        user_input=user_input
    )


def get_parameter_prompt(user_input):
    if not isinstance(user_input, str) or not user_input.strip():
        raise ValueError("El mensaje no puede estar vacío")

    return PARAMETER_PROMPT.format(
        user_input=user_input
    )


def validate_response(response):
    data = json.loads(response)

    if not isinstance(data, dict):
        raise ValueError("La respuesta debe ser un objeto JSON")


    required_fields = [
    "intencion",
    "herramienta",
    "parametros",
    "informacion_faltante",
    "requiere_confirmacion",
    "estado",
    "mensaje"
]





    for field in required_fields:
        if field not in data:
            raise ValueError(f"Falta el campo: {field}")

    if not isinstance(data["parametros"], dict):
        raise ValueError("Los parámetros deben ser un objeto")


    if data["estado"] not in [
    "analizado",
    "incompleto",
    "no_soportado"
]:

        raise ValueError("Estado no válido")


    if not isinstance(data["intencion"], str):
        raise ValueError("La intencion debe ser texto")

    if data["herramienta"] is not None and not isinstance(
        data["herramienta"], str
    ):
        raise ValueError("La herramienta debe ser texto o null")

    if not isinstance(data["informacion_faltante"], list):
        raise ValueError("La informacion faltante debe ser una lista")

    if not isinstance(data["requiere_confirmacion"], bool):
        raise ValueError("La confirmacion debe ser true o false")

    if not isinstance(data["mensaje"], str):
        raise ValueError("El mensaje debe ser texto")


    herramientas_permitidas = {
        "crear_tarea": "tasks.create",
        "crear_evento": "calendar.create_event"
    }

    intenciones_sin_herramienta = {
        "no_soportada",
        "desconocida"
    }

    intencion = data["intencion"]
    herramienta = data["herramienta"]
    estado = data["estado"]

    if intencion in herramientas_permitidas:
        if herramienta != herramientas_permitidas[intencion]:
            raise ValueError(
                "La herramienta no corresponde a la intencion"
            )

        if estado == "no_soportado":
            raise ValueError(
                "Estado incompatible con la intencion"
            )

    elif intencion in intenciones_sin_herramienta:
        if herramienta is not None:
            raise ValueError(
                "Esta intencion no permite herramientas"
            )

        if estado != "no_soportado":
            raise ValueError(
                "La intencion no soportada requiere estado no_soportado"
            )

    else:
        raise ValueError("Intencion no permitida")


    parametros_obligatorios = {
        "crear_tarea": ["title"],
        "crear_evento": ["title", "start", "end"]
    }

    if intencion in parametros_obligatorios:
        faltantes = [
            campo
            for campo in parametros_obligatorios[intencion]
            if not isinstance(data["parametros"].get(campo), str)
            or not data["parametros"][campo].strip()
        ]

        if faltantes:
            if estado != "incompleto":
                raise ValueError(
                    "Hay parametros faltantes y el estado no es incompleto"
                )

            if not set(faltantes).issubset(
                set(data["informacion_faltante"])
            ):
                raise ValueError(
                    "No se declararon todos los parametros faltantes"
                )

        elif estado == "incompleto":
            raise ValueError(
                "El estado es incompleto pero los parametros estan presentes"
            )


    return data