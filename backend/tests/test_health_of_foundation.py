from app.core.exceptions import ErrorResponse
from app.security.nosql import reject_mongo_operators


def test_error_contract_serializes() -> None:
    assert ErrorResponse(code="test", message="message").code == "test"


def test_safe_nosql_input_passes() -> None:
    assert reject_mongo_operators({"profile": {"name": "Rahaf"}}) == {"profile": {"name": "Rahaf"}}
