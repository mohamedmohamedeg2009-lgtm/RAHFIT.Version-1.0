# Intelligent Workout Frontend Integration

## Scope

The frontend integrates the authenticated `/api/v1/intelligent-workouts` API without duplicating workout, safety, readiness, completion, or adaptation logic. It coexists with the legacy `/api/v1/workouts` experience and does not mix identifiers or response models between the two contracts.

## Routes

| Route | Responsibility |
| --- | --- |
| `/intelligent-workouts` | Active-plan overview and setup entry point. |
| `/intelligent-workouts/setup/profile` | Canonical profile update required by generation. |
| `/intelligent-workouts/setup/health` | Explicit, privacy-aware health declaration. |
| `/intelligent-workouts/generate` | Plan generation preferences and result. |
| `/intelligent-workouts/plans/:planId` | Complete plan hierarchy, explanations, warnings, and lifecycle actions. |
| `/intelligent-workouts/plans/:planId/session/:dayNumber` | Start and record a plan-day session. |
| `/intelligent-workouts/sessions/:sessionId` | Resume or review an owner-scoped session. |
| `/intelligent-workouts/plans/:planId/adaptation` | Request and display non-mutating adaptation guidance. |
| `/intelligent-workouts/history/plans` | Paginated plan history. |
| `/intelligent-workouts/history/sessions` | Paginated session history. |

All routes are protected by the existing authentication boundary. The shared API client supplies the bearer access token and performs the existing refresh flow. Unknown and foreign resource identifiers receive the same safe not-found experience.

## Client architecture

`intelligentWorkoutService` is the single typed transport boundary for plans, sessions, adaptation, and required setup calls. It uses `apiRequest`; screens do not call `fetch` directly. Network state remains local to each route because no query-cache dependency exists in the current frontend. After lifecycle mutations, the affected server resource is fetched again.

Types mirror the published API contract in snake case to avoid lossy transformations. The client never sends owner IDs, calculated completion, timestamps, adaptation flags, provider metadata, prompts, or internal context.

## Error behavior

`workoutErrorMapper` maps stable backend codes to safe user actions:

- incomplete profile and health declarations link to the correct setup step;
- readiness and medical-clearance restrictions are shown without unsafe workarounds;
- archived plan, terminal session, active-plan conflict, and validation states retain their backend meaning;
- generation and persistence failures support deliberate retries;
- resource not-found responses never disclose ownership information.

The deterministic fallback generation mode is a successful result. The frontend explains the fallback and does not retry solely because AI assistance was unavailable.

## Session and adaptation rules

Session updates send a full progress snapshot. Users can record completed sets, repetitions, load, RPE, skips, pain, duration, and notes within API limits. The UI displays `completion_percentage` returned by the backend and does not calculate final completion or lifecycle eligibility.

Adaptation analysis is presented as guidance only. The client does not mutate a plan from `action`, even if a future response changes the automatic-application flag. Pain and safety notices never claim to diagnose a condition.

## Accessibility and responsive behavior

Semantic headings, fieldsets, legends, labels, live progress regions, keyboard-native controls, focus styles from the design system, and alert roles support WCAG-oriented operation. The layout reduces multi-column forms and set tracking to a single-column flow on small screens and inherits the application's RTL-aware logical spacing.

## Testing

Frontend tests cover the typed service contract and authorization header, ownership-safe errors, overview states, explicit profile and health setup, fallback generation, complete plan rendering, session snapshots, server-owned progress, and non-mutating adaptation results.

## Known integration constraint

The setup contract currently exposes `PUT /profile` and `PUT /health-profile` but no read endpoints. The frontend therefore does not claim to know stored setup completeness on page load. Generation errors remain the authoritative signal and route users to the required step. Prefilling previously saved sensitive values requires a future approved read contract.
