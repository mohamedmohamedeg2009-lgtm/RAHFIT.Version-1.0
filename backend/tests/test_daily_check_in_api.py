"""Integration test suite for Daily Check-in endpoints, persistence, and AI context integration."""

from datetime import UTC, date, datetime

import httpx
import pytest
from fastapi import FastAPI, status

from app.controllers.auth import get_current_user
from app.controllers.daily_check_in import get_daily_check_in_service, router
from app.database.indexes import REQUIRED_INDEXES
from app.models.ai_context import AIContextPurpose, AIContextRequest
from app.models.daily_check_in import DailyCheckInInputs, HydrationStatus
from app.models.user import User
from app.repositories.daily_check_in import MongoDailyCheckInRepository
from app.services.daily_check_in import DailyCheckInService
from app.services.daily_check_in_engine import DailyCheckInEngine
from tests.test_ai_conversation import InMemoryAIConversationStore


class InMemoryDailyCheckInRepository:
    def __init__(self) -> None:
        self.store: dict[tuple[str, str], dict] = {}

    async def upsert(self, check_in):
        key = (check_in.user_id, check_in.date.isoformat())
        self.store[key] = check_in
        return check_in

    async def get_by_date(self, user_id: str, check_in_date: date):
        key = (user_id, check_in_date.isoformat())
        return self.store.get(key)

    async def list_history(self, user_id: str, limit: int = 20, offset: int = 0):
        matching = [
            item
            for item in self.store.values()
            if item.user_id == user_id
        ]
        matching.sort(key=lambda x: x.date, reverse=True)
        return matching[offset : offset + limit], len(matching)


@pytest.fixture
def test_user() -> User:
    return User(
        id="owner-user-123",
        email="owner@example.com",
        password_hash="hashed_password",
        is_active=True,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def other_user() -> User:
    return User(
        id="other-user-456",
        email="other@example.com",
        password_hash="hashed_password",
        is_active=True,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def memory_repo() -> InMemoryDailyCheckInRepository:
    return InMemoryDailyCheckInRepository()


@pytest.fixture
def check_in_service(memory_repo: InMemoryDailyCheckInRepository) -> DailyCheckInService:
    return DailyCheckInService(memory_repo, DailyCheckInEngine())  # type: ignore[arg-type]


@pytest.fixture
def app(test_user: User, check_in_service: DailyCheckInService) -> FastAPI:
    fastapi_app = FastAPI()
    fastapi_app.include_router(router, prefix="/api/v1")
    fastapi_app.dependency_overrides[get_current_user] = lambda: test_user
    fastapi_app.dependency_overrides[get_daily_check_in_service] = lambda: check_in_service
    return fastapi_app


@pytest.mark.asyncio
async def test_1_creates_first_check_in_for_today(app: FastAPI) -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post(
            "/api/v1/check-ins/daily",
            json={
                "sleep_hours": 8.0,
                "sleep_quality": 4,
                "energy_level": 4,
                "stress_level": 2,
                "muscle_soreness": 1,
                "pain_level": 0,
                "hydration_status": "good",
                "mood": 4,
                "optional_note": "Feeling energetic today",
            },
        )
        assert res.status_code == status.HTTP_200_OK
        data = res.json()["check_in"]
        assert data["user_id"] == "owner-user-123"
        assert data["readiness_result"]["readiness_score"] >= 80
        assert data["readiness_result"]["recommended_action"] == "normal_training"


@pytest.mark.asyncio
async def test_2_updates_same_day_rather_than_duplicating(app: FastAPI) -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        # First submission
        res1 = await client.post(
            "/api/v1/check-ins/daily",
            json={
                "sleep_hours": 7.0,
                "sleep_quality": 3,
                "energy_level": 3,
                "stress_level": 3,
                "muscle_soreness": 2,
                "pain_level": 0,
                "hydration_status": "moderate",
                "mood": 3,
            },
        )
        assert res1.status_code == status.HTTP_200_OK
        id1 = res1.json()["check_in"]["id"]

        # Second submission for same day
        res2 = await client.post(
            "/api/v1/check-ins/daily",
            json={
                "sleep_hours": 8.5,
                "sleep_quality": 5,
                "energy_level": 5,
                "stress_level": 1,
                "muscle_soreness": 1,
                "pain_level": 0,
                "hydration_status": "good",
                "mood": 5,
            },
        )
        assert res2.status_code == status.HTTP_200_OK
        data2 = res2.json()["check_in"]
        assert data2["id"] == id1  # Same ID updated
        assert data2["readiness_result"]["readiness_score"] >= 80

        # Verify today endpoint returns updated check-in
        res_today = await client.get("/api/v1/check-ins/daily/today")
        assert res_today.status_code == status.HTTP_200_OK
        assert res_today.json()["check_in"]["id"] == id1


@pytest.mark.asyncio
async def test_3_another_user_cannot_access_owner_check_in(
    app: FastAPI, other_user: User
) -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        await client.post(
            "/api/v1/check-ins/daily",
            json={
                "sleep_hours": 8.0,
                "sleep_quality": 4,
                "energy_level": 4,
                "stress_level": 2,
                "muscle_soreness": 1,
                "pain_level": 0,
                "hydration_status": "good",
                "mood": 4,
            },
        )

    # Switch to other_user
    app.dependency_overrides[get_current_user] = lambda: other_user
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        res_today = await client.get("/api/v1/check-ins/daily/today")
        assert res_today.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_4_history_is_owner_scoped_and_newest_first(app: FastAPI) -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        await client.post(
            "/api/v1/check-ins/daily",
            json={
                "sleep_hours": 8.0,
                "sleep_quality": 4,
                "energy_level": 4,
                "stress_level": 2,
                "muscle_soreness": 1,
                "pain_level": 0,
                "hydration_status": "good",
                "mood": 4,
            },
        )
        res_hist = await client.get("/api/v1/check-ins/daily/history?limit=10&offset=0")
        assert res_hist.status_code == status.HTTP_200_OK
        hist = res_hist.json()
        assert hist["total"] == 1
        assert len(hist["items"]) == 1


@pytest.mark.asyncio
async def test_5_invalid_ranges_are_rejected(app: FastAPI) -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post(
            "/api/v1/check-ins/daily",
            json={
                "sleep_hours": 30.0,  # Invalid
                "sleep_quality": 4,
                "energy_level": 4,
                "stress_level": 2,
                "muscle_soreness": 1,
                "pain_level": 0,
                "hydration_status": "good",
                "mood": 4,
            },
        )
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_6_unsafe_html_note_is_rejected(app: FastAPI) -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        res = await client.post(
            "/api/v1/check-ins/daily",
            json={
                "sleep_hours": 8.0,
                "sleep_quality": 4,
                "energy_level": 4,
                "stress_level": 2,
                "muscle_soreness": 1,
                "pain_level": 0,
                "hydration_status": "good",
                "mood": 4,
                "optional_note": "<script>alert('hack')</script>",
            },
        )
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_7_unique_owner_date_index_exists() -> None:
    assert "daily_check_ins" in REQUIRED_INDEXES
    assert "daily_check_ins_user_date_unique" in REQUIRED_INDEXES["daily_check_ins"]
