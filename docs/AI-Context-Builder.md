# RAHFIT AI — Approved AI Context Builder

## Sprint scope

Sprint 2.3 implements an internal, provider-neutral Context Builder for future AI Coach safety and orchestration stages. It selects structured, minimum-necessary facts from existing owner-scoped application services. It does not create prompts, call providers, generate output, classify capabilities, persist context, expose a context endpoint, or modify plans.

## Bounded-context philosophy

Python owns source selection, purpose minimization, ownership checks, ordering, truncation, omission tracking, and hard serialized-size enforcement. The result is structured application data rather than an unstructured prompt. Existing deterministic services remain authoritative for assessment safety, readiness, workout planning, nutrition planning, and progress.

The builder reads the latest completed assessment first because its deterministic safety status is required. Optional product sources are loaded only when the selected purpose needs them. Missing optional plans produce explicit omissions rather than misleading substitutes.

## Context version

Every result uses the stable version `rahfit-ai-context-v1`. The result contains the authenticated owner reference, purpose, ordered sections, inclusion and omission records, build metadata, generation timestamp, and deterministic serialized-size metadata.

## Supported purposes

| Purpose | Minimum approved context |
|---|---|
| `explain_assessment` | Safety, request, goals, latest assessment, minimal profile |
| `explain_workout_plan` | Safety, request, goals, active workout, relevant assessment/profile, current workout progress |
| `explain_nutrition_plan` | Safety, request, goals, active nutrition plan, relevant assessment/profile, current nutrition progress |
| `general_fitness_question` | Safety, request, goals, experience/equipment profile |
| `general_nutrition_question` | Safety, request, goals, nutrition targets/restrictions, relevant metrics |
| `safe_motivation` | Safety, optional request, goals, current approved progress, stored preferences |
| `summarize_current_plan` | Safety, optional request, goals, active workout/nutrition summaries and current statuses |
| `clarify_recommendation` | Safety, request, goals, and exactly one trusted assessment/workout/nutrition recommendation source |
| `suggest_approved_workout_alternative` | Safety, request, goals, equipment/injuries and bounded active workout items |
| `suggest_approved_nutrition_alternative` | Safety, request, goals, allergies/preferences, targets and bounded approved meal foods |

Unknown purposes and arbitrary source selection are rejected. Clarification requires a typed recommendation source; other purposes cannot supply one.

## Approved data sources

The builder accepts constructor-injected, owner-scoped readers compatible with existing services:

- authenticated `User`, selecting only explicitly approved fields;
- latest completed `AssessmentResult` through `AssessmentService`;
- current workout state through `WorkoutService`;
- current nutrition state through `NutritionService`;
- bounded owned conversation detail through `AIConversationService`.

The builder does not query MongoDB directly and does not recalculate any safety, readiness, workout, nutrition, or progress result. Current workout and nutrition status are the only progress sources presently implemented; no unsupported longitudinal measurements or memories are inferred.

## Forbidden data

Serialized context excludes password hashes, passwords, email addresses, access and refresh tokens, reset or verification tokens, provider/API credentials, authorization headers, audit data, complete database documents, MongoDB metadata, generation keys, assessment/session/plan IDs when not required, hidden instructions, prompts, provider requests/responses, deleted data, administrator metadata, and unsupported medical inferences.

The internal owner reference is included solely to preserve the trusted build identity. Request models forbid extra fields and never accept an owner ID, arbitrary field list, raw source query, override data, or system instruction.

## Ownership model

`build_context(authenticated_user, request)` receives the user from trusted authentication. Every source call uses that identity. Returned assessment, workout, nutrition, session, and conversation ownership is checked again at the builder boundary. Any owner mismatch fails the entire build. Missing and unauthorized requested conversations use the same safe error and deleted conversations/messages are excluded.

## Section priority

The deterministic order is:

1. `safety`
2. `request`
3. `goals`
4. `workout` and `nutrition`
5. `assessment` and `profile`
6. `progress`
7. `preferences`
8. `conversation`

Safety is mandatory. A supplied current question is isolated in its own section and marked as untrusted plain text. Lower-priority sections are removed before higher-priority sections when the hard limit is reached. Mandatory safety and request overflow fails closed.

