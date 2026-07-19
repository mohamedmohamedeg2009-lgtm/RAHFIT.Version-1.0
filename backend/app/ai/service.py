import json
from typing import Protocol, cast

import structlog
from pydantic import ValidationError

from app.ai.exceptions import AIProviderError, AISafetyError, AIValidationError
from app.ai.provider import AIProvider, AIProviderRequest, AIProviderResponse
from app.ai.schemas import (
    AIServiceRequest,
    AIServiceResponse,
    AITextOutput,
    OutputModelT,
)
from app.models.ai_context import AIApprovedContext, AIContextRequest
from app.models.ai_safety import AISafetyRequest, AISafetyResult, AISafetyRuntimeMetadata
from app.models.user import User
from app.services.ai_classifier import CapabilityClassifier


class ContextBuilder(Protocol):
    async def build_context(
        self,
        authenticated_user: User,
        request: AIContextRequest,
        daily_check_in: Any | None = None,
    ) -> AIApprovedContext: ...


class SafetyEvaluator(Protocol):
    def evaluate_safety(
        self,
        authenticated_user: User,
        request: AISafetyRequest,
    ) -> AISafetyResult: ...


class StructuredLogger(Protocol):
    def info(self, event: str, **event_fields: object) -> object: ...

    def warning(self, event: str, **event_fields: object) -> object: ...


class AIService:
    """The only application boundary permitted to invoke an AI provider."""

    def __init__(
        self,
        *,
        provider: AIProvider,
        context_builder: ContextBuilder,
        safety_engine: SafetyEvaluator,
        logger: StructuredLogger | None = None,
        daily_check_in_repository: Any | None = None,
    ) -> None:
        self.provider = provider
        self.context_builder = context_builder
        self.safety_engine = safety_engine
        self.logger = logger or cast(
            StructuredLogger,
            structlog.get_logger("app.ai.service"),
        )
        self.daily_check_in_repository = daily_check_in_repository

    async def generate_text(
        self,
        authenticated_user: User,
        request: AIServiceRequest,
    ) -> AIServiceResponse[AITextOutput]:
        provider_request, safety = await self.prepare_text(authenticated_user, request)
        return await self.generate_prepared_text(request, provider_request, safety)

    async def prepare_text(
        self,
        authenticated_user: User,
        request: AIServiceRequest,
    ) -> tuple[AIProviderRequest, AISafetyResult]:
        """Build approved provider input and enforce safety without provider I/O."""
        return await self._prepare(authenticated_user, request)

    async def generate_prepared_text(
        self,
        request: AIServiceRequest,
        provider_request: AIProviderRequest,
        safety: AISafetyResult,
    ) -> AIServiceResponse[AITextOutput]:
        """Generate from already-approved provider input exactly once."""
        try:
            response = await self.provider.generate_text(provider_request)
            output = AITextOutput(text=response.text)
        except ValidationError as exc:
            raise AIValidationError(self.provider.name, self.provider.model) from exc
        except AIProviderError as exc:
            self._log_failure(request, exc)
            raise
        self._log_success(request, response)
        return self._service_response(output, response, safety)

    async def generate_json(
        self,
        authenticated_user: User,
        request: AIServiceRequest,
        response_model: type[OutputModelT],
    ) -> AIServiceResponse[OutputModelT]:
        provider_request, safety = await self._prepare(authenticated_user, request)
        try:
            response = await self.provider.generate_json(provider_request, response_model)
            if response.structured_payload is None:
                raise AIValidationError(self.provider.name, self.provider.model)
            output = response_model.model_validate(response.structured_payload)
        except ValidationError as exc:
            raise AIValidationError(self.provider.name, self.provider.model) from exc
        except AIProviderError as exc:
            self._log_failure(request, exc)
            raise
        self._log_success(request, response)
        return self._service_response(output, response, safety)

    async def _prepare(
        self,
        authenticated_user: User,
        request: AIServiceRequest,
    ) -> tuple[AIProviderRequest, AISafetyResult]:
        normalized_prompt = CapabilityClassifier.normalize(request.prompt)
        if not normalized_prompt:
            raise AIValidationError(
                self.provider.name,
                self.provider.model,
                "ai_prompt_empty_after_normalization",
            )
        context_request = request.context_request.model_copy(
            update={"current_user_question": normalized_prompt}
        )
        daily_check_in = None
        if self.daily_check_in_repository is not None:
            from datetime import UTC, datetime
            daily_check_in = await self.daily_check_in_repository.get_by_date(
                authenticated_user.id, datetime.now(UTC).date()
            )
        approved_context = await self.context_builder.build_context(
            authenticated_user,
            context_request,
            daily_check_in=daily_check_in,
        )
        safety = self.safety_engine.evaluate_safety(
            authenticated_user,
            AISafetyRequest(
                authenticated_owner_reference=authenticated_user.id,
                normalized_user_message=normalized_prompt,
                classification=request.classification,
                policy=request.policy,
                approved_context=approved_context,
                runtime=AISafetyRuntimeMetadata(
                    request_id=request.request_id,
                    locale=request.locale,
                ),
            ),
        )
        if not safety.requires_provider:
            raise AISafetyError(safety.reason_code.value)
        approved_user_content = self._provider_context(approved_context, safety)
        metadata = {
            key: value
            for key, value in {
                "request_id": request.request_id,
                "context_version": approved_context.context_version,
                "safety_decision": safety.final_decision.value,
                "safety_reason_code": safety.reason_code.value,
            }.items()
            if value is not None
        }
        return (
            AIProviderRequest(
                system_instructions=request.system_instructions,
                approved_user_content=approved_user_content,
                max_output_tokens=request.max_output_tokens,
                metadata=metadata,
            ),
            safety,
        )

    @staticmethod
    def _provider_context(context: AIApprovedContext, safety: AISafetyResult) -> str:
        allowed = set(safety.allowed_context_sections)
        payload = {
            "context_version": context.context_version,
            "purpose": context.purpose.value,
            "sections": [
                {
                    "name": section.name.value,
                    "data": section.data,
                }
                for section in context.sections
                if section.name in allowed
            ],
        }
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    @staticmethod
    def _service_response(
        output: OutputModelT,
        response: AIProviderResponse,
        safety: AISafetyResult,
    ) -> AIServiceResponse[OutputModelT]:
        return AIServiceResponse[OutputModelT](
            output=output,
            provider=response.provider,
            model=response.model,
            usage=response.usage,
            latency_ms=response.latency_ms,
            provider_request_id=response.provider_request_id,
            safety_decision=safety.final_decision,
            safety_reason_code=safety.reason_code,
        )

    def _log_success(self, request: AIServiceRequest, response: AIProviderResponse) -> None:
        self.logger.info(
            "ai_generation_completed",
            request_id=request.request_id,
            provider=response.provider,
            model=response.model,
            latency_ms=response.latency_ms,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.total_tokens,
        )

    def _log_failure(self, request: AIServiceRequest, exc: AIProviderError) -> None:
        self.logger.warning(
            "ai_generation_failed",
            request_id=request.request_id,
            provider=exc.provider,
            model=exc.model,
            reason_code=exc.category.value,
        )
