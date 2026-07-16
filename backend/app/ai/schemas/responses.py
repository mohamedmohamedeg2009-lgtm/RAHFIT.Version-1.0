from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.ai.provider import AITokenUsage
from app.models.ai_safety import AISafetyDecision, AISafetyReasonCode


class AITextOutput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str = Field(min_length=1, max_length=20_000)


OutputModelT = TypeVar("OutputModelT", bound=BaseModel)


class AIServiceResponse(BaseModel, Generic[OutputModelT]):
    model_config = ConfigDict(frozen=True, extra="forbid")

    output: OutputModelT
    provider: str
    model: str
    usage: AITokenUsage
    latency_ms: int = Field(ge=0)
    provider_request_id: str | None = Field(default=None, max_length=200)
    safety_decision: AISafetyDecision
    safety_reason_code: AISafetyReasonCode
