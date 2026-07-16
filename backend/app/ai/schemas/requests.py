from pydantic import BaseModel, ConfigDict, Field

from app.ai.context_limits import AI_CONTEXT_LIMITS
from app.models.ai_classifier import AICapabilityClassificationResult
from app.models.ai_context import AIContextRequest
from app.models.ai_policy import AIPolicyResult


class AIServiceRequest(BaseModel):
    """Trusted internal generation request; it is not a public API schema."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    prompt: str = Field(min_length=1, max_length=AI_CONTEXT_LIMITS.maximum_question_characters)
    system_instructions: str = Field(min_length=1, max_length=10_000)
    context_request: AIContextRequest
    classification: AICapabilityClassificationResult
    policy: AIPolicyResult
    request_id: str | None = Field(default=None, max_length=128)
    locale: str | None = Field(default=None, max_length=16)
    max_output_tokens: int | None = Field(default=None, ge=1, le=4_096)
