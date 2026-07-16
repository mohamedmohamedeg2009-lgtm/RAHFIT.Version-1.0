# Intelligent Workout API Contract

## Scope and compatibility

This is the frontend integration contract for the authenticated Intelligent Workout API
under `/api/v1/intelligent-workouts`. It is separate from the legacy
`/api/v1/workouts` contract. Both remain registered; clients must not mix their schemas
or identifiers.

All workout business, safety, completion, lifecycle, and adaptation decisions remain
server-owned. The API uses JSON over HTTPS in deployed environments. Dates and timestamps
use ISO 8601; backend timestamps include a UTC offset, normally `Z` or `+00:00`.

## Authentication and prerequisites

Every endpoint requires `Authorization: Bearer <access-token>`. The token comes from the
normal `/api/v1/auth/register` or `/api/v1/auth/login` flow. Do not persist tokens in
application logs, analytics, URLs, or error reports.

Generation requires the authenticated owner to have both canonical records:

- `PUT /api/v1/profile` stores the strict `UserProfileData` request and returns `204`.
- `PUT /api/v1/health-profile` stores the explicit `HealthProfileUpdateRequest` and returns
  `204`. Empty arrays explicitly mean that the user declared no records in that category.
  Private free-text health notes are deliberately not accepted by this setup contract.

These setup endpoints derive ownership from the bearer token. They never accept a user
ID. Frontend health capture must use appropriate privacy messaging and must not mirror
payloads into telemetry.

## Endpoint table

| Method and path | Stable operation ID | Success | Purpose |
| --- | --- | --- | --- |
| `POST /plans/generate` | `intelligent_workouts_generate_plan` | `201` plan | Generate and activate a validated plan. |
| `GET /plans/active` | `intelligent_workouts_get_active_plan` | `200` plan | Get the owner's active plan. |
| `GET /plans` | `intelligent_workouts_list_plans` | `200` page | Get owner-scoped plan history. |
| `GET /plans/{plan_id}` | `intelligent_workouts_get_plan` | `200` plan | Get one owner-scoped plan. |
| `POST /plans/{plan_id}/activate` | `intelligent_workouts_activate_plan` | `200` plan | Activate an eligible plan. |
| `POST /plans/{plan_id}/archive` | `intelligent_workouts_archive_plan` | `200` status | Archive an active plan. |
| `POST /sessions` | `intelligent_workouts_create_session` | `201` session | Start or record an active-plan session. |
| `GET /sessions` | `intelligent_workouts_list_sessions` | `200` page | Get owner-scoped session history. |
| `GET /sessions/{session_id}` | `intelligent_workouts_get_session` | `200` session | Get one owner-scoped session. |
| `PATCH /sessions/{session_id}` | `intelligent_workouts_update_session` | `200` session | Record validated progress. |
| `POST /adaptation/analyze` | `intelligent_workouts_analyze_adaptation` | `200` recommendation | Analyze without mutating the plan. |

Foreign and unknown resource IDs intentionally return the same `404` response.

## TypeScript-friendly request shapes

```ts
type GenerationMode =
  | "deterministic"
  | "ai_assisted"
  | "deterministic_fallback";
type WorkoutStatus = "active" | "archived";
type SessionStatus = "in_progress" | "completed" | "abandoned";

interface GenerateWorkoutPlanRequest {
  duration_weeks?: number;       // integer, 4..12; default 8
  use_ai_assistance?: boolean;   // default false
}

interface CompletedSetInput {
  set_number: number;            // integer, 1..8
  actual_reps?: number | null;   // integer, 0..100
  actual_load_kg?: number | null;
  perceived_exertion?: number | null; // integer, 1..10
  completed: boolean;
}

interface CompletedExerciseInput {
  exercise_id: string;
  completed_sets: CompletedSetInput[];
  skipped?: boolean;
  pain_reported?: boolean;
  pain_area?: string | null;
}

interface CreateWorkoutSessionRequest {
  plan_id: string;
  day_number: number;
  status: SessionStatus;
  completed_exercises: CompletedExerciseInput[];
  actual_duration_minutes?: number | null;
  notes?: string | null;
}

interface UpdateWorkoutSessionRequest {
  status?: SessionStatus | null;
  completed_exercises?: CompletedExerciseInput[] | null;
  actual_duration_minutes?: number | null;
  notes?: string | null;
}

interface AnalyzeWorkoutAdaptationRequest {
  plan_id: string;
}
```

