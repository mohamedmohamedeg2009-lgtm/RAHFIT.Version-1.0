from time import perf_counter

import httpx
from pydantic import BaseModel, ValidationError

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


class OpenAICompatibleProvider(AIProvider):
    """Legacy compatible adapter retained for existing deployments and tests."""

    endpoint = "https://api.openai.com/v1/chat/completions"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        request_timeout_seconds: float,
        max_output_tokens: int,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._request_timeout_seconds = request_timeout_seconds
        self._max_output_tokens = max_output_tokens
        self._transport = transport

    @property
    def name(self) -> str:
        return "openai"

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
        return await self._generate(request)

    async def generate_json(
        self,
        request: AIProviderRequest,
        response_model: type[ResponseModelT],
    ) -> AIProviderResponse:
        response = await self._generate(request, response_model=response_model)
        try:
            validated = response_model.model_validate_json(response.text)
        except ValidationError as exc:
            raise AIValidationError(self.name, self.model) from exc
        return response.model_copy(update={"structured_payload": validated.model_dump()})

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(
                timeout=self.request_timeout_seconds,
                transport=self._transport,
            ) as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
        except httpx.HTTPError:
            return False
        return response.status_code < 500

    async def _generate(
        self,
        request: AIProviderRequest,
        *,
        response_model: type[BaseModel] | None = None,
    ) -> AIProviderResponse:
        started = perf_counter()
        token_limit = min(
            request.max_output_tokens or self.max_output_tokens,
            self.max_output_tokens,
        )
        payload: dict[str, object] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": request.system_instructions},
                {"role": "user", "content": request.approved_user_content},
            ],
            "max_tokens": token_limit,
        }
        if response_model is not None:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "strict": True,
                    "schema": response_model.model_json_schema(),
                },
            }
        try:
            async with httpx.AsyncClient(
                timeout=self.request_timeout_seconds,
                transport=self._transport,
            ) as client:
                response = await client.post(
                    self.endpoint,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise AITimeoutError(self.name, self.model) from exc
        except httpx.HTTPError as exc:
            raise self._error(ProviderErrorCategory.UNAVAILABLE) from exc
        except Exception as exc:
            raise self._error(ProviderErrorCategory.UNEXPECTED) from exc

        self._raise_for_status(response.status_code)
        try:
            raw_payload = response.json()
            text = raw_payload["choices"][0]["message"]["content"]
            if not isinstance(text, str) or not text.strip():
                raise ValueError
            usage_value = raw_payload.get("usage") if isinstance(raw_payload, dict) else None
            usage = usage_value if isinstance(usage_value, dict) else {}
            request_id = raw_payload.get("id") if isinstance(raw_payload, dict) else None
            result = AIProviderResponse(
                text=text.strip(),
                provider=self.name,
                model=self.model,
                usage=AITokenUsage(
                    input_tokens=self._non_negative_int(usage.get("prompt_tokens")),
                    output_tokens=self._non_negative_int(usage.get("completion_tokens")),
                    total_tokens=self._non_negative_int(usage.get("total_tokens")),
                ),
                latency_ms=round((perf_counter() - started) * 1_000),
                provider_request_id=request_id if isinstance(request_id, str) else None,
            )
        except (KeyError, IndexError, TypeError, ValueError, ValidationError) as exc:
            raise AIValidationError(self.name, self.model) from exc
        return result

    def _raise_for_status(self, status_code: int) -> None:
        if status_code in {401, 403}:
            raise self._error(ProviderErrorCategory.AUTHENTICATION_FAILED)
        if status_code == 429:
            raise self._error(ProviderErrorCategory.RATE_LIMITED)
        if status_code >= 500:
            raise self._error(ProviderErrorCategory.UNAVAILABLE)
        if status_code >= 400:
            raise self._error(ProviderErrorCategory.UNEXPECTED)

    def _error(self, category: ProviderErrorCategory) -> AIProviderError:
        return AIProviderError(category, self.name, self.model)

    @staticmethod
    def _non_negative_int(value: object) -> int | None:
        return value if isinstance(value, int) and value >= 0 else None
