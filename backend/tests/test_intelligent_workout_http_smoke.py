from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.router import router as application_router
from app.config import Settings, get_settings
from app.controllers.auth import get_auth_service
from app.controllers.intelligent_workout import get_intelligent_workout_service
from app.controllers.user_intelligence import (
    get_health_profile_service,
    get_user_profile_service,
)
from app.health import HealthProfile, HealthProfileData, HealthProfileService
from app.models.user import User
from app.profile import UserProfile, UserProfileData, UserProfileService
from app.readiness import ReadinessChecker
from app.services.auth import AuthService
from app.users.service import UserIntelligenceService
from app.workouts.exercises import ExerciseCatalog, ExerciseSelector
from app.workouts.generator import WorkoutGenerator
from app.workouts.models import WorkoutPlan, WorkoutSession, WorkoutStatus
from app.workouts.planner import WorkoutPlanner
from app.workouts.service import WorkoutService
from app.workouts.validator import WorkoutValidator


class InMemoryUserStore:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    async def create(self, email: str, password_hash: str) -> User:
        user = User(id=f"user-{len(self.users) + 1}", email=email, password_hash=password_hash)
        self.users[user.id] = user
        return user

    async def find_by_email(self, email: str) -> User | None:
        return next((item for item in self.users.values() if item.email == email), None)

    async def find_by_id(self, user_id: str) -> User | None:
        return self.users.get(user_id)

    async def find_by_provider(self, provider: str, provider_subject: str) -> User | None:
        return next(
            (
                user
                for user in self.users.values()
                if user.provider == provider and user.provider_subject == provider_subject
            ),
            None,
        )

    async def link_google_account(
        self, user_id: str, provider_subject: str, verified_email: str
    ) -> bool:
        user = self.users.get(user_id)
        if user is None:
            return False
        self.users[user_id] = user.model_copy(
            update={
                "provider": "google",
                "provider_subject": provider_subject,
                "verified_email": verified_email,
            }
        )
        return True

    async def create_google_user(
        self, email: str, display_name: str | None, provider_subject: str
    ) -> User:
        user = User(
            id=f"user-{len(self.users) + 1}",
            email=email,
            password_hash="",
            display_name=display_name,
            provider="google",
            provider_subject=provider_subject,
            verified_email=email,
        )
        self.users[user.id] = user
        return user

    async def increment_token_version(self, user_id: str, expected_version: int) -> User | None:
        user = self.users.get(user_id)
        if user is None or user.token_version != expected_version:
            return None
        updated = user.model_copy(update={"token_version": user.token_version + 1})
        self.users[user_id] = updated
        return updated


class InMemoryProfileStore:
    def __init__(self) -> None:
        self.profiles: dict[str, UserProfile] = {}

    async def get_by_user_id(self, user_id: str) -> UserProfile | None:
        return self.profiles.get(user_id)

    async def save(self, user_id: str, profile: UserProfileData) -> UserProfile:
        existing = self.profiles.get(user_id)
        now = datetime.now(UTC)
        saved = UserProfile(
            id=existing.id if existing else f"profile-{user_id}",
            user_id=user_id,
            created_at=existing.created_at if existing else now,
            updated_at=now,
            **profile.model_dump(exclude_computed_fields=True),
        )
        self.profiles[user_id] = saved
        return saved


class InMemoryHealthStore:
    def __init__(self) -> None:
        self.profiles: dict[str, HealthProfile] = {}

    async def get_by_user_id(self, user_id: str) -> HealthProfile | None:
        return self.profiles.get(user_id)

    async def save(self, user_id: str, profile: HealthProfileData) -> HealthProfile:
        existing = self.profiles.get(user_id)
        now = datetime.now(UTC)
        saved = HealthProfile(
            id=existing.id if existing else f"health-{user_id}",
            user_id=user_id,
            created_at=existing.created_at if existing else now,
            updated_at=now,
            **profile.model_dump(exclude_computed_fields=True),
        )
        self.profiles[user_id] = saved
        return saved


