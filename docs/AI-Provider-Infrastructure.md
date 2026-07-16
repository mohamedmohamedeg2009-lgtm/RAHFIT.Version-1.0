# RAHFIT AI — Provider-Based AI Architecture

**Status:** Implemented foundation

**Scope:** Provider abstraction, Gemini and mock adapters, safe service orchestration, structured output validation, dependency injection, configuration, logging, and tests. No public generation endpoint or frontend feature is included.

## 1. Architecture Goal

Application and domain services must never import or call a vendor SDK. All generation follows one dependency direction:

```text
Business service
    ↓
AIService
    ↓
AIProvider
    ↓
GeminiProvider | MockProvider | future provider
```

`AIService` is the application boundary. `AIProvider` is the vendor-neutral contract. Provider adapters own vendor translation only. This keeps safety, context ownership, validation, and domain policy outside vendor code.

## 2. Package Responsibilities

| Package or file | Responsibility |
| --- | --- |
| `app/ai/provider.py` | Abstract provider interface and provider-neutral request, response, usage, and availability contracts |
| `app/ai/exceptions.py` | Stable provider, timeout, validation, and safety exceptions without vendor details |
| `app/ai/service.py` | Approved Context construction, Safety Engine invocation, provider invocation, output validation, and safe metadata logging |
| `app/ai/providers/gemini_provider.py` | Google GenAI SDK translation, timeout enforcement, structured response configuration, usage extraction, and stable error mapping |
| `app/ai/providers/mock_provider.py` | Deterministic test provider with no network behavior |
| `app/ai/providers/openai_compatible_provider.py` | Backward-compatible adapter for existing configured deployments |
| `app/ai/providers/__init__.py` | Stable exports, including compatibility names used by earlier tests and services |
| `app/ai/schemas/` | Trusted internal AIService request and typed response contracts |
| `app/ai/prompts/` | Reserved for a future reviewed and versioned prompt layer; no prompt templates are implemented here |
| `app/ai/resolver.py` | Local configuration resolution and explicit provider injection |

## 3. Provider Contract

Every provider implements:

- `generate_text` for bounded text output.
- `generate_json` for output constrained by a caller-provided Pydantic model.
- `health_check` for an explicit provider probe.
- Stable provider name, model, timeout, output-token limit, and availability properties.

The legacy `generate` method remains as a compatibility alias for text generation. New application code uses `AIService`, not this alias and not provider adapters directly.

Provider requests contain only trusted system instructions, serialized approved context, bounded output tokens, and non-sensitive correlation metadata. API keys never enter provider-neutral request objects.

## 4. AIService Pipeline

For text and structured generation, `AIService` performs the following sequence:

1. Normalize and bound the trusted internal prompt.
2. Replace the context request's question with the normalized prompt.
3. Build owner-scoped Approved Context through the existing Context Builder.
4. Construct the existing trusted `AISafetyRequest` from authenticated ownership, classification, policy, context, locale, and request ID.
5. Invoke the existing deterministic Safety Engine.
6. Stop with `AISafetyError` when the safety result does not require a provider.
7. Serialize only context sections approved by the Safety Engine.
8. Invoke the injected provider exactly once.
9. Validate text or structured output.
10. Return typed output plus safe provider, model, token, latency, request ID, and safety metadata.

The service has no database access, HTTP endpoint, authentication logic, provider selection global, or mutable singleton.

## 5. Gemini Provider

`GeminiProvider` uses the official Google GenAI SDK and its asynchronous API. Model, API key, timeout, and maximum output tokens come only from validated settings.

Text generation supplies approved context as content and trusted system instructions through the SDK configuration. JSON generation additionally requests `application/json` and supplies the caller's Pydantic response model as the response schema. The returned value is validated before it crosses the provider boundary.

The adapter extracts safe token counts and the provider request identifier when available. It maps timeout, authentication, rate-limit, server, invalid-response, and unexpected failures to stable internal exceptions. Raw SDK errors and credentials are never returned or logged.

The availability endpoint remains configuration-only and does not call `health_check`. A health probe occurs only when an explicit trusted caller invokes it.

## 6. Mock Provider

`MockProvider` is deterministic and makes no network calls. It records typed requests and supports stable success, timeout, rate-limit, unavailable, and invalid-response modes.

The resolver cannot select MockProvider from runtime configuration. Tests inject it through constructors or the resolver override. Compatibility exports retain the previous `FakeAIProvider` and `FakeProviderMode` names.

## 7. Structured Outputs

