from pydantic import BaseModel, ConfigDict

from app.health.models import HealthProfile
from app.profile.models import UserProfile


class UserIntelligenceSnapshot(BaseModel):
    """Owner-scoped canonical input for readiness and future AI decisions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    user_id: str
    profile: UserProfile | None
    health_profile: HealthProfile | None
