# RAHFIT AI — AI Policy Layer

## Sprint scope

Sprint 2.3.5 introduces a dedicated, provider-neutral policy domain that answers one question: given a known AI capability and a requested action, is that action permitted? The layer is a pure deterministic Python service with no I/O dependencies.

This sprint does not build prompts, inspect prompt injection, evaluate runtime health or medical safety context, call an AI provider, access the database, use memory, expose a public endpoint, or add chat UI.

## Policy contract

The internal request contains exactly:

- one typed capability;
- one typed normal or forbidden requested action.

The result contains exactly:

- `decision`;
- `reason_code`.

Unknown enum values and extra request fields are rejected before policy evaluation. Decisions and reason codes are stable strings suitable for future orchestration and testing.

## Capabilities

| Capability | Primary permitted action | Decision |
|---|---|---|
| `explain_assessment` | `explain` | `allow` |
| `explain_workout` | `explain` | `allow` |
| `explain_nutrition` | `explain` | `allow` |
| `explain_progress` | `explain`, `summarize` | `allow` |
| `motivate` | `encourage` | `allow` |
| `summarize` | `summarize` | `allow` |
| `suggest_workout_alternative` | `recommend` | `allow_with_limits` |
| `suggest_nutrition_alternative` | `recommend` | `allow_with_limits` |

Read access is permitted only where needed to support the listed capability. An action absent from a capability allowlist is denied with `action_not_permitted_for_capability`.

## Allowed actions

- `read`: consume already approved application results required by the capability.
- `explain`: explain approved deterministic assessment, workout, nutrition, or progress information.
- `summarize`: summarize approved current information without changing it.
- `recommend`: select from approved alternatives only; it cannot create or apply unapproved plans.
- `encourage`: provide non-medical motivation without overriding safety restrictions.

`recommend` is deliberately limited for workout and nutrition alternatives. Future orchestration must use only alternatives supplied or supported by the deterministic engines.

## Forbidden actions

| Forbidden action | Decision | Stable reason code |
|---|---|---|
| `diagnose_medical_condition` | `professional_guidance_required` | `medical_diagnosis_requires_professional_guidance` |
| `prescribe_medication` | `deny` | `medication_prescription_forbidden` |
| `override_workout_engine` | `deny` | `workout_engine_override_forbidden` |
| `override_nutrition_engine` | `deny` | `nutrition_engine_override_forbidden` |
| `ignore_safety_restrictions` | `deny` | `safety_override_forbidden` |
| `reveal_system_prompt` | `deny` | `system_prompt_disclosure_forbidden` |
| `reveal_internal_context` | `deny` | `internal_context_disclosure_forbidden` |
| `reveal_secrets` | `deny` | `secret_disclosure_forbidden` |
| `access_database` | `deny` | `database_access_forbidden` |
| `execute_code` | `deny` | `code_execution_forbidden` |
| `internet_browsing` | `deny` | `internet_browsing_forbidden` |

Forbidden-action policy takes precedence over the selected capability. Medical diagnosis always requires professional guidance. All other listed forbidden actions are completely unsupported and denied.

## Decision types

- `allow`: the capability/action pair is permitted at the policy level.
- `allow_with_limits`: permitted only inside deterministic product-engine boundaries.
- `deny`: unsupported or explicitly forbidden.
- `professional_guidance_required`: the request belongs with a qualified professional rather than the AI product flow.

An `allow` decision is not final authorization to generate content. Future layers must still enforce authentication, context ownership, runtime safety, provider availability, and output validation.

## Architecture

`AIPolicyService` is a stateless synchronous evaluator. Capability rules and forbidden-action rules are explicit typed mappings. It has no constructor dependencies, performs no network or database work, and produces no side effects. It does not import the Context Builder, provider resolver, prompt infrastructure, or application repositories.

The policy layer has no public API route. A future trusted orchestrator may evaluate policy before requesting context and before any prompt or provider stage.

## Relationship with the future Safety Engine

The Policy Layer answers whether a capability/action category is generally permitted. A future Safety Engine will evaluate user-specific context, medical red flags, request content, and current restrictions. The responsibilities remain separate:

- Policy Layer: static capability and action permissions.
- Safety Engine: contextual safety eligibility and escalation.
- Context Builder: minimum-necessary approved user data.
- Future Prompt Builder: construction only after policy and safety approval.

The Safety Engine may make an allowed capability more restrictive. It may never turn a policy-level denial into an allowance.

## Testing

Automated tests cover every capability, every forbidden action, professional-guidance precedence across all capabilities, action/capability mismatches, unknown values, mass assignment, deterministic repeated evaluation, exact result fields, stable reason-code serialization, absence of public routes, and proof that evaluation invokes no provider or prompt behavior.

## Explicitly deferred

Prompt construction, system prompts, prompt-injection detection, contextual Safety Engine decisions, provider calls, generation, output validation, memory, database access, tools, browsing, streaming, public policy APIs, and chat UI are deferred.
