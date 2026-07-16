# RAHFIT AI Workout Engine

## Purpose and boundary

The Workout Engine converts the canonical User Intelligence snapshot into an auditable,
owner-scoped plan. Python owns eligibility, exercise selection, frequency, recovery,
volume, prescriptions, validation, persistence, and adaptation. The existing legacy
workout endpoints and documents remain unchanged during this migration sprint.

## Architecture

`WorkoutService` is the application boundary. It obtains generation from
`WorkoutGenerator`, persists only through `WorkoutRepositoryProtocol`, and returns safe
schemas. `WorkoutGenerator` obtains the owner snapshot through
`UserIntelligenceService`, evaluates `ReadinessChecker`, creates constraints with
`WorkoutPlanner`, selects from `ExerciseCatalog` through `ExerciseSelector`, and passes
the completed plan through `WorkoutValidator` before it can be saved.

The catalog is versioned and immutable at runtime. Exercises declare movement pattern,
muscles, required equipment, location, difficulty, contraindications, injury exclusions,
pain exclusions, mobility requirements, chronic-condition exclusions, clearance needs,
default prescription, instructions, and safety notes. Selector
rejections carry stable reason codes so decisions can be tested and audited.

## Generation flow

1. Resolve the authenticated user's canonical profile and health profile.
2. Fail closed if readiness is incomplete or blocked.
3. Derive a deterministic plan type, safe frequency, recovery weekdays, duration, volume,
   repetition range, rest, and movement-pattern requirements.
4. Filter the approved catalog for equipment, location, experience, injury, pain,
   mobility, chronic-condition, duration, and duplication constraints.
5. Build warm-up, main, accessory, optional conditioning, and cooldown sections plus
   deterministic safety and progression text.
6. Validate ownership, catalog membership, schedule, duration, volume, and all health and
   environment constraints.
7. Optionally ask `AIService` for structured explanation only. Provider code is never
   imported by this domain. AI must echo the exact approved IDs and cannot change days, exercises,
   prescriptions, safety notes, or progression. Invalid or unavailable AI output falls
   back to the already validated deterministic plan.
8. Validate again, then persist a new active version while archiving the prior version.

Generation modes are `deterministic`, `ai_assisted`, and `deterministic_fallback`.
Fallback reason codes describe provider unavailability, provider validation failure, or
an exercise allow-list mismatch without exposing vendor errors.

Identical approved inputs and rule/catalog versions produce the same `generation_key`
and deterministic decisions. Entity IDs and timestamps remain unique per generation.

## Safety rules

- A complete profile and explicit health declaration are mandatory.
- Blocked readiness never reaches plan construction or a provider.
- Active injuries, reported pain, mobility limitations, and catalog contraindications
  exclude conflicting movements.
- Equipment, location, and experience level are allow-list constraints.
- Every day requires warm-up, main, and cooldown sections.
- User session duration, experience-based weekly volume, bounded sets/repetitions/rest,
  unique weekdays, and unique exercises per day are validated.
- Age group, clearance, maximum consecutive days, high-intensity exposure, exercise
  count, warm-up/cooldown duration, repeated loading patterns, and progression limits
  are enforced by centralized rules.
- Final catalog and health validation occurs before and after optional AI assistance.
- Plans carry stop-exercise and professional-guidance notices; they do not diagnose or
  prescribe medical treatment.

## Persistence and indexes

New documents use `intelligent_workout_plans` and `intelligent_workout_sessions` so the
new schema cannot corrupt the legacy `workout_plans` readers. Owner and ID are included
in every lookup. Index initialization creates one partial unique active plan per owner,
owner history, generation/version history, and owner-scoped session history/status
indexes. Unique `plan_id` and `session_id` indexes support stable external identifiers;
the active-plan index is partial and unique by owner.

Adoption requires running normal application index initialization. A future explicit
migration can map or retire legacy workout documents after API consumers move to the new
contract; no automatic data rewrite is performed.

## Progress and adaptation

Sessions record approved exercise IDs, set results, completion, duration, exertion,
skips, pain, and lifecycle timestamps. `WorkoutAdaptationEngine` deterministically
recommends maintaining, reducing intensity or volume, replacing exercise, adding
recovery, shortening a session, requiring review, maintaining the plan, or blocking
training. Each recommendation contains stable recommendation and reason codes, severity,
privacy-safe evidence, optional affected resource, and an automatic-application flag.
Health, pain, injury, and blocked-readiness recommendations are never auto-applied.

## Exercise catalog maintenance

Add exercises only through the typed catalog constructor. IDs must remain stable and
unique. Use existing goal, experience, equipment, muscle, and location vocabularies.
Every entry must include primary muscles, instructions, safety notes, valid set and
repetition defaults, operational requirements, and explicit safety exclusions. Tests
must prove catalog-wide movement-pattern coverage and reject duplicate or incomplete
entries. The competition catalog intentionally remains Python-owned rather than being
copied into MongoDB.

## Adding plan types

Add the plan type to `WorkoutPlanType`, map an existing `TrainingGoal` in the planner,
define deterministic day templates and prescriptions, and add validation and regression
tests. A new type is incomplete until it has equipment/location coverage, recovery
spacing, movement balance, duration bounds, safe fallback behavior, and documentation.

## Validation contract

Validation returns `valid`, `valid_with_warnings`, or `invalid`, plus separate structured
errors and warnings, stable validation codes, and non-sensitive metadata. Checks cover
ownership, catalog membership, equipment, location, difficulty, injuries, pain,
mobility, chronic conditions, clearance, duration, section completeness, repetitions,
rest, sets, weekly volume, recovery, high intensity, movement balance, duplicates,
alternatives, versions, statuses, and progression. Invalid plans never reach the
repository through `WorkoutService`.

