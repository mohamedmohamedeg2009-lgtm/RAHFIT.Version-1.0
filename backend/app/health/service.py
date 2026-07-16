from typing import Protocol

from app.health.models import HealthProfile, HealthProfileData


class HealthProfileStore(Protocol):
    async def get_by_user_id(self, user_id: str) -> HealthProfile | None: ...

    async def save(self, user_id: str, profile: HealthProfileData) -> HealthProfile: ...


class HealthProfileNotFoundError(Exception):
    pass


class HealthProfileService:
    def __init__(self, health_profiles: HealthProfileStore) -> None:
        self.health_profiles = health_profiles

    async def get_profile(self, user_id: str) -> HealthProfile:
        profile = await self.health_profiles.get_by_user_id(self._user_id(user_id))
        if profile is None:
            raise HealthProfileNotFoundError
        return profile

    async def save_profile(self, user_id: str, data: HealthProfileData) -> HealthProfile:
        owner = self._user_id(user_id)
        profile = await self.health_profiles.save(owner, data)
        if profile.user_id != owner:
            raise RuntimeError("Health repository returned another user's profile.")
        return profile

    @staticmethod
    def _user_id(user_id: str) -> str:
        normalized = user_id.strip()
        if not normalized or len(normalized) > 256:
            raise ValueError("A valid user ID is required.")
        return normalized
