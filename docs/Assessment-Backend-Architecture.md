# RAHFIT AI — Assessment Backend Architecture

**Sprint:** 3.2.2  
**Status:** Implemented adaptive assessment engine  
**Scope:** Smart Assessment lifecycle only; no plan generation, AI, dashboard, nutrition, workout, report, notification, payment, or frontend behavior.

## 1. Architecture

The Assessment Engine follows the existing controller → service → repository → MongoDB boundaries. Controllers authenticate, validate transport data, delegate, and translate domain failures into safe API responses. The service owns lifecycle, ownership, branching, validation, completion, and deterministic result generation. The repository owns MongoDB queries, optimistic concurrency, indexes, and atomic completion persistence.

Assessment answers use structured values and are never interpreted as MongoDB query expressions. Resource lookup always includes the authenticated user identifier, so a record owned by another user is returned as unavailable rather than revealing its existence.

## 2. Collections

### `assessment_questions`

Stores the governed, versioned question catalogue. Each document contains a stable question identifier, category, presentation metadata, type, requiredness, constraints, choices, dependency/visibility rules, display order, version, and active state.

The unique `(version, question_id)` index prevents duplicate definitions. The `(version, active, display_order)` index supports ordered catalogue reads. Published versions should be treated as immutable; corrections should publish a new version.

### `assessment_sessions`

Stores one user-owned assessment attempt. Answers are embedded as a map keyed by question identifier. This structure gives each question at most one current answer and makes replacing an answer atomic. A revision counter protects against lost concurrent updates.

Only one `in_progress` session is permitted per user through a partial unique index. Completed sessions remain historical evidence and are not overwritten. Parent-answer changes remove answers from branches that are no longer visible.

### `assessment_results`

Stores the immutable, deterministic profile snapshot produced from a completed session. It records the source session, user, assessment version, answered question identifiers, completed categories, normalized answers grouped by category, generation time, and completion state.

The session identifier is unique, making completion idempotent. `(user_id, generated_at)` supports the latest-result read. Session completion and result insertion execute in one MongoDB transaction.

## 3. Assessment Flow

1. An authenticated user requests the active question catalogue or starts an assessment.
2. The service resumes the user's existing active session or creates one against an active question version.
3. Each answer is checked for ownership, session state, question visibility, type, range, format, and allowed choices.
4. Saving replaces the question's prior value and invalidates answers from newly hidden dependent branches.
5. The service returns the next unanswered visible question.
6. Completion recalculates the visible path and rejects missing required answers.
7. Deterministic consistency and safety engines validate the completed branch.
8. A `STOP` safety outcome blocks completion; otherwise readiness, risk, and summary data are generated.
9. MongoDB atomically marks the session completed and stores its versioned result.
10. Downstream modules may later consume the latest completed result, but none are implemented in this sprint.

## 4. Service Responsibilities

| Service operation | Responsibility |
| --- | --- |
| Get questions | Resolve and return an active, ordered question version. |
| Start assessment | Resume the existing active session or create exactly one new session. |
| Resume assessment | Validate owner and in-progress state, then restore next-question context. |
| Save answer | Enforce ownership, visibility, type and metadata rules; replace duplicates and invalidate hidden branches. |
| Validate answer | Apply deterministic validation for every supported question type. |
| Get next question | Select the highest-priority visible unanswered question using deterministic branch rules. |
| Finish assessment | Require visible mandatory answers, enforce consistency and safety, and coordinate atomic completion. |
| Generate result | Create deterministic risk, readiness, summary, and immutable profile data without AI. |
| Get latest assessment | Return only the authenticated user's latest completed result. |

## 5. Validation

Supported question types are text, textarea, number, integer, boolean, single choice, multiple choice, date, height, weight, time, and slider.

Validation includes:

- Pydantic request and model validation.
- Required-answer enforcement against the current visible branch.
- Integer and numeric type enforcement that rejects booleans as numbers.
- Minimum and maximum numeric bounds.
- ISO date and 24-hour time parsing.
- Single- and multiple-choice allowlists.
- Duplicate-choice and duplicate-answer prevention.
- String length and pattern rules.
- Dependency and visibility-rule enforcement.
- Optimistic revision checks for concurrent writes.
- Owner-scoped session and result access.
- Lifecycle checks that block writes after completion.

All client-facing failures use safe, stable assessment error codes. Internal exceptions and database details are not returned.

## 6. REST API

All endpoints require a valid access token.

| Method and path | Purpose |
| --- | --- |
| `GET /api/v1/assessments/questions` | Get the latest or requested active question version. |
| `POST /api/v1/assessments/start` | Start a session or resume the user's active session. |
| `POST /api/v1/assessments/{session_id}/answer` | Validate and save one answer. |
| `POST /api/v1/assessments/{session_id}/finish` | Validate and complete the assessment. |
| `GET /api/v1/assessments/latest` | Get the user's latest completed result. |
| `GET /api/v1/assessments/sessions/{session_id}` | Get one owned session and its next question. |
| `POST /api/v1/assessments/sessions/{session_id}/resume` | Resume one owned in-progress session. |

