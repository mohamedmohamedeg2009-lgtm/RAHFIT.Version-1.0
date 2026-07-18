from datetime import UTC, datetime
from typing import Any, cast

from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

from app.controllers.auth import get_current_user
from app.controllers.user_intelligence import (
    get_health_profile_service,
    get_user_profile_service,
    router,
)
from app.health import HealthProfile, HealthProfileData, HealthProfileService
from app.models.user import User
from app.profile import UserProfile, UserProfileData, UserProfileService

NOW = datetime(2026, 7, 17, 12, tzinfo=UTC)
OWNER = User(id="owner-1", email="owner@example.com", password_hash="hash")
OTHER = User(id="owner-2", email="other@example.com", password_hash="hash")


def profile_data() -> dict[str, Any]:
    return {
        "identity": {"full_name": "Test Owner", "age": 28, "gender": "male", "country": "EG"},
        "body": {"height_cm": 180.0, "weight_kg": 82.0, "body_fat_percentage": 18.0},
        "goals": {
            "primary_goal": "general_fitness",
            "secondary_goal": None,
            "target_weight_kg": None,
            "target_date": None,
        },
        "training": {
            "experience": "beginner",
            "available_days": 3,
            "session_duration_minutes": 45,
            "available_equipment": ["bodyweight", "dumbbell"],
            "workout_location": "home_gym",
        },
        "lifestyle": {
            "sleep_hours": 7.5,
            "stress_level": 4,
            "activity_level": "moderate",
            "daily_water_ml": 2500,
        },
        "nutrition": {
            "dietary_preferences": ["halal"],
            "allergies": [],
            "dietary_restrictions": [],
        },
    }


def health_data() -> dict[str, Any]:
    return {
        "injuries": [],
        "chronic_conditions": [],
        "pain_areas": [],
        "mobility_limitations": [],
        "surgery_history": [],
    }


class ProfileStore:
    def __init__(self, profiles: dict[str, UserProfile]) -> None:
        self.profiles = profiles

    async def get_by_user_id(self, user_id: str) -> UserProfile | None:
        return self.profiles.get(user_id)

    async def save(self, user_id: str, profile: UserProfileData) -> UserProfile:
        saved = UserProfile(
            id=f"profile-{user_id}",
            user_id=user_id,
            created_at=NOW,
            updated_at=NOW,
            **profile.model_dump(exclude={"bmi", "bmr_kcal", "age_group"}),
        )
        self.profiles[user_id] = saved
        return saved


class HealthStore:
    def __init__(self, profiles: dict[str, HealthProfile]) -> None:
        self.profiles = profiles

    async def get_by_user_id(self, user_id: str) -> HealthProfile | None:
        return self.profiles.get(user_id)

    async def save(self, user_id: str, profile: HealthProfileData) -> HealthProfile:
        saved = HealthProfile(
            id=f"health-{user_id}",
            user_id=user_id,
            created_at=NOW,
            updated_at=NOW,
            **profile.model_dump(exclude={"active_injury_areas", "requires_medical_clearance"}),
        )
        self.profiles[user_id] = saved
        return saved


def api_client(
    user: User,
    profile_store: ProfileStore,
    health_store: HealthStore,
) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_user_profile_service] = lambda: UserProfileService(profile_store)
    app.dependency_overrides[get_health_profile_service] = lambda: HealthProfileService(
        health_store
    )
    return TestClient(app)


def saved_profile(owner: str = OWNER.id) -> UserProfile:
    return UserProfile(
        id="private-profile-id",
        user_id=owner,
        schema_version=9,
        created_at=NOW,
        updated_at=NOW,
        **UserProfileData.model_validate(profile_data()).model_dump(
            exclude={"bmi", "bmr_kcal", "age_group"}
        ),
    )


def saved_health(owner: str = OWNER.id) -> HealthProfile:
    return HealthProfile(
        id="private-health-id",
        user_id=owner,
        schema_version=9,
        created_at=NOW,
        updated_at=NOW,
        notes="private clinician note",
        **health_data(),
    )


def test_profile_and_health_read_success_excludes_private_fields() -> None:
    client = api_client(
        OWNER,
        ProfileStore({OWNER.id: saved_profile()}),
        HealthStore({OWNER.id: saved_health()}),
    )

    profile = client.get("/api/v1/user-intelligence/profile")
    health = client.get("/api/v1/user-intelligence/health")

    assert profile.status_code == health.status_code == 200
    assert profile.json()["identity"]["full_name"] == "Test Owner"
    assert health.json() == health_data()
    serialized = f"{profile.text} {health.text}"
    for private_field in (
        "user_id",
        "owner_id",
        "private-profile-id",
        "private-health-id",
        "schema_version",
        "created_at",
        "updated_at",
        "private clinician note",
        "notes",
    ):
        assert private_field not in serialized


def test_missing_and_foreign_owned_data_share_the_same_not_found_contract() -> None:
    stores = (ProfileStore({OWNER.id: saved_profile()}), HealthStore({OWNER.id: saved_health()}))
    foreign = api_client(OTHER, *stores)
    empty = api_client(OTHER, ProfileStore({}), HealthStore({}))

    for path in ("/api/v1/user-intelligence/profile", "/api/v1/user-intelligence/health"):
        foreign_response = foreign.get(path)
        empty_response = empty.get(path)
        assert foreign_response.status_code == empty_response.status_code == 404
        assert foreign_response.json() == empty_response.json()


def test_read_endpoints_require_authentication() -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    def unauthenticated() -> None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    app.dependency_overrides[get_current_user] = unauthenticated
    client = TestClient(app)

    assert client.get("/api/v1/user-intelligence/profile").status_code == 401
    assert client.get("/api/v1/user-intelligence/health").status_code == 401


def test_existing_put_contracts_remain_unchanged() -> None:
    profiles = ProfileStore({})
    health = HealthStore({})
    client = api_client(OWNER, profiles, health)

    assert client.put("/api/v1/profile", json=profile_data()).status_code == 204
    assert client.put("/api/v1/health-profile", json=health_data()).status_code == 204
    assert OWNER.id in profiles.profiles
    assert OWNER.id in health.profiles


def test_openapi_exposes_stable_read_operation_ids_and_safe_schemas() -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    schema = app.openapi()
    paths = cast(dict[str, Any], schema["paths"])

    assert paths["/api/v1/user-intelligence/profile"]["get"]["operationId"] == (
        "user_intelligence_get_profile"
    )
    assert paths["/api/v1/user-intelligence/health"]["get"]["operationId"] == (
        "user_intelligence_get_health"
    )
    components = cast(dict[str, Any], schema["components"])["schemas"]
    assert "notes" not in components["HealthProfileReadResponse"]["properties"]
    assert "user_id" not in components["UserProfileReadResponse"]["properties"]
