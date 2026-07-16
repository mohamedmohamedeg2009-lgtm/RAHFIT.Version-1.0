from typing import Protocol

from app.health.models import HealthProfile
from app.profile.models import UserProfile
from app.users.models import UserIntelligenceSnapshot


class UserProfileReader(Protocol):
    async def get_by_user_id(self, user_id: str) -> UserProfile | None: ...


class HealthProfileReader(Protocol):
    async def get_by_user_id(self, user_id: str) -> HealthProfile | None: ...


class UserIntelligenceService:
    """Single owner-scoped read boundary for profile and health intelligence."""

    def __init__(
        self,
        profiles: UserProfileReader,
        health_profiles: HealthProfileReader,
    ) -> None:
        self.profiles = profiles
        self.health_profiles = health_profiles

    async def get_snapshot(self, user_id: str) -> UserIntelligenceSnapshot:
        owner = self._user_id(user_id)
        profile = await self.profiles.get_by_user_id(owner)
        health_profile = await self.health_profiles.get_by_user_id(owner)
        if profile is not None and profile.user_id != owner:
            raise RuntimeError("Profile ownership invariant failed.")
        if health_profile is not None and health_profile.user_id != owner:
            raise RuntimeError("Health profile ownership invariant failed.")
        return UserIntelligenceSnapshot(
            user_id=owner,
            profile=profile,
            health_profile=health_profile,
        )

    @staticmethod
    def _user_id(user_id: str) -> str:
        normalized = user_id.strip()
        if not normalized or len(normalized) > 256:
            raise ValueError("A valid user ID is required.")
        return normalized