## Authenticated API

The new contract is registered under `/api/v1/intelligent-workouts`. The legacy
`/api/v1/workouts` routes and documents remain unchanged. Every endpoint requires the
existing bearer authentication dependency, and every resource lookup includes the
authenticated owner. A resource owned by another user therefore has the same `404`
response as an unknown resource.

| Method | Path | Responsibility |
| --- | --- | --- |
| `POST` | `/plans/generate` | Generate, validate, persist, and activate a plan |
| `GET` | `/plans/active` | Return the owner's active plan |
| `GET` | `/plans` | List owned plan history with `limit` and `offset` |
| `GET` | `/plans/{plan_id}` | Return one owned plan |
| `POST` | `/plans/{plan_id}/activate` | Activate an archived owned plan |
| `POST` | `/plans/{plan_id}/archive` | Archive an active owned plan |
| `POST` | `/sessions` | Start or record progress for an active plan day |
| `GET` | `/sessions` | List owned sessions, optionally filtered by plan |
| `GET` | `/sessions/{session_id}` | Return one owned session |
| `PATCH` | `/sessions/{session_id}` | Update an in-progress session snapshot |
| `POST` | `/adaptation/analyze` | Return a deterministic, non-mutating recommendation |

List responses contain `items`, `limit`, `offset`, and `has_more`. Ordering uses time and
resource-ID tie-breakers. Page size is bounded to 100 and offset to 100,000. Request
models reject unknown fields and never accept ownership, computed completion, adaptation
flags, generation metadata, or timestamps. Response models omit owner IDs, health
records, prompt/context data, provider/model metadata, and internal diagnostics.

Example generation body:

```json
{"duration_weeks": 8, "use_ai_assistance": false}
```

Example session start body:

```json
{
  "plan_id": "<owned-plan-id>",
  "day_number": 1,
  "status": "in_progress",
  "completed_exercises": []
}
```

`PATCH /sessions/{session_id}` accepts a full progress snapshot for supplied mutable
fields. Exercise membership, set counts, completion percentage, skipped exercises, pain
flags, and terminal timestamps are recalculated by `WorkoutService`. Completed or
abandoned sessions cannot be reopened, and sessions can progress only while their plan
is active.

## Stable application errors

- `workout_profile_incomplete`
- `workout_health_profile_incomplete`
- `workout_readiness_blocked`
- `workout_generation_failed`
- `workout_validation_failed`
- `workout_plan_not_found`
- `workout_session_not_found`
- `workout_owner_mismatch`
- `workout_exercise_unavailable`
- `workout_active_plan_conflict`
- `workout_plan_archived`
- `workout_ai_enhancement_failed`

HTTP mappings use `404` for owner-scoped missing resources, `409` for prerequisites and
invalid lifecycle transitions, `403` for readiness or professional-clearance blocks,
`422` for unsafe/invalid constraints, and `503` for safe generation or persistence
failure. Validation errors use the application-wide `validation_error` contract. Error
messages and codes never contain health descriptions, prompts, provider responses,
secrets, tokens, or database details.

Additional API error codes are `workout_session_state_invalid`,
`workout_medical_clearance_required`, and `workout_persistence_failed`.

## Security and observability

All repositories are owner-scoped. Provider credentials and raw health notes are never
stored in plans or logged. Generation logs contain owner reference, plan ID, mode, and
stable generation key; provider telemetry remains in `AIService`. Do not log plan context,
health free text, secrets, or provider prompts.

AI assistance runs only through `AIService`, which builds purpose-minimized approved
context and applies the existing Safety Engine before `MockProvider`, Gemini, or a future
provider. The workout package has no direct provider or vendor SDK import. Raw provider
responses and prompts are not persisted.

## Replacement consistency

MongoDB document writes are atomic individually, but a standalone MongoDB deployment
cannot guarantee an atomic archive-and-insert plan replacement. The repository therefore
uses an explicit best-effort consistency boundary: it archives the current plan, inserts
the validated replacement, checks an ambiguous insert result by ID, and restores the
previous active plan when the replacement is known not to exist. Activation uses the
same compensating approach. A failed compensation returns the privacy-safe
`workout_persistence_failed` error without exposing database details.

This is not advertised as a database transaction. Under rare concurrent or ambiguous
network failures, manual reconciliation may still be required. Production deployments
should use a MongoDB replica set and transaction-capable unit of work, or migrate to a
single-document active-version head. Tests cover the deterministic compensation path.

## Verification

Run `pytest backend/tests/test_intelligent_workout_engine.py -q` for focused catalog,
selection, planning, generation, MockProvider fallback, validation, ownership, progress,
index, compensation, and adaptation coverage. Run
`pytest backend/tests/test_intelligent_workout_api.py -q` for authentication, routing,
ownership privacy, generation modes/failure, lifecycle, pagination, and safe response
contracts. Full release verification also runs Ruff, Black, strict mypy, the complete
backend suite, frontend checks, `git diff --check`, secret-pattern scanning, and
vendor-import isolation checks.

## Known limitations

The initial catalog is intentionally compact and English-only. It requires clinical and
exercise-science review before production use. AI assistance currently enhances only
explanation and uses safe fallback rather than plan composition. Offset pagination is
bounded and deterministic but should become cursor pagination at high scale. Replacement
compensation is not equivalent to a multi-document transaction. No frontend changes are
part of this sprint.