## Purpose-based minimization

Each purpose maps to an allowlist of sections. The builder loads only sources required by that allowlist. For example, a general fitness question does not read active product plans; workout explanation does not read nutrition; nutrition explanation does not read workout. Conversation context is excluded by default even when a conversation ID exists.

The builder transports existing restrictions and approved alternatives represented in deterministic plans. It never invents exercises, foods, meals, medical facts, or historical progress.

## Size limits

Competition-ready centralized defaults are:

- 1,000 current-question characters;
- 12,000 bytes for the complete serialized context result;
- 8 recent conversation messages and 2,000 combined conversation characters;
- 7 progress records;
- 8 workout items;
- 8 nutrition items;
- 3 preference fields;
- 6 deterministic safety explanations;
- 500 characters for an individual transported text field.

No provider tokenizer is used. JSON is measured as UTF-8 with deterministic serialization. The final reported size equals the complete serialized result size and never exceeds the configured maximum.

## Truncation and omission behavior

Source lists are bounded before assembly. Conversation trimming removes the oldest low-priority messages first and truncates a remaining oversized message only when necessary. Workout, nutrition, progress, preference, safety-explanation, and conversation truncation is recorded on the section and in build metadata.

If the assembled result remains too large, complete optional sections are omitted from priority 8 upward. Each omission includes a stable reason code: purpose minimization, not requested, purpose not approved, source missing, source unavailable, no approved data, or hard size limit. Safety is never removed to preserve optional data.

## Conversation-history limits

Conversation history is used only when a trusted caller explicitly requests it and the purpose is one of general fitness, general nutrition, safe motivation, or recommendation clarification. Retrieval is owner-scoped through the conversation service. Only `user`, `assistant`, and `system_notice` message data already validated by the conversation domain is transported. Output contains role and bounded plain-text content only, in chronological order, with no IDs, timestamps, provider metadata, prompts, deleted messages, or full historical dump.

## Explainability metadata

Internal metadata records the context version, purpose, included sections, omitted sections, truncated sections, source categories used, build timestamp, complete serialized size, configured maximum, question length, and bounded conversation counts. Inclusion and omission reasons contain no raw sensitive data.

## Source-failure behavior

- A missing completed assessment produces explicit `not_assessed` safety context and limits personalization.
- An assessment dependency failure stops the build with a stable required-source error because safety cannot be trusted.
- Missing optional workout or nutrition plans produce `source_missing` omissions.
- Optional dependency failures produce `source_unavailable` omissions.
- Explicitly requested missing, deleted, or unauthorized conversation context fails with the same safe resource error.
- Any source returning another user's data fails closed as an ownership error.

No fallback substitutes another user's data or guesses unavailable context.

## Privacy and logging

The Context Builder has no logging of question text, message content, complete context, profile, or assessment data. Future operational logs may contain only owner reference, purpose, safe conversation ID, section names, size, latency, and stable error category. Context is returned in memory to its trusted caller and is not automatically stored.

Question input is whitespace-normalized, length-bounded, rejected when required but empty, and rejected when it contains HTML/script-like markup. It remains isolated as untrusted text. Prompt-injection classification is intentionally deferred.

## Testing strategy

Automated tests cover every purpose, invalid purpose/options, owner derivation, cross-user failures for every source, latest assessment safety/readiness transport, missing and failed sources, purpose source minimization, question validation, forbidden-field regression, plan summaries, progress/preferences limits, conversation ownership/deletion/order/bounds, priority pressure, mandatory overflow, exact serialized size, metadata, deterministic repeated builds, provider/network non-use, non-persistence, and sensitive-log absence. The full product regression suite remains required.

## Explicitly deferred

Capability classification, safety decisions, prompt construction, hidden/system prompts, provider selection and calls, response generation, prompt-injection detection, post-generation validation, governed memory, summarization, token/cost tracking, feedback, streaming, tools, internet access, autonomous agents, plan mutation, computer vision, public context inspection, and frontend AI Coach UI are deferred to separately approved sprints.