`generate_json` requires a concrete Pydantic model from the trusted caller. This supports coach responses and future workout or nutrition output contracts without coupling the provider package to those domains.

Validation occurs at two boundaries:

1. The provider asks the vendor for the requested schema and validates the returned payload.
2. `AIService` validates the provider-neutral structured payload again before returning it.

Missing payloads, invalid JSON, additional forbidden fields, impossible field values, or schema mismatches result in `AIValidationError`. Raw LLM output is never accepted as a workout plan, nutrition plan, or coach response.

## 8. Dependency Injection

`AIService` receives these dependencies through its constructor:

- `AIProvider`
- Context Builder-compatible dependency
- Safety Engine-compatible dependency
- optional structured logger

`AIProviderResolver` receives validated settings and an optional explicit provider override. No provider instance, API client, service, or mutable provider choice is stored in module-global state.

Business services that later require generation must depend on `AIService`. They must not import `google.genai`, `GeminiProvider`, or any other provider adapter.

## 9. Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `AI_FEATURE_ENABLED` | `false` | Fail-safe feature gate |
| `AI_PROVIDER` | `gemini` | Provider selected by the resolver |
| `GEMINI_API_KEY` | empty | Gemini secret loaded through `SecretStr` |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model identifier |
| `AI_TIMEOUT` | `15` | Gemini request timeout in seconds, bounded to 1–60 |
| `AI_MAX_OUTPUT_TOKENS` | `600` | Output ceiling, bounded to 1–4096 |

Legacy `AI_API_KEY`, `AI_MODEL`, and `AI_REQUEST_TIMEOUT_SECONDS` remain available only when `AI_PROVIDER=openai`. This preserves existing deployments while making Gemini the default.

Real credentials belong in ignored local environment files or deployment secret managers. They must never be committed, returned by an API, included in request metadata, or logged.

## 10. Error Contract

| Exception | Meaning |
| --- | --- |
| `AIProviderError` | Stable provider failure with provider, model, and safe category |
| `AITimeoutError` | Provider timeout |
| `AIValidationError` | Invalid provider output or invalid internal generation input |
| `AISafetyError` | Safety Engine rejected provider generation |

Stable provider categories include disabled, not configured, unavailable, timeout, rate limited, invalid response, authentication failure, and unexpected failure.

## 11. Logging and Privacy

Successful generation emits a structured `ai_generation_completed` event containing only:

- request ID
- provider
- model
- latency
- input, output, and total token counts when available

Provider failures emit `ai_generation_failed` with the stable reason code. Logs never contain API keys, prompts, system instructions, Approved Context data, full provider responses, authentication data, or raw vendor exception messages.

## 12. Adding a Future Provider

To add a provider safely:

1. Create an adapter under `app/ai/providers/` that implements every `AIProvider` method.
2. Keep SDK imports inside that adapter.
3. Load all credentials, models, limits, and timeouts from validated settings.
4. Map vendor failures to the stable exception contract.
5. Implement Pydantic-backed structured generation and defensive response parsing.
6. Add deterministic, network-free unit tests for text, JSON, timeout, authentication, rate limit, malformed output, token metadata, and health behavior.
7. Register the provider in `AIProviderResolver` without changing `AIService` or business services.
8. Document its configuration and operational behavior.

## 13. Testing Strategy

Automated tests verify:

- Gemini text and structured configuration through an injected SDK client.
- Pydantic validation of structured responses.
- Stable timeout and rate-limit mapping without secret leakage.
- Isolated health-check behavior.
- MockProvider determinism and network independence.
- Existing OpenAI-compatible behavior and compatibility imports.
- Context construction before safety evaluation.
- Safety rejection before any provider call.
- Provider invocation only after an allowed safety result.
- Structured validation at AIService.
- Metadata-only logging.
- Configuration-derived availability without provider calls.

No automated test calls Gemini, OpenAI, or another paid service.

## 14. Operational Boundaries

- No public generation endpoint is introduced.
- No authentication, MongoDB, repository, workout, nutrition, dashboard, or frontend behavior is changed.
- No automatic retry is performed, preventing accidental duplicate billing.
- No tools, browsing, code execution, file access, function calling, streaming, agents, or memory are enabled.
- Provider output cannot directly mutate workout or nutrition state.
- Future public generation requires the idempotency, quota, persistence, post-generation validation, and orchestration controls documented by the Architecture Gate Review.

## 15. Migration

No database migration is required.

Deployment configuration must provide `GEMINI_API_KEY` when Gemini is enabled. Existing OpenAI-compatible deployments must set `AI_PROVIDER=openai` explicitly and may continue using their existing legacy variables.
