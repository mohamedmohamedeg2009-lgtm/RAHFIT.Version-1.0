# Deterministic AI Safety Engine

## Sprint Scope

Sprint 2.4B adds an internal, Python-owned pre-generation Safety Engine. It evaluates the trusted output of the Capability Classifier and Policy Layer against the approved structured context and normalized current user message. The engine decides whether a future orchestration layer may continue toward an AI provider.

This sprint does not construct prompts, call providers, generate responses, validate generated output, persist safety results, expose a public safety or message endpoint, implement memory, stream content, or add frontend AI Coach behavior.

## Deterministic Safety Philosophy

The same typed input produces the same decision when evaluated with the same injected clock. Rules are explicit, ordered, versioned, bilingual where message matching is required, and independent of an LLM or embedding model. Missing or inconsistent trusted input never defaults to `allow`.

Safety evaluation version: `rahfit-ai-safety-v1`.

## Internal Input Contract

The internal safety request contains only:

- Authenticated owner reference supplied by trusted application code.
- Normalized current user message.
- Typed Capability Classifier result.
- Typed Policy Layer result.
- Approved Context Builder result.
- Optional bounded runtime metadata such as request ID and locale.

The domain contract forbids extra fields. It does not accept public owner IDs, capability or policy overrides, arbitrary context sections, system prompts, credentials, database queries, provider options, or instructions to disable safety. The service independently verifies that the authenticated user, request owner, and approved-context owner match.

## Decision Types

| Decision | Provider eligible | Meaning |
| --- | --- | --- |
| `allow` | Yes | No deterministic rule prevents the supported request. |
| `allow_with_caution` | Yes | The request may continue, but future orchestration must preserve the returned caution. |
| `refuse` | No | A prohibited, dangerous, conflicting, or policy-denied request must stop. |
| `professional_guidance_required` | No | A qualified professional must handle the request; provider generation stops. |
| `fallback` | No | Input confidence, completeness, ownership, or integrity is insufficient for safe continuation. |

Provider eligibility is enforced by the result model and cannot contradict the final decision.

## Exact Decision Precedence

The lowest numbered matching group wins. Lower-priority caution or allow results cannot replace a stronger decision.

1. Prompt injection, secret extraction, explicit safety bypass, stop-status override, and prohibited technical actions.
2. Policy `deny`.
3. Policy professional-guidance decision, urgent symptoms, and authoritative assessment stop status.
4. Diagnosis, treatment, medication or dosage, drug or performance-enhancer, and strict minor supplement rules.
5. Existing injury, allergy, and dietary restriction conflicts.
6. Dangerous calorie restriction, fasting, eating-disorder-enabling behavior, extreme rapid weight loss, and aggressive minor dieting.
7. Dangerous workout duration, no-rest demands, excessive sessions or repetitions, severe-pain training, intentional injury, extreme heat or dehydration, and unsafe progression.
8. Unsupported capability, low classification confidence, or unavailable assessment safety context.
9. Policy `allow_with_limits`.
10. Low readiness, assessment caution, supplement education caution, or other approved-context caution.
11. Allow.

Integrity failures are evaluated before this table and return fail-closed `fallback` results.

## Policy Integration

The engine consumes the existing immutable Policy Layer result and does not reproduce its permission table.

- `deny` becomes `refuse` and cannot be upgraded.
- `professional_guidance_required` remains professional guidance.
- `allow_with_limits` becomes `allow_with_caution` unless a stronger rule matches.
- `allow` still requires all safety checks to pass.
- The policy reason code is retained in safe evaluation metadata.
- Allowed or limited policy reason codes must be compatible with the classified product capability; inconsistencies fail closed.

## Classifier Integration

The engine consumes the existing immutable classifier result.

- The eight product capabilities map directly to their existing Policy Layer capability enum.
- `medical_related` enters deterministic medical evaluation and cannot become normal allow.
- `unsupported` cannot reach a provider.
- Supported classifications below `0.80` confidence return `fallback`.
- The engine does not classify messages or duplicate the classifier rule catalog.

## Approved-Context Integration

The Context Builder remains the only source for user-specific safety data. The engine reads, but never mutates, approved sections. Safety evaluation uses the mandatory `safety` section and may approve capability-specific subsets of `request`, `profile`, `goals`, `assessment`, `workout`, `nutrition`, `progress`, and `preferences` for future orchestration.

Conversation data and unrelated sections remain blocked unless a later approved capability contract explicitly permits them. Missing safety sections, malformed safety fields, owner mismatch, unavailable assessment safety state, and missing restriction data for alternative requests return `fallback`.

## Prompt Injection and Extraction Detection

Bounded normalized phrase groups detect English, Arabic, and mixed-language attempts to:

- Ignore or replace system and safety instructions.
- Disable restrictions or request unrestricted/developer mode.
- Reveal prompts, hidden instructions, internal context, developer messages, secrets, tokens, API keys, or environment variables.
- Access databases, execute arbitrary code, invoke hidden tools, browse the internet, or jailbreak the system.

Detection uses fixed substring and token matching only; it uses no dynamic regular expressions, model calls, or embeddings. Stable safe rule identifiers are returned instead of hidden phrase lists. Explicit educational phrases about prompt-injection prevention are excluded from injection matching, although the classifier and policy may still reject them as outside product scope.

## Medical Safety

Urgent symptom groups include chest pain, severe breathing difficulty, fainting or loss of consciousness, stroke-like symptoms, severe allergic reaction, uncontrolled bleeding, and sudden severe neurological symptoms. These return `professional_guidance_required` and cannot proceed to a provider.

