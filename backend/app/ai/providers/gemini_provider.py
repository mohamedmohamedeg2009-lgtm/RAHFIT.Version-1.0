from time import perf_counter
from typing import Protocol, cast

import httpx
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.ai.exceptions import (
    AIProviderError,
    AITimeoutError,
    AIValidationError,
    ProviderErrorCategory,
)
from app.ai.provider import (
    AIProvider,
    AIProviderRequest,
    AIProviderResponse,
    AITokenUsage,
    ProviderAvailabilityStatus,
    ResponseModelT,
)


class _GeminiUsage(Protocol):
    prompt_token_count: int | None
    candidates_token_count: int | None
    total_token_count: int | None


class _GeminiResponse(Protocol):
    text: str | None
    parsed: object
    usage_metadata: _GeminiUsage | None
    response_id: str | None


class _GeminiModels(Protocol):
    async def generate_content(
        self,
        *,
        model: str,
        contents: str,
        config: types.GenerateContentConfig,
    ) -> _GeminiResponse: ...

    async def get(self, *, model: str) -> object: ...


class _GeminiAsyncClient(Protocol):
    models: _GeminiModels


class GeminiProvider(AIProvider):
    """Google GenAI SDK adapter with bounded, typed text and JSON generation."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        request_timeout_seconds: float,
        max_output_tokens: int,
        client: _GeminiAsyncClient | None = None,
    ) -> None:
        self._model = model
        self._request_timeout_seconds = request_timeout_seconds
        self._max_output_tokens = max_output_tokens
        self._client = client or cast(
            _GeminiAsyncClient,
            genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(
                    timeout=round(request_timeout_seconds * 1_000),
                ),
            ).aio,
        )

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model(self) -> str:
        return self._model

    @property
    def request_timeout_seconds(self) -> float:
        return self._request_timeout_seconds

    @property
    def max_output_tokens(self) -> int:
        return self._max_output_tokens

    @property
    def availability(self) -> ProviderAvailabilityStatus:
        return ProviderAvailabilityStatus.AVAILABLE

    async def generate_text(self, request: AIProviderRequest) -> AIProviderResponse:
        response, latency_ms = await self._call(
            request,
            types.GenerateContentConfig(
                system_instruction=request.system_instructions,
                max_output_tokens=self._token_limit(request),
            ),
        )
        try:
            text = self._validated_text(response)
            return self._response(response, text, latency_ms)
        except (TypeError, ValueError, ValidationError) as exc:
            raise AIValidationError(self.name, self.model) from exc

    async def generate_json(
        self,
        request: AIProviderRequest,
        response_model: type[ResponseModelT],
    ) -> AIProviderResponse:
        response, latency_ms = await self._call(
            request,
            types.GenerateContentConfig(
                system_instruction=request.system_instructions,
                max_output_tokens=self._token_limit(request),
                response_mime_type="application/json",
                response_schema=response_model,
            ),
        )
        try:
            text = self._validated_text(response)
            parsed = response.parsed
            if isinstance(parsed, response_model):
                validated = parsed
            elif parsed is not None:
                validated = response_model.model_validate(parsed)
            else:
                validated = response_model.model_validate_json(text)
            return self._response(
                response,
                text,
                latency_ms,
                structured_payload=validated.model_dump(mode="json"),
            )
        except (TypeError, ValueError, ValidationError) as exc:
            raise AIValidationError(self.name, self.model) from exc

    async def health_check(self) -> bool:
        try:
            await self._client.models.get(model=self.model)
        except Exception:
            return False
        return True

    async def _call(
        self,
        request: AIProviderRequest,
        config: types.GenerateContentConfig,
    ) -> tuple[_GeminiResponse, int]:
        started = perf_counter()
        try:
            response = await self._client.models.generate_content(
                model=self.model,
                contents=request.approved_user_content,
                config=config,
            )
        except (TimeoutError, httpx.TimeoutException) as exc:
            raise AITimeoutError(self.name, self.model) from exc
        except errors.APIError as exc:
            raise self._map_api_error(exc) from exc
        except Exception as exc:
            raise AIProviderError(
                ProviderErrorCategory.UNEXPECTED,
                self.name,
                self.model,
            ) from exc
        return response, round((perf_counter() - started) * 1_000)

    def _map_api_error(self, exc: errors.APIError) -> AIProviderError:
        status_code = getattr(exc, "code", None)
        if status_code in {401, 403}:
            category = ProviderErrorCategory.AUTHENTICATION_FAILED
        elif status_code == 429:
            category = ProviderErrorCategory.RATE_LIMITED
        elif isinstance(status_code, int) and status_code >= 500:
            category = ProviderErrorCategory.UNAVAILABLE
        else:
            category = ProviderErrorCategory.UNEXPECTED
        return AIProviderError(category, self.name, self.model)

    def _response(
        self,
        response: _GeminiResponse,
        text: str,
        latency_ms: int,
        *,
        structured_payload: dict[str, object] | None = None,
    ) -> AIProviderResponse:
        usage = response.usage_metadata
        return AIProviderResponse(
            text=text,
            structured_payload=structured_payload,
            provider=self.name,
            model=self.model,
            usage=AITokenUsage(
                input_tokens=self._safe_int(
                    usage.prompt_token_count if usage is not None else None
                ),
                output_tokens=self._safe_int(
                    usage.candidates_token_count if usage is not None else None
                ),
                total_tokens=self._safe_int(usage.total_token_count if usage is not None else None),
            ),
            latency_ms=latency_ms,
            provider_request_id=(
                response.response_id if isinstance(response.response_id, str) else None
            ),
        )

    def _token_limit(self, request: AIProviderRequest) -> int:
        return min(
            request.max_output_tokens or self.max_output_tokens,
            self.max_output_tokens,
        )

    @staticmethod
    def _validated_text(response: _GeminiResponse) -> str:
        text = response.text
        if not isinstance(text, str) or not text.strip():
            raise ValueError("provider_returned_empty_text")
        return text.strip()

    @staticmethod
    def _safe_int(value: object) -> int | None:
        return value if isinstance(value, int) and value >= 0 else None