class InMemoryWorkoutStore:
    def __init__(self) -> None:
        self.plans: dict[str, WorkoutPlan] = {}
        self.sessions: dict[str, WorkoutSession] = {}

    async def create(self, plan: WorkoutPlan) -> WorkoutPlan:
        self.plans[plan.plan_id] = plan
        return plan

    async def replace_active_plan(self, plan: WorkoutPlan) -> WorkoutPlan:
        now = datetime.now(UTC)
        current = await self.get_active_plan(plan.user_id)
        if current is not None:
            self.plans[current.plan_id] = current.model_copy(
                update={"status": WorkoutStatus.ARCHIVED, "archived_at": now, "updated_at": now}
            )
        replacement = plan.model_copy(
            update={
                "version": current.version + 1 if current else 1,
                "status": WorkoutStatus.ACTIVE,
                "activated_at": now,
                "archived_at": None,
                "updated_at": now,
            }
        )
        self.plans[replacement.plan_id] = replacement
        return replacement

    async def get_active_plan(self, user_id: str) -> WorkoutPlan | None:
        return next(
            (
                item
                for item in self.plans.values()
                if item.user_id == user_id and item.status == WorkoutStatus.ACTIVE
            ),
            None,
        )

    async def get_by_id(self, user_id: str, plan_id: str) -> WorkoutPlan | None:
        plan = self.plans.get(plan_id)
        return plan if plan is not None and plan.user_id == user_id else None

    async def list_user_plans(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[WorkoutPlan, ...]:
        plans = sorted(
            (item for item in self.plans.values() if item.user_id == user_id),
            key=lambda item: (item.generated_at, item.plan_id),
            reverse=True,
        )
        return tuple(plans[offset : offset + limit])

    async def activate_plan(self, user_id: str, plan_id: str) -> WorkoutPlan | None:
        target = await self.get_by_id(user_id, plan_id)
        if target is None:
            return None
        now = datetime.now(UTC)
        current = await self.get_active_plan(user_id)
        if current is not None and current.plan_id != plan_id:
            self.plans[current.plan_id] = current.model_copy(
                update={"status": WorkoutStatus.ARCHIVED, "archived_at": now, "updated_at": now}
            )
        activated = target.model_copy(
            update={
                "status": WorkoutStatus.ACTIVE,
                "activated_at": now,
                "archived_at": None,
                "updated_at": now,
            }
        )
        self.plans[plan_id] = activated
        return activated

    async def archive_plan(self, user_id: str, plan_id: str) -> bool:
        target = await self.get_by_id(user_id, plan_id)
        if target is None or target.status != WorkoutStatus.ACTIVE:
            return False
        now = datetime.now(UTC)
        self.plans[plan_id] = target.model_copy(
            update={"status": WorkoutStatus.ARCHIVED, "archived_at": now, "updated_at": now}
        )
        return True

    async def get_version_history(
        self, user_id: str, generation_key: str
    ) -> tuple[WorkoutPlan, ...]:
        return tuple(
            item
            for item in self.plans.values()
            if item.user_id == user_id and item.generation_metadata.generation_key == generation_key
        )

    async def save_session(self, session: WorkoutSession) -> WorkoutSession:
        self.sessions[session.session_id] = session
        return session

    async def update_session(self, session: WorkoutSession) -> WorkoutSession | None:
        current = await self.get_session(session.user_id, session.session_id)
        if current is None:
            return None
        self.sessions[session.session_id] = session
        return session

    async def get_session(self, user_id: str, session_id: str) -> WorkoutSession | None:
        session = self.sessions.get(session_id)
        return session if session is not None and session.user_id == user_id else None

    async def list_sessions(
        self,
        user_id: str,
        plan_id: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[WorkoutSession, ...]:
        sessions = sorted(
            (
                item
                for item in self.sessions.values()
                if item.user_id == user_id and (plan_id is None or item.plan_id == plan_id)
            ),
            key=lambda item: (item.started_at, item.session_id),
            reverse=True,
        )
        return tuple(sessions[offset : offset + limit])


class SmokeEnvironment:
    def __init__(self) -> None:
        self.settings = Settings(
            _env_file=None,
            mongodb_uri="mongodb://localhost:27017",
            mongodb_database="rahfit_smoke",
            jwt_secret_key="smoke-test-secret-key-with-32-characters",
            ai_feature_enabled=False,
        )
        self.users = InMemoryUserStore()
        self.profiles = InMemoryProfileStore()
        self.health = InMemoryHealthStore()
        self.workouts = InMemoryWorkoutStore()
        intelligence = UserIntelligenceService(self.profiles, self.health)
        readiness = ReadinessChecker()
        generator = WorkoutGenerator(
            intelligence=intelligence,
            readiness=readiness,
            planner=WorkoutPlanner(),
            catalog=ExerciseCatalog(),
            selector=ExerciseSelector(),
            validator=WorkoutValidator(),
            id_factory=lambda: str(uuid4()),
        )
        self.workout_service = WorkoutService(
            self.workouts,
            generator,
            intelligence=intelligence,
            readiness=readiness,
            id_factory=lambda: str(uuid4()),
        )
        app = FastAPI()
        app.include_router(application_router, prefix="/api/v1")
        app.dependency_overrides[get_settings] = lambda: self.settings
        app.dependency_overrides[get_auth_service] = lambda: AuthService(self.users, self.settings)
        app.dependency_overrides[get_user_profile_service] = lambda: UserProfileService(
            self.profiles
        )
        app.dependency_overrides[get_health_profile_service] = lambda: HealthProfileService(
            self.health
        )
        app.dependency_overrides[get_intelligent_workout_service] = lambda: self.workout_service
        self.client = TestClient(app)


@pytest.fixture
def smoke() -> SmokeEnvironment:
    return SmokeEnvironment()


def _profile() -> dict[str, Any]:
    return {
        "identity": {"full_name": "Smoke User", "age": 30, "gender": "male", "country": "EG"},
        "body": {"height_cm": 180.0, "weight_kg": 80.0, "body_fat_percentage": 18.0},
        "goals": {"primary_goal": "muscle_gain", "secondary_goal": "general_fitness"},
        "training": {
            "experience": "intermediate",
            "available_days": 3,
            "session_duration_minutes": 45,
            "available_equipment": ["bodyweight", "dumbbell"],
            "workout_location": "home_gym",
        },
        "lifestyle": {
            "sleep_hours": 8.0,
            "stress_level": 4,
            "activity_level": "moderate",
            "daily_water_ml": 2500,
        },
        "nutrition": {
            "dietary_preferences": [],
            "allergies": [],
            "dietary_restrictions": [],
        },
    }


def _health(*, blocked: bool = False) -> dict[str, Any]:
    return {
        "injuries": [],
        "chronic_conditions": (
            [{"name": "test condition", "controlled": False, "medically_cleared": False}]
            if blocked
            else []
        ),
        "pain_areas": [],
        "mobility_limitations": [],
        "surgery_history": [],
    }


def _register(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Smoke-test-password-123!"},
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _prepare(client: TestClient, authorization: dict[str, str], *, blocked: bool = False) -> None:
    assert client.put("/api/v1/profile", headers=authorization, json=_profile()).status_code == 204
    assert (
        client.put(
            "/api/v1/health-profile", headers=authorization, json=_health(blocked=blocked)
        ).status_code
        == 204
    )


def test_full_authenticated_intelligent_workout_http_journey(smoke: SmokeEnvironment) -> None:
    client = smoke.client
    owner = _register(client, "owner@example.com")
    foreign = _register(client, "foreign@example.com")
    _prepare(client, owner)

    assert client.get("/api/v1/intelligent-workouts/plans", headers={}).status_code == 401
    invalid = client.post(
        "/api/v1/intelligent-workouts/plans/generate",
        headers=owner,
        json={"user_id": "foreign-user"},
    )
    assert invalid.status_code == 422

    generated = client.post(
        "/api/v1/intelligent-workouts/plans/generate",
        headers=owner,
        json={"duration_weeks": 8, "use_ai_assistance": False},
    )
    assert generated.status_code == 201, generated.text
    plan = generated.json()
    plan_id = plan["plan_id"]
    assert plan["generation_mode"] == "deterministic"

    active = client.get("/api/v1/intelligent-workouts/plans/active", headers=owner)
    history = client.get("/api/v1/intelligent-workouts/plans", headers=owner)
    detail = client.get(f"/api/v1/intelligent-workouts/plans/{plan_id}", headers=owner)
    assert active.status_code == history.status_code == detail.status_code == 200
    assert active.json()["plan_id"] == plan_id
    assert history.json()["items"][0]["plan_id"] == plan_id

    foreign_plan = client.get(f"/api/v1/intelligent-workouts/plans/{plan_id}", headers=foreign)
    assert foreign_plan.status_code == 404

    day = plan["weekly_schedule"][0]
    exercise = day["sections"][0]["exercises"][0]
    started = client.post(
        "/api/v1/intelligent-workouts/sessions",
        headers=owner,
        json={
            "plan_id": plan_id,
            "day_number": day["day_number"],
            "status": "in_progress",
            "completed_exercises": [],
        },
    )
    assert started.status_code == 201, started.text
    session_id = started.json()["session_id"]
    assert started.json()["completion_percentage"] == 0

    retrieved = client.get(f"/api/v1/intelligent-workouts/sessions/{session_id}", headers=owner)
    assert retrieved.status_code == 200
    assert (
        client.get(
            f"/api/v1/intelligent-workouts/sessions/{session_id}", headers=foreign
        ).status_code
        == 404
    )

    completed_exercise = {
        "exercise_id": exercise["exercise_id"],
        "completed_sets": [{"set_number": 1, "actual_reps": 8, "completed": True}],
        "skipped": False,
        "pain_reported": False,
    }
    progress: dict[str, object] = {
        "status": "in_progress",
        "completed_exercises": [completed_exercise],
        "actual_duration_minutes": 20,
    }
    updated = client.patch(
        f"/api/v1/intelligent-workouts/sessions/{session_id}", headers=owner, json=progress
    )
    assert updated.status_code == 200, updated.text
    assert 0 < updated.json()["completion_percentage"] < 100

    completed_exercise["pain_reported"] = True
    completed_exercise["pain_area"] = "shoulder discomfort"
    pain_update = client.patch(
        f"/api/v1/intelligent-workouts/sessions/{session_id}", headers=owner, json=progress
    )
    assert pain_update.status_code == 200
    assert pain_update.json()["adaptation_flags"] == ["pain_requires_review"]

    before_adaptation = client.get(
        f"/api/v1/intelligent-workouts/plans/{plan_id}", headers=owner
    ).json()
    adaptation = client.post(
        "/api/v1/intelligent-workouts/adaptation/analyze",
        headers=owner,
        json={"plan_id": plan_id},
    )
    assert adaptation.status_code == 200, adaptation.text
    assert adaptation.json()["automatic_application_allowed"] is False
    after_adaptation = client.get(
        f"/api/v1/intelligent-workouts/plans/{plan_id}", headers=owner
    ).json()
    assert before_adaptation == after_adaptation

    progress["status"] = "completed"
    assert (
        client.patch(
            f"/api/v1/intelligent-workouts/sessions/{session_id}",
            headers=owner,
            json=progress,
        ).status_code
        == 200
    )
    archived = client.post(f"/api/v1/intelligent-workouts/plans/{plan_id}/archive", headers=owner)
    assert archived.status_code == 200
    assert archived.json() == {"plan_id": plan_id, "status": "archived"}


def test_http_smoke_covers_blocked_readiness_and_deterministic_fallback(
    smoke: SmokeEnvironment,
) -> None:
    client = smoke.client
    blocked = _register(client, "blocked@example.com")
    _prepare(client, blocked, blocked=True)
    response = client.post("/api/v1/intelligent-workouts/plans/generate", headers=blocked, json={})
    assert response.status_code == 403

    fallback = _register(client, "fallback@example.com")
    _prepare(client, fallback)
    generated = client.post(
        "/api/v1/intelligent-workouts/plans/generate",
        headers=fallback,
        json={"use_ai_assistance": True},
    )
    assert generated.status_code == 201
    assert generated.json()["generation_mode"] == "deterministic_fallback"
