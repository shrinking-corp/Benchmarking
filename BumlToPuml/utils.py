from typing import Any


def _type_name(value: Any) -> str:
    return value.name if hasattr(value, "name") else str(value)
