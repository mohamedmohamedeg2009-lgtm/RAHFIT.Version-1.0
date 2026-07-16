from typing import Any

from fastapi import FastAPI

from app.api.router import router

PREFIX = "/api/v1/intelligent-workouts"
EXPECTED_OPERATIONS = {
    ("post", f"{PREFIX}/plans/generate"): "intelligent_workouts_generate_plan",
    ("get", f"{PREFIX}/plans/active"): "intelligent_workouts_get_active_plan",
    ("get", f"{PREFIX}/plans"): "intelligent_workouts_list_plans",
    ("get", f"{PREFIX}/plans/{{plan_id}}"): "intelligent_workouts_get_plan",
    ("post", f"{PREFIX}/plans/{{plan_id}}/activate"): ("intelligent_workouts_activate_plan"),
    ("post", f"{PREFIX}/plans/{{plan_id}}/archive"): "intelligent_workouts_archive_plan",
    ("post", f"{PREFIX}/sessions"): "intelligent_workouts_create_session",
    ("get", f"{PREFIX}/sessions"): "intelligent_workouts_list_sessions",
    ("get", f"{PREFIX}/sessions/{{session_id}}"): "intelligent_workouts_get_session",
    ("patch", f"{PREFIX}/sessions/{{session_id}}"): "intelligent_workouts_update_session",
    ("post", f"{PREFIX}/adaptation/analyze"): "intelligent_workouts_analyze_adaptation",
}
PUBLIC_ROOT_SCHEMAS = {
    "WorkoutGenerationRequest",
    "WorkoutPlanResponse",
    "WorkoutPlanListResponse",
    "RecordWorkoutSessionRequest",
    "UpdateWorkoutSessionRequest",
    "WorkoutSessionResponse",
    "WorkoutSessionListResponse",
    "WorkoutAdaptationRequest",
    "WorkoutAdaptationResponse",
    "WorkoutArchiveResponse",
    "ErrorResponse",
}
FORBIDDEN_PUBLIC_FIELDS = {
    "_id",
    "user_id",
    "owner_id",
    "password_hash",
    "provider",
    "model",
    "prompt",
    "raw_context",
    "health_notes",
    "generation_metadata",
}


def _openapi() -> dict[str, Any]:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app.openapi()


def _reachable_fields(
    schema: dict[str, Any], components: dict[str, dict[str, Any]], seen: set[str]
) -> set[str]:
    reference = schema.get("$ref")
    if isinstance(reference, str):
        name = reference.rsplit("/", maxsplit=1)[-1]
        if name in seen:
            return set()
        seen.add(name)
        return _reachable_fields(components[name], components, seen)
    fields = set(schema.get("properties", {}))
    for value in schema.get("properties", {}).values():
        fields.update(_reachable_fields(value, components, seen))
    for key in ("items", "additionalProperties"):
        value = schema.get(key)
        if isinstance(value, dict):
            fields.update(_reachable_fields(value, components, seen))
    for key in ("anyOf", "allOf", "oneOf"):
        for value in schema.get(key, []):
            fields.update(_reachable_fields(value, components, seen))
    return fields


def test_openapi_contains_stable_intelligent_and_legacy_paths() -> None:
    contract = _openapi()
    paths = contract["paths"]
    for (method, path), operation_id in EXPECTED_OPERATIONS.items():
        assert path in paths
        assert method in paths[path]
        operation = paths[path][method]
        assert operation["operationId"] == operation_id
        assert operation["summary"]
        assert operation["description"]
    assert "/api/v1/workouts/current" in paths
    assert "/api/v1/workouts/generate" in paths


def test_operation_ids_are_unique_and_public_schemas_are_registered() -> None:
    contract = _openapi()
    operation_ids = [
        operation["operationId"]
        for path in contract["paths"].values()
        for method, operation in path.items()
        if method in {"get", "post", "put", "patch", "delete"}
    ]
    assert len(operation_ids) == len(set(operation_ids))
    schemas = contract["components"]["schemas"]
    assert PUBLIC_ROOT_SCHEMAS.issubset(schemas)
    assert "IntelligentWorkoutDay" in schemas
    assert "app__workouts__models__WorkoutDay" not in schemas
    assert "notes" not in schemas["HealthProfileUpdateRequest"]["properties"]


def test_every_intelligent_operation_declares_bearer_security_and_safe_errors() -> None:
    contract = _openapi()
    for method, path in EXPECTED_OPERATIONS:
        operation = contract["paths"][path][method]
        assert {"HTTPBearer": []} in operation["security"]
        assert "401" in operation["responses"]
        for code, response in operation["responses"].items():
            if int(code) >= 400:
                error_schema = response["content"]["application/json"]["schema"]
                assert error_schema["$ref"].endswith("/ErrorResponse")


def test_client_schemas_exclude_internal_ownership_provider_and_persistence_fields() -> None:
    components = _openapi()["components"]["schemas"]
    for name in PUBLIC_ROOT_SCHEMAS - {"ErrorResponse"}:
        fields = _reachable_fields(components[name], components, {name})
        assert fields.isdisjoint(FORBIDDEN_PUBLIC_FIELDS), (name, fields)


def test_dates_enums_pagination_and_nullable_fields_have_stable_json_shapes() -> None:
    schemas = _openapi()["components"]["schemas"]
    plan = schemas["WorkoutPlanResponse"]["properties"]
    session = schemas["WorkoutSessionResponse"]["properties"]
    pagination = schemas["WorkoutPlanListResponse"]["properties"]

    assert plan["generated_at"]["format"] == "date-time"
    assert session["started_at"]["format"] == "date-time"
    assert {item.get("type") for item in session["completed_at"]["anyOf"]} == {
        "string",
        "null",
    }
    assert set(pagination) == {"items", "limit", "offset", "has_more"}
    assert schemas["GenerationMode"]["enum"] == [
        "deterministic",
        "ai_assisted",
        "deterministic_fallback",
    ]
    assert schemas["SessionStatus"]["enum"] == ["in_progress", "completed", "abandoned"]