Diagnosis and treatment requests require professional guidance. Prescription, dosage, stopping or changing medication, and medication-combination instructions are refused. A general `medical_related` classification without a narrower match still requires professional guidance. The engine produces no diagnosis, treatment, rehabilitation plan, medication advice, or emergency message, and it does not change assessment safety state.

## Injury Restrictions

Confirmed injuries and workout restrictions come only from the approved safety context. Explicit attempts to ignore or override a named existing restriction are refused. Assessment `stop` remains authoritative, while lower-severity caution and low readiness produce caution when no stronger rule matches.

The current approved context exposes injury labels, not exercise-level contraindication records. The engine therefore does not invent a contraindication from an injury name. Approved alternative requests remain constrained by Policy Layer limits and require restriction context to be present.

## Allergy and Dietary Restrictions

Confirmed allergy conflicts and explicit attempts to ignore an existing allergy are refused. Existing dietary preferences use a small deterministic mapping for direct conflicts such as `no_pork`, `no_seafood`, vegetarian, and vegan restrictions. The engine does not infer allergies, invent substitutions, or calculate meals.

## Dangerous Nutrition Requests

Centralized competition-safe routing thresholds are safety guardrails, not medical diagnostic criteria:

| Rule | Threshold or behavior |
| --- | --- |
| Extreme daily calories | `≤ 800 kcal` → refuse |
| Low daily calories | `< 1,200 kcal` → professional guidance |
| Dangerous fasting | `≥ 48 hours` → refuse |
| Caution fasting | `≥ 24 hours` → caution |
| Extreme weight-loss rate | `≥ 5 kg/week` → refuse |
| Rapid weight-loss rate | `> 2 kg/week` → professional guidance |

Starvation, purging, self-induced vomiting, laxative misuse, deliberate dehydration, hiding disordered eating, and eliminating essential nutrition entirely are refused. Ambiguous aggressive dieting may receive caution. Aggressive dieting by a confirmed minor requires professional guidance.

## Dangerous Workout Requests

Centralized routing thresholds are:

| Rule | Threshold or behavior |
| --- | --- |
| Extreme daily training | `≥ 240 minutes/day` → refuse |
| Caution daily training | `≥ 180 minutes/day` → caution |
| Excessive daily sessions | `≥ 3 sessions/day` → refuse |
| Excessive repetitions | `≥ 1,000 repetitions` → refuse |
| Low readiness | `< 50/100` → caution |

No-rest demands, training through severe pain, intentional injury, extreme heat or dehydration, and explicit unsafe progression are refused. The engine does not modify a workout or calculate a new program.

## Drugs, Supplements, and Minor Handling

Prescription instructions, anabolic steroids, unsafe performance-enhancing drugs, controlled substances, and drug or supplement combinations for rapid results are refused. General non-dosage supplement education can continue only with caution. When approved context confirms minor status, supplement and aggressive-dieting requests require professional guidance. Normal safe explanation and motivation remain available for minors.

Age is never inferred from message wording. If approved minor status is unavailable, age-specific rules are not invented; the broader safety rules still apply.

## Findings and Warnings

Results contain typed findings and warnings with only:

- Stable category.
- Severity.
- Stable reason code.
- Source category.
- Optional non-sensitive scalar metadata such as a documented threshold.

They never include full messages, complete context, exact hidden detection phrases, secrets, prompts, credentials, or raw medical and dietary records. Only findings at or above the winning precedence are returned so a lower-priority caution does not confuse a refusal.

## Fail-Closed Behavior

The following conditions return `fallback` with provider eligibility disabled:

- Missing classifier, policy, or approved context.
- Owner or cross-user context mismatch.
- Message not normalized by the approved normalization contract.
- Classifier and policy incompatibility.
- Missing or malformed mandatory safety data.
- Missing required restriction context for an alternative capability.
- Low classifier confidence.
- Unexpected internal evaluation failure.

Typed domain validation rejects unknown enum values and extra override fields before service evaluation. Stack traces and sensitive input are not included in results.

## Privacy and Logging

Safe evaluation logs may contain owner reference, classified capability, policy decision, final safety decision, stable reason code, safe matched-rule identifiers, finding categories, and context version.

Logs never contain full user messages, full context, passwords, tokens, API keys, prompts, hidden phrases, complete conversations, or complete medical and nutrition data. The Safety Engine performs no network, database, repository, provider, or persistence operation.

## Testing Strategy

Automated tests cover:

- Every supported classifier capability and provider-eligibility mapping.
- Policy precedence and classifier compatibility.
- English, Arabic, and mixed-language injection and extraction attempts.
- Benign AI-safety discussion false-positive regression.
- Medical diagnosis, treatment, dosage, urgent symptoms, and general education distinction.
- Injury, allergy, dietary, dangerous dieting, eating-disorder, dangerous workout, drug, supplement, minor, readiness, and stop-status paths.
- Ownership isolation, context immutability, missing and malformed input, unknown enum rejection, logging privacy, and internal dependency failure.
- Absence of provider, network, prompt, persistence, and public endpoint behavior.
- Full existing backend and unchanged frontend regression suites.

## Explicitly Deferred

Post-generation output validation is intentionally deferred. Prompt construction, provider orchestration, response generation, memory, token and cost tracking, feedback, summarization, tools, streaming, and AI Coach UI are also outside Sprint 2.4B.