`PATCH` represents the supplied progress snapshot, not an instruction to increment
server values. At least one field is required. Send `completed_exercises` using only IDs
from the selected plan day. Do not calculate or send completion percentage, skipped IDs,
adaptation flags, or lifecycle timestamps.

## TypeScript-friendly response shapes

```ts
type ISODateTime = string;
type WorkoutPlanType =
  | "weight_loss" | "muscle_gain" | "general_fitness" | "strength"
  | "football_performance" | "goalkeeper_performance"
  | "home_workout" | "beginner_foundation";
type SectionType = "warmup" | "main" | "accessory" | "conditioning" | "cooldown";
type MovementPattern =
  | "squat" | "hinge" | "push" | "pull" | "lunge" | "carry"
  | "core" | "rotation" | "locomotion" | "mobility" | "conditioning";

interface SetPrescription {
  sets: number;
  min_reps: number;
  max_reps: number;
  rest_seconds: number;
  tempo: string;
  intensity_guidance: string;
  rpe_min: number;
  rpe_max: number;
  reps_in_reserve: number;
  duration_seconds: number | null;
  distance_meters: number | null;
  progression_limit_percentage: number;
}

interface PlannedExercise {
  exercise_id: string;
  exercise_name: string;
  movement_pattern: MovementPattern;
  primary_muscles: string[];
  equipment: string[];
  prescription: SetPrescription;
  estimated_duration_minutes: number;
  alternatives: string[];
  instructions: string[];
  safety_notes: string[];
}

interface WorkoutPlanResponse {
  plan_id: string;
  plan_type: WorkoutPlanType;
  status: WorkoutStatus;
  duration_weeks: number;
  training_days_per_week: number;
  weekly_schedule: Array<{
    day_number: number;
    weekday: number; // 1..7
    title: string;
    focus: string;
    estimated_duration_minutes: number;
    sections: Array<{ section_type: SectionType; exercises: PlannedExercise[] }>;
    recovery_notes: string[];
    warnings: WorkoutWarning[];
    high_intensity: boolean;
  }>;
  warnings: WorkoutWarning[];
  safety_notes: string[];
  progression_guidance: string[];
  explanation: {
    summary: string;
    rationale: string[];
    motivation: string;
    recovery_reminder: string;
  };
  generation_mode: GenerationMode;
  generated_at: ISODateTime;
  activated_at: ISODateTime | null;
  archived_at: ISODateTime | null;
  version: number;
}

interface WorkoutWarning {
  code: string;
  message: string;
  professional_guidance: boolean;
}

interface WorkoutSessionResponse {
  session_id: string;
  plan_id: string;
  workout_day_id: string;
  day_number: number;
  status: SessionStatus;
  completion_percentage: number;
  completed_exercises: CompletedExerciseInput[];
  skipped_exercise_ids: string[];
  adaptation_flags: string[];
  planned_duration_minutes: number;
  actual_duration_minutes: number | null;
  started_at: ISODateTime;
  completed_at: ISODateTime | null;
  updated_at: ISODateTime;
}

interface Page<T> {
  items: T[];
  limit: number;
  offset: number;
  has_more: boolean;
}

interface WorkoutAdaptationResponse {
  recommendation_code: string;
  action:
    | "reduce_volume" | "reduce_intensity" | "replace_exercise"
    | "add_recovery_day" | "shorten_session" | "maintain_plan"
    | "require_review" | "block_training";
  reason_code: string;
  severity: "info" | "caution" | "high" | "critical";
  evidence_summary: string[];
  automatic_application_allowed: boolean;
  affected_exercise_id: string | null;
  affected_day_number: number | null;
}
```

Plan and session list endpoints return `Page<WorkoutPlanResponse>` and
`Page<WorkoutSessionResponse>`. Query parameters are `limit=1..100`, `offset=0..100000`,
and optional `plan_id` for sessions.

## Lifecycle behavior

Plan lifecycle is `active → archived`; an eligible archived plan can be activated, which
archives the prior active plan. Only one active plan is allowed per owner. Replacement
uses best-effort compensation on standalone MongoDB and is not advertised as a
multi-document transaction.

Session lifecycle begins at `in_progress` and can terminate as `completed` or
`abandoned`. Terminal sessions cannot be reopened. Sessions can be changed only while
their plan is active. Pain input creates deterministic review flags; it does not diagnose
or mutate the plan.

