# RAHFIT AI — AI Provider Infrastructure and Availability

**Sprint:** 2.1  
**Status:** Implemented  
**Scope:** Provider infrastructure only. No AI Coach conversation, prompt acceptance endpoint, memory, context builder, plan mutation, or chat interface is included.

## 1. Sprint Scope

This sprint establishes the smallest safe boundary required for future AI features. The backend can identify whether AI is disabled, requires setup, is locally available, or is temporarily unavailable. A provider-neutral contract prevents future domain services from depending directly on one vendor.

Core authentication, assessment, dashboard, workout, and nutrition functionality remains independent of provider availability. No provider request occurs during startup or an availability check.

## 2. Provider-Neutral Architecture

The infrastructure has five boundaries:

1. Environment-backed settings normalize provider configuration without consuming generic host variables.
2. A typed provider protocol describes generic request, response, usage, availability, and failure behavior.
3. An OpenAI-compatible adapter translates the protocol into one external HTTP request.
4. A resolver selects the configured adapter or returns a safe local availability state.
5. An availability service exposes secret-free status to the authenticated API and existing dashboard feature system.

No RAHFIT assessment, workout, nutrition, safety, conversation, or user-context logic exists inside the provider interface.

## 3. Provider Contract

The generic request contains system instructions, approved user content, a bounded output-token request, and optional non-sensitive metadata. It does not contain domain-specific models or provider credentials.

The generic response contains generated text, an optional structured payload, provider and model names, optional input/output/total token counts, latency, and a safe provider request identifier. It never includes authentication headers, API keys, raw client objects, or vendor exceptions.

The provider protocol exposes its configured model, request timeout, maximum output tokens, local availability, and one non-streaming generation operation. Streaming, tools, browsing, files, function calling, and agents are intentionally absent.

## 4. Configured Provider Adapter

The configured adapter targets an OpenAI-compatible chat-completions interface because no previously installed vendor SDK or stronger project-specific provider decision existed. The runtime uses the already approved HTTP client dependency rather than introducing a large SDK.

The adapter is instantiated only after the feature is enabled, the provider name is supported, and a non-blank key exists. Its HTTP client is created only for a generation request. It enforces the configured timeout and caps request output tokens at the configured maximum. There is no startup call, availability probe, streaming, or automatic retry loop.

Provider responses are validated defensively. Missing or blank content becomes a stable invalid-response error. Token usage and request identifiers are accepted only when they have the expected safe types.

## 5. Deterministic Fake Provider

The fake provider is an explicit test dependency. It never performs network access and returns a stable response, stable request identifier, one-millisecond latency, and deterministic token counts. Tests can select deterministic timeout, rate-limit, unavailable, and invalid-response modes and can inspect the typed requests received.

The configuration resolver never selects `fake`, including in production. Tests inject it directly through the resolver override. This prevents a fake response from silently becoming production behavior.

## 6. Provider Resolver

The resolver has no global mutable state. It receives validated settings and an optional test override. Resolution is local and deterministic:

| Condition | Result |
| --- | --- |
| Feature disabled | `disabled` |
| Feature enabled with missing/blank key | `setup_required` |
| Supported provider with valid local configuration | `available` |
| Unknown provider | `temporarily_unavailable` |
| Explicit test override | `available` with the injected provider |

Resolving availability does not make an external request or create an HTTP client.

## 7. Availability API

`GET /api/v1/ai-coach/availability` is the only AI Coach-prefixed endpoint in this sprint. It requires authentication because the existing dashboard and future feature entitlements are authenticated product surfaces.

Expected configuration states return successful responses. The response contains feature-enabled state, stable status, safe provider/model names where applicable, a stable reason code, and concise display text. It does not reveal the key, raw key-presence diagnostics, headers, stack traces, or provider authentication details.

No endpoint accepts prompts, user content, provider payloads, conversations, messages, or memory.

## 8. Dashboard Integration

The existing dashboard already has a reusable feature-availability model, so it consumes the dedicated availability service. The dashboard maps infrastructure state to its existing feature statuses without adding a page, route, or custom AI Coach interface. It contains presentation mapping only; provider selection remains in the resolver and availability service.

## 9. Environment Configuration

| Variable | Default | Validation and purpose |
| --- | --- | --- |
| `AI_FEATURE_ENABLED` | `false` | Explicit feature gate; disabled by default |
| `AI_PROVIDER` | `openai` | Trimmed and normalized to lowercase; unknown values resolve safely |
| `AI_API_KEY` | empty | Optional secret; blank/whitespace is treated as missing |
| `AI_MODEL` | `gpt-4.1-mini` | Trimmed; blank values use the safe default |
| `AI_REQUEST_TIMEOUT_SECONDS` | `15` | Safe range 1–60 seconds; invalid values fall back to 15 |
| `AI_MAX_OUTPUT_TOKENS` | `600` | Safe range 1–4096; invalid values fall back to 600 |

All variables use an unambiguous `AI_` prefix. Real credentials belong in ignored local/deployment secrets, never `.env.example` or source control.

## 10. Stable Error Mapping

Internal categories are `provider_disabled`, `provider_not_configured`, `provider_unavailable`, `provider_timeout`, `provider_rate_limited`, `provider_invalid_response`, `provider_authentication_failure`, and `unexpected_provider_failure`.

The configured adapter maps timeouts, network failures, authentication responses, rate limits, server failures, invalid payloads, and other HTTP failures into these stable categories. Vendor exception text is retained only as a chained internal cause and is not returned by the availability API.

Future callers may log provider name, model, stable category, latency, and request correlation identifiers. They must not log API keys, authorization headers, full instructions, approved user content, sensitive context, or full provider responses.

## 11. Startup and Failure Behavior

The backend starts when AI is disabled, when the key is absent, and when the feature is enabled but setup is incomplete. Invalid provider names become a safe availability state instead of breaking unrelated routes. Invalid timeout and token settings fall back to bounded defaults.

Authentication, dashboard, assessment, workout, and nutrition services neither import provider-specific clients nor depend on a successful external request. Availability checks are local and cannot incur paid usage.

## 12. Testing Strategy

Automated tests cover configuration defaults and normalization, whitespace keys, bounded numeric settings, every availability state, unknown providers, production rejection of fake configuration, resolver override, deterministic fake response and token metadata, all fake failure modes, configured-adapter parsing, stable HTTP error mapping, authenticated availability responses, guest rejection, secret exclusion, no provider call during availability, startup without a key, single-route registration, and dashboard consumption.

External requests in adapter tests use an in-memory mock transport. No automated test calls a real or paid provider.

## 13. Security Considerations

- Secrets use `SecretStr` configuration and are absent from response schemas.
- The external client and authorization header exist only inside the configured adapter request boundary.
- Availability is configuration-derived and performs no external call.
- No unrestricted input or provider-generation API is exposed.
- No raw provider exception is exposed through the API.
- No dynamic evaluation, tools, browsing, file access, streaming, or agents exist.
- The fake provider is injectable for tests but cannot be selected through production configuration.
- Existing authentication protects the availability endpoint.

## 14. Explicitly Deferred

AI Coach chat, conversations, messages, context selection, prompt orchestration, output safety gates, memory, usage quotas, cost accounting, AI plan explanation, workout or nutrition changes, streaming, tools, function calling, browsing, files, agents, vector storage, frontend chat routes, and chat components are deferred to later approved sprints.
