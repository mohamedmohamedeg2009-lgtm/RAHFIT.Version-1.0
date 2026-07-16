# AI Capability Classifier

## Purpose

The AI Capability Classifier is a deterministic orchestration component that maps the current user message to exactly one supported RAHFIT AI capability. It establishes intent before future policy, safety, prompt, and provider stages run.

The classifier does not generate content, make policy decisions, evaluate medical safety, call an AI provider, read stored context, or expose an API. Its only responsibility is classification.

## Supported Capabilities

| Capability | Meaning |
| --- | --- |
| `explain_assessment` | Explain the user's assessment or assessment result. |
| `explain_workout` | Explain an approved workout, exercise, or training plan. |
| `explain_nutrition` | Explain an approved nutrition plan, meal, or macro target. |
| `explain_progress` | Explain progress, trends, measurements, or goal status. |
| `motivate` | Provide encouragement within the supported coaching scope. |
| `summarize` | Summarize supported RAHFIT AI information. |
| `suggest_workout_alternative` | Identify a request for an alternative exercise or workout. |
| `suggest_nutrition_alternative` | Identify a request for an alternative meal or food. |
| `medical_related` | Identify medical or symptom-related content for mandatory downstream review. |
| `unsupported` | Stop requests that do not map to a supported capability. |

The eight product capabilities reuse the canonical capability values owned by the AI Policy Layer. `medical_related` and `unsupported` are classifier-specific routing outcomes; they do not expand Policy Layer permissions.

## Deterministic Priority

When one message matches more than one rule, the first matching category in this fixed order wins:

1. Medical-related content
2. Workout alternative
3. Nutrition alternative
4. Workout explanation
5. Nutrition explanation
6. Progress explanation
7. Assessment explanation
8. Summary
9. Motivation
10. Unsupported

Medical content therefore cannot be masked by a workout, nutrition, or motivation phrase. Alternative requests take precedence over general explanations, and ambiguous requests always produce the same result for the same normalized message.

## Message Normalization

Classification uses only the current user message. The normalization pipeline:

1. Applies Unicode compatibility normalization.
2. Uses language-neutral case folding.
3. Normalizes common Arabic letter variants.
4. Removes Arabic diacritics and tatweel.
5. Converts punctuation and symbols to spaces.
6. Collapses repeated whitespace.
7. Rejects empty or non-meaningful input.

English, Arabic, and mixed-language messages share the same rule evaluation path. Matching is based on normalized exact phrases, bounded phrases, and required keyword groups; it does not use random selection, an AI model, or mutable state.

## Classification Result

Each successful classification returns:

| Field | Contract |
| --- | --- |
| `capability` | Exactly one supported or special routing capability. |
| `confidence` | Deterministic value from `0.0` to `1.0`. |
| `matched_rules` | Stable, non-sensitive rule identifiers; never raw prompts, secrets, or internal context. |
| `reason_code` | Stable machine-readable explanation of the decision. |
| `requires_safety_review` | `true` for every supported or medical route; `false` only when processing stops as unsupported. |
| `unsupported_reason` | Present only for unsupported results. |

Confidence is evidence-based rather than probabilistic:

| Evidence | Confidence |
| --- | ---: |
| Exact normalized intent | `1.00` |
| Supported phrase within a larger message | `0.95` |
| All required intent/topic groups | `0.90` |
| Single unambiguous topic group | `0.75` |

Confidence does not grant permission and must not bypass future policy or safety checks.

## Unsupported Requests

Unsupported results are separated into stable reasons:

- `prohibited_technical_request`: code execution, hacking, database access, prompt disclosure, or secret disclosure requests.
- `unrelated_request`: explicitly unrelated requests such as creative-writing tasks.
- `no_supported_intent`: any other message without a supported capability.

Unsupported classification stops the future orchestration pipeline before safety, prompt, or provider stages.

## Architectural Boundaries

- The classifier is a stateless domain service with strongly typed input and output contracts.
- It imports no provider, prompt builder, safety engine, repository, database, or HTTP controller.
- It performs no I/O and makes no network calls.
- It does not read or mutate approved context, conversation history, or user data.
- It does not evaluate permissions; the existing AI Policy Layer remains authoritative for policy decisions.
- It does not generate a response or user-facing medical guidance.

These boundaries keep classification independently testable and prevent feature coupling.

## Future Safety Engine Integration

For a supported result, a future orchestrator will pass the classification to the Safety Engine before any prompt is assembled or provider is called. `medical_related` must always enter the strict medical-safety path. Other supported capabilities also set `requires_safety_review` so apparently benign messages cannot skip downstream safety controls.

The expected future sequence is:

`Current message → Capability Classifier → Policy Layer → Safety Engine → Prompt Builder → Provider`

The classifier does not implement or simulate any later stage in this sequence.

## Verification Expectations

The classifier is complete only when tests prove:

- Every supported capability has English and Arabic coverage.
- Mixed-language input is supported.
- Priority conflicts are deterministic.
- Unicode, punctuation, whitespace, and Arabic normalization are stable.
- Unsupported technical and unrelated requests stop safely.
- Confidence, matched-rule metadata, and reason codes are stable.
- Identical input produces identical output.
- No provider, prompt, context, safety, database, or public API behavior is introduced.