Generation modes mean:

- `deterministic`: Python produced and validated the plan without provider assistance.
- `ai_assisted`: AI explained an already validated allow-listed plan through `AIService`.
- `deterministic_fallback`: assistance was requested but unavailable, unsafe, or invalid;
  the valid deterministic plan was returned successfully.

The frontend must treat all three modes as successful plans. It must not retry solely
because fallback was used.

Adaptation returns a recommendation only. The frontend must never apply it as a plan
mutation, regardless of `action`; `automatic_application_allowed` is currently false.

## Error contract

```ts
interface ErrorResponse {
  code: string;
  message: string;
  details?: Array<Record<string, unknown>> | null;
  request_id?: string | null;
}
```

| HTTP | Representative stable codes | Frontend behavior |
| --- | --- | --- |
| `401` | Authentication handler | Refresh/re-authenticate; do not reveal credentials. |
| `403` | `workout_readiness_blocked`, `workout_medical_clearance_required` | Show the safe restriction and guidance path. |
| `404` | `workout_plan_not_found`, `workout_session_not_found` | Treat unknown and foreign resources identically. |
| `409` | `workout_profile_incomplete`, `workout_health_profile_incomplete`, `workout_plan_archived`, `workout_session_state_invalid`, `workout_active_plan_conflict` | Refresh state or navigate to the required setup. |
| `422` | `validation_error`, `workout_validation_failed`, `workout_exercise_unavailable` | Bind safe validation details; never infer business state. |
| `500` | `internal_error`, `workout_error` | Show a generic retry message and retain request ID. |
| `503` | `workout_generation_failed`, `workout_persistence_failed` | Retry later; do not assume a write committed. |

## Fields clients must not send or assume

Never send `_id`, `user_id`, `owner_id`, `generation_metadata`, `completion_percentage`,
`skipped_exercise_ids`, `adaptation_flags`, timestamps, version overrides, provider,
model, prompt, raw context, secrets, or internal validation metadata.

Never assume provider/model fields, internal generation keys, health notes, owner IDs,
MongoDB IDs, raw AI output, or unlisted response properties exist. Do not derive a new
plan from explanations or adaptation text. OpenAPI is authoritative for nullability and
required fields.

## Repeatable smoke test

The CLI uses only the configured API server and normal production endpoints. It does not
require Gemini and never prints tokens, passwords, or health payloads.

PowerShell:

```powershell
$env:RAHFIT_API_BASE_URL = "http://127.0.0.1:8000"
$env:RAHFIT_SMOKE_EMAIL = "<dedicated-primary-test-email>"
$env:RAHFIT_SMOKE_PASSWORD = "<dedicated-primary-test-password>"
$env:RAHFIT_SMOKE_SECONDARY_EMAIL = "<dedicated-secondary-test-email>"
$env:RAHFIT_SMOKE_SECONDARY_PASSWORD = "<dedicated-secondary-test-password>"
backend\.venv\Scripts\python.exe backend\scripts\smoke_intelligent_workout.py
```

The accounts must be dedicated test accounts. The script reuses them through login when
registration reports a duplicate. It creates or replaces their canonical setup, creates
a plan/session, validates cross-user isolation and adaptation, completes the session, and
archives the plan.

### Local standalone MongoDB

Start the normal local standalone database and API using the project `.env`, with AI
disabled or without a Gemini key. Run the PowerShell command above. Plan replacement is
validated through its documented compensating behavior; the command does not claim
transactional atomicity.

### Replica set or staging

Point the API deployment's `MONGODB_URI` at the authorized replica set/staging database,
start that API, set `RAHFIT_API_BASE_URL` to its HTTPS URL, and use dedicated non-production
test accounts. The same command verifies the public contract. Destructive production
credentials and databases must never be used. The optional transactional replacement
test remains a future deployment-specific check because the current repository uses
document operations plus compensation rather than a MongoDB transaction.

## Python compatibility

Python 3.12 is canonical through `.python-version`, CI, Ruff, Black, mypy, and setup
documentation. Run the full compatibility gate in a Python 3.12 environment:

```powershell
py -3.12 -m venv backend\.venv312
backend\.venv312\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
backend\.venv312\Scripts\python.exe -m ruff check backend
backend\.venv312\Scripts\python.exe -m black --check backend
backend\.venv312\Scripts\python.exe -m mypy backend\app
backend\.venv312\Scripts\python.exe -m pytest -q
```
