from typing import Protocol

from app.profile.models import UserProfile, UserProfileData


class UserProfileStore(Protocol):
    async def get_by_user_id(self, user_id: str) -> UserProfile | None: ...

    async def save(self, user_id: str, profile: UserProfileData) -> UserProfile: ...


class UserProfileNotFoundError(Exception):
    pass


class UserProfileService:
    def __init__(self, profiles: UserProfileStore) -> None:
        self.profiles = profiles

    async def get_profile(self, user_id: str) -> UserProfile:
        profile = await self.profiles.get_by_user_id(self._user_id(user_id))
        if profile is None:
            raise UserProfileNotFoundError
        return profile

    async def save_profile(self, user_id: str, data: UserProfileData) -> UserProfile:
        owner = self._user_id(user_id)
        profile = await self.profiles.save(owner, data)
        if profile.user_id != owner:
            raise RuntimeError("Profile repository returned another user's profile.")
        return profile

    @staticmethod
    def _user_id(user_id: str) -> str:
        normalized = user_id.strip()
        if not normalized or len(normalized) > 256:
            raise ValueError("A valid user ID is required.")
        return normalized
