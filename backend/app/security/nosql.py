from collections.abc import Mapping
from typing import Any

from fastapi import HTTPException, status


def reject_mongo_operators(value: Any) -> Any:
    """Reject user-controlled MongoDB operators and dotted field paths recursively."""
    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            if str(key).startswith("$") or "." in str(key):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid input key."
                )
            reject_mongo_operators(nested_value)
    elif isinstance(value, list):
        for item in value:
            reject_mongo_operators(item)
    return value
