from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ValidationResult:
    """
    Resultado de la validación de parámetros.
    """

    valid: bool
    errors: List[str] = field(default_factory=list)


class ParameterValidator:
    """
    Valida los parámetros antes de ejecutar una herramienta.
    """

    @staticmethod
    def validate(
        parameters: Dict[str, Any],
        schema: Dict[str, Any],
    ) -> ValidationResult:

        errors: List[str] = []

        if not isinstance(parameters, dict):
            return ValidationResult(
                valid=False,
                errors=["Los parámetros deben ser un diccionario."],
            )

        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # Verificar parámetros obligatorios
        for parameter in required:
            if parameter not in parameters:
                errors.append(
                    f"Falta el parámetro obligatorio: {parameter}"
                )

        # Verificar parámetros enviados
        for name, value in parameters.items():

            if name not in properties:
                errors.append(
                    f"Parámetro no permitido: {name}"
                )
                continue

            expected_type = properties[name].get("type")

            if not ParameterValidator._is_valid_type(
                value,
                expected_type,
            ):
                errors.append(
                    f"El parámetro '{name}' tiene un tipo inválido."
                )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
        )

    @staticmethod
    def _is_valid_type(
        value: Any,
        expected_type: str,
    ) -> bool:

        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list,
        }

        python_type = type_map.get(expected_type)

        if python_type is None:
            return True

        # Evita aceptar True/False como integer o number.
        if expected_type in ("integer", "number") and isinstance(value, bool):
            return False

        return isinstance(value, python_type)