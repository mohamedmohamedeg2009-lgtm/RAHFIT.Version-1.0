from pydantic import BaseModel, ConfigDict

from app.profile.models import (
    BodyProfile,
    GoalsProfile,
    IdentityProfile,
    LifestyleProfile,
    NutritionProfile,
    TrainingProfile,
    UserProfile,
)


class UserProfileReadResponse(BaseModel):
    """Client-safe profile projection without ownership or persistence metadata."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    identity: IdentityProfile
    body: BodyProfile
    goals: GoalsProfile
    training: TrainingProfile
    lifestyle: LifestyleProfile
    nutrition: NutritionProfile

    @classmethod
    def from_domain(cls, profile: UserProfile) -> "UserProfileReadResponse":
        return cls(
            identity=profile.identity,
            body=profile.body,
            goals=profile.goals,
            training=profile.training,
            lifestyle=profile.lifestyle,
            nutrition=profile.nutrition,
        )
