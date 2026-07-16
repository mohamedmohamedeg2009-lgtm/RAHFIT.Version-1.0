# RAHFIT AI Workout Architecture

## 1. Scope

Sprint 3.4 introduces a deterministic workout-planning and workout-session capability. It consumes a completed smart assessment and produces an explainable plan without an AI model, randomness, nutrition behavior, coaching, reports, payments, or notifications.

The module follows the existing controller-service-repository architecture. Controllers own HTTP translation, services own business and safety decisions, repositories own persistence, and the React client only presents server decisions.

## 2. Domain Model

| Aggregate or value | Responsibility |
| --- | --- |
| `Exercise` | Versioned catalog definition with movement, muscles, equipment, difficulty, prescription ranges, tags, and contraindications. |
| `WorkoutPlan` | Immutable generated schedule tied to a user and assessment result. One plan is active per user. |
| `WorkoutDay` | Ordered training day with a split focus, duration, and prescribed exercises. |
| `WorkoutExercise` | Exercise snapshot and goal-specific prescription stored with the plan. |
| `WorkoutSession` | User-owned execution record for one plan day and calendar date. |
| `ExerciseProgress` | Completed-set or skipped state for a prescribed exercise. |
| `WorkoutProgress` | Derived session completion counters and percentage. |

Supported goals are fat loss, muscle gain, strength, general fitness, endurance, football performance, and goalkeeper performance. Supported experience levels are beginner, intermediate, and advanced. Training locations are commercial gym, home gym, and bodyweight-only.

## 3. Exercise Catalog

The catalog is defined independently from generation rules and is versioned at exercise level. Every entry includes:

- Stable identifier, name, description, version, and active state.
- Primary muscle groups, required equipment, movement type, exercise type, and compound/isolation classification.
- Difficulty and minimum supported experience.
- Recommended repetitions, sets, rest, and tempo.
- Contraindicated injury areas, conservative injury support, and goal/split tags.

Catalog changes must preserve identifiers used by stored plans. Removing an exercise means making a future catalog version inactive; it must not invalidate existing plan snapshots.

## 4. Deterministic Generation

Generation input is derived from the latest owner-scoped assessment plus the user's weekly availability and session duration. The generator calculates a stable SHA-256 generation key from normalized inputs. Repeating generation with unchanged inputs returns the current plan.

Split rules are fixed:

| Experience | Split |
| --- | --- |
| Beginner | Full body each available day |
| Intermediate | Alternating upper and lower body |
| Advanced | Repeating push, pull, and legs |

The generator filters by active catalog version, experience, split focus, available equipment, and injury contraindications. It then sorts candidates using deterministic goal relevance, experience proximity, movement type, and stable exercise identifier. Movement diversity is selected before any repeated movement type. Session duration controls exercise count; goal controls sets, reps, and rest.

Python is the sole decision owner. The browser cannot select exercises or bypass safety rules.

## 5. Safety Rules

- A completed assessment is required.
- A `STOP` assessment safety result blocks generation and returns a safety-specific error.
- Any exercise contraindicated for a reported injury is removed before selection.
- A plan is rejected when available equipment and safe exercises cannot create a complete session.
- Exercise progress cannot exceed prescribed sets.
- A session cannot complete until every exercise is completed or explicitly skipped.
- All plan and session reads are scoped by authenticated user ownership.

This module is fitness guidance, not diagnosis or medical treatment. Professional clearance remains required whenever the assessment safety engine indicates it.

## 6. API Contract

| Method and path | Purpose |
| --- | --- |
| `GET /api/v1/workouts/current` | Current active plan, today's deterministic day, and today's session if present. |
| `POST /api/v1/workouts/generate` | Generate or return an idempotent plan from the latest assessment. |
| `GET /api/v1/workouts/history` | Plan history and derived seven-day adherence. |
| `GET /api/v1/workouts/{plan_id}` | Owner-scoped plan details. |
| `POST /api/v1/workouts/{plan_id}/days/{day_id}/sessions/start` | Start or resume a session. |
| `PATCH /api/v1/workouts/sessions/{session_id}/exercises/{exercise_id}` | Record completed sets or skip state. |
| `POST /api/v1/workouts/sessions/{session_id}/complete` | Validate and finish a session. |

Errors use the existing structured API detail contract. Expected conflicts include missing assessment, safety restriction, insufficient safe exercise coverage, stale session revision, and incomplete session.

## 7. Persistence and Concurrency

Plans and sessions use separate collections. Indexes support one active plan per user, generation-key lookup, user history, session history, day/date lookup, and a unique in-progress session per user/plan/day. Session writes use optimistic revision matching so concurrent updates cannot silently overwrite progress.

Plan documents intentionally snapshot exercise prescriptions. This keeps historic plans reproducible when the exercise catalog evolves.

## 8. Dashboard Integration

The dashboard receives an optional workout state from the workout service. After a safe completed assessment:

- No active plan produces a `generate_workout` priority and action-required module state.
- An active plan produces a start or continue priority for today's workout.
- A completed or active session exposes real completion percentage and a direct destination route.
- A `STOP` assessment keeps workout planning locked.
- A workout source failure marks dashboard data partial rather than inventing progress.

## 9. Frontend Experience

Protected routes provide plan generation/current workout, full plan details, active session, and history. The client renders loading, empty, error, in-progress, skipped, and completed states. It uses the shared design system, responsive logical properties, keyboard-native controls, progress semantics, and application-level Arabic RTL/English LTR support.

No fake workout data is shipped in production. The frontend service translates the snake-case transport contract to camel-case presentation types.

## 10. Testing Strategy

Backend tests cover deterministic splits, repeatability, goal prescriptions, injury exclusion, equipment filtering, assessment and safety gates, session progress, completion validation, and adherence. Frontend tests verify the transport boundary, current-plan rendering, navigation, and session progress mutations. Full linting, formatting, static typing, unit tests, and production build remain release gates.

## 11. Known Boundaries

- The catalog is intentionally curated rather than externally administered in this sprint.
- Progression across plan versions and automatic deloading are future capabilities.
- Wearable ingestion, live timers, offline mutation queues, exercise media, coach overrides, AI recommendations, and nutrition coupling are outside Sprint 3.4.
- Weekly adherence is based on completed sessions in the latest seven-day window versus the current plan schedule.

## 12. Definition of Done

Sprint 3.4 is complete when the catalog and deterministic generator are versioned and tested; assessment, safety, equipment, and injury rules are enforced in Python; owner-scoped APIs and optimistic session updates pass checks; dashboard and protected workout screens use real data; documentation is current; and backend plus frontend verification commands pass.