OpenAPI documents authentication, summaries, request and response contracts, validation constraints, and expected conflict/not-found outcomes.

## 7. Security and Privacy

- Authentication is mandatory for every route.
- Session and result lookups are constrained by authenticated `user_id`.
- Cross-user access is intentionally indistinguishable from a missing resource.
- The controller never accepts an owner identifier from request data.
- Question identifiers are restricted to safe lowercase keys before use in MongoDB update paths.
- Errors omit stack traces, database messages, and hidden resource identifiers.
- Assessment content must not be written to application logs or analytics events.
- MongoDB encryption, backup, retention, export, and deletion controls remain governed by the enterprise database blueprint.

## 8. Operational Requirements

The built-in versioned catalogue is provisioned idempotently during application startup. Existing documents are not overwritten, allowing deployment-specific configuration to remain authoritative. At least one active, internally consistent version is required. Completion transactions require MongoDB configured as a replica set or managed cluster with transaction support.

Deployment validation should verify question identifiers, dependency targets, dependency ordering, rule patterns, category coverage, and absence of circular dependencies before publishing a question version.

## 9. Adaptive Branching

The adaptive branching engine evaluates question metadata rather than controller conditionals. A question may declare one or more visibility conditions and zero or more priority conditions. Visibility conditions use logical `AND`; an unanswered dependency is not treated as satisfied.

Supported operators are equality, inequality, membership, containment, and numeric less-than/greater-than comparisons with inclusive variants. Visible questions are sorted by deterministic effective priority and then stable display order and identifier. There is no random selection.

The current catalogue implements these governed branches:

- Male-specific context appears only after the corresponding user-provided gender answer.
- Advanced programming appears only for advanced users aged at least 16; beginners and younger users do not receive it.
- Fat-loss selection moves the nutrition question earlier and reveals target-weight context.
- Knee selection reveals knee-specific limitation details.
- Home training reveals home equipment and hides commercial gym equipment; the reverse applies outside home training.
- Football and goalkeeper questions appear only when their parent sport and position answers apply.

Changing an earlier answer resets stored answers that directly depend on it and recursively removes descendants. Catalogue validation rejects missing dependencies, mixed versions, duplicate question identifiers, self-dependencies, and dependency cycles before a version is used.

## 10. Safety Rules

The dedicated safety engine receives only validated session answers and applies ordered, immutable Python rules. Every triggered rule returns an identifier, `SAFE`, `CAUTION`, or `STOP`, a risk level, and a fixed user-safe explanation.

Chest pain, unexplained loss of consciousness, medical red flags, recent surgery, heart disease, uncontrolled hypertension, severe dizziness, and serious injury produce `STOP`. Pregnancy and a non-serious reported injury produce `CAUTION`. Multiple triggers are retained in declaration order while the most restrictive status controls the outcome.

`STOP` prevents session completion and leaves the session in progress. The API returns `safety_restricted` without exposing private answers or internal implementation details. No AI model evaluates, overrides, or explains safety decisions.

## 11. Risk Classification

Risk is classified as `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`. No triggered rule produces `LOW`; caution conditions produce at least `MEDIUM`; serious clearance conditions produce `HIGH`; chest pain, loss of consciousness, and general medical red flags produce `CRITICAL`. When multiple rules trigger, the highest risk is retained and every deterministic explanation is returned.

Risk classification is a product safety disposition, not a diagnosis. It does not estimate disease probability and cannot be downgraded by preferences, question priority, or future AI output.

## 12. Readiness Score

Assessment completeness is the percentage of currently visible questions with non-empty answers. Missing categories include a visible category with an unanswered required question or no answered question. Because a new answer may reveal a new branch, completeness may decrease temporarily as relevant questions are added.

Readiness is an integer from 0 to 100. It starts from completeness and applies a transparent risk deduction: none for `LOW`, 15 points for `MEDIUM`, 35 points for `HIGH`, and a zero score for `CRITICAL` or `STOP`. A completed `CAUTION` assessment can therefore be usable only within its stated restrictions. Session responses expose live completeness, readiness, missing categories, and safety state; completed results persist the same values.

## 13. Deterministic Assessment Summary

Completed results include fixed-template sections for goals, lifestyle, medical considerations, training readiness, equipment, and experience. Summary text is assembled only from validated answers and safety outcomes. It contains no generative AI language and makes no medical or performance claim.

## 14. Future Extension

Future sprints may add assessment modes, safety/readiness rules, reassessment and supersession, expiry policies, consent-aware sensitive sections, localization, administrative catalogue publishing, and domain events. These extensions must preserve version immutability, user ownership, deterministic Python authority, and historical interpretability.

Workout, nutrition, AI Coach, dashboards, reports, notifications, payments, and frontend assessment screens are deliberately outside Sprint 3.2.2.
