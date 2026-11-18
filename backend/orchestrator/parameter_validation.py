"""Validación de parámetros antes de autorizar la ejecución de herramientas.

Mantiene la interfaz ParameterValidator.validate(parameters, schema) utilizada
por el orquestador. No ejecuta herramientas ni revisa permisos.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class ValidationResult:
    """Resultado de la validación de parámetros."""

    valid: bool
    errors: List[str] = field(default_factory=list)


class ParameterValidator:
    """Valida un subconjunto de JSON Schema usado en el catálogo de KEFA."""

    @staticmethod
    def validate(
        parameters: Dict[str, Any],
        schema: Dict[str, Any],
    ) -> ValidationResult:
        errors: List[str] = []

        if not isinstance(parameters, dict):
            return ValidationResult(False, ["Los parámetros deben ser un diccionario."])

        if not isinstance(schema, dict):
            return ValidationResult(False, ["El esquema de parámetros no es válido."])

        required = schema.get("required", [])
        properties = schema.get("properties", {})
        if not isinstance(required, (list, tuple)) or not isinstance(properties, dict):
            return ValidationResult(False, ["El esquema de parámetros no es válido."])

        for name in required:
            if not isinstance(name, str):
                return ValidationResult(False, ["El esquema de parámetros no es válido."])
            if name not in parameters:
                errors.append(f"Falta el parámetro obligatorio: {name}")

        allow_extra = schema.get("additionalProperties", False)
        for name, value in parameters.items():
            if name not in properties:
                if not allow_extra:
                    errors.append(f"Parámetro no permitido: {name}")
                continue

            definition = properties[name]
            if not isinstance(definition, dict):
                errors.append(f"Esquema inválido para el parámetro '{name}'.")
                continue

            expected = definition.get("type")
            if expected not in (None, "string", "integer", "number", "boolean", "object", "array", "date-time"):
                errors.append(f"Tipo de esquema no admitido para '{name}': {expected}")
                continue

            if not ParameterValidator._is_valid_type(value, expected):
                errors.append(f"El parámetro '{name}' tiene un tipo inválido.")
                continue

            if expected == "string":
                min_length = definition.get("minLength", 0)
                if name in required:
                    min_length = max(min_length, 1)
                if len(value.strip()) < min_length:
                    errors.append(f"El parámetro '{name}' no puede estar vacío o ser demasiado corto.")
                max_length = definition.get("maxLength")
                if max_length is not None and len(value) > max_length:
                    errors.append(f"El parámetro '{name}' supera la longitud máxima permitida.")

            if expected == "date-time":
                parsed = ParameterValidator._parse_datetime(value)
                if parsed is None:
                    errors.append(f"El parámetro '{name}' debe ser una fecha y hora ISO 8601 válida con zona horaria.")

        # Para eventos de calendario, el final debe ser posterior al inicio.
        if "start" in properties and "end" in properties:
            start = ParameterValidator._parse_datetime(parameters.get("start"))
            end = ParameterValidator._parse_datetime(parameters.get("end"))
            if start is not None and end is not None and end <= start:
                errors.append("La fecha y hora de finalización debe ser posterior al inicio.")

        return ValidationResult(valid=not errors, errors=errors)

    @staticmethod
    def _parse_datetime(value: Any):
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            result = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if result.tzinfo is None or result.utcoffset() is None:
                return None
            return result
        except (ValueError, TypeError, OverflowError):
            return None

    @staticmethod
    def _is_valid_type(value: Any, expected_type: str) -> bool:
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list,
            "date-time": str,
        }
        if expected_type is None:
            return True
        python_type = type_map.get(expected_type)
        if python_type is None:
            return False
        if expected_type in ("integer", "number") and isinstance(value, bool):
            return False
        return isinstance(value, python_type)
