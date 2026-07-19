# RAHFIT AI — Intelligent Dashboard Architecture

**Sprint:** 3.3  
**Status:** Implemented  
**Scope:** Authenticated dashboard aggregation and presentation only.

## 1. Purpose

The Intelligent Dashboard is the authenticated user’s daily decision surface. It summarizes only state that RAHFIT currently owns, presents exactly one useful next action, and makes safety or missing-data constraints explicit. It does not generate workouts, nutrition plans, AI advice, health metrics, reports, or other future-module data.

The dashboard remains useful throughout the current lifecycle:

- Before assessment, it directs the user to start.
- During assessment, it restores the owned in-progress session.
- Under a deterministic `STOP`, it elevates safety above every product action and locks plan preparation.
- After a safe completion, it links to the real assessment result and identifies future modules honestly.
- During an optional aggregation failure, it preserves safe account actions and labels the response as partial.

## 2. Backend Aggregation Flow

`GET /api/v1/dashboard` is protected by the existing bearer-token dependency. The authenticated `User` is the sole ownership input; the endpoint never accepts a user identifier from the client.

The flow is:

1. Authentication resolves the active owner.
2. `DashboardService` requests the owner’s active assessment without creating a session.
3. If no active session exists, it requests the owner’s latest completed result.
4. The service derives the assessment view, real progress fields, feature availability, safety notice, and profile completeness.
5. Centralized deterministic rules select exactly one daily priority.
6. The controller serializes the immutable view through the stable dashboard response schema.

Assessment visibility, readiness, risk, and safety remain owned by the Assessment service. The Dashboard service consumes those results and does not duplicate their rule engines.

## 3. Deterministic Priority Rules

Rules are evaluated in strict precedence order.

| Precedence | Condition | Selected action | Reason |
| --- | --- | --- | --- |
| 1 | Optional assessment source unavailable | Refresh dashboard | A partial response must not imply that missing data is safe or complete. |
| 2 | Assessment safety is `STOP` | Review safety warning | Safety restrictions override onboarding and product actions. |
| 3 | No active or completed assessment | Start assessment | Assessment is the prerequisite for personalized planning. |
| 4 | An owned assessment is in progress | Resume assessment | Completing the saved assessment is the nearest valid next step. |
| 5 | Assessment completed and supported profile preferences are missing | Review profile setup | Missing preferences are shown explicitly without inventing values. |
| 6 | Assessment completed with no higher-priority restriction | View assessment summary | The real completed result is the current available outcome. |

React receives the selected action, explanation, severity, and valid destination. It never recomputes precedence or safety.

## 4. Response Sections

| Section | Responsibility |
| --- | --- |
| User | Derived display name, real primary goal when available, current units, assessment status, profile completeness, and missing preference fields. |
| Assessment | Lifecycle state, completion, readiness, risk, safety, missing categories, latest completion time, and 90-day reassessment indicator. |
| Daily priority | Exactly one deterministic action with title, description, route, reason, and severity. |
| Features | Assessment, workout, nutrition, AI Coach, progress, and reports expressed as `available`, `locked`, `coming_soon`, or `action_required`. |
| Safety notice | Returned only for `CAUTION` or `STOP`; states whether plan generation is blocked. |
| Progress | Assessment completion, profile completeness, latest real readiness score, and last assessment activity only. |
| Quick actions | Only actions valid for the current state; unavailable module routes are never emitted. |
| Metadata | Generation time, freshness, partial-data indicator, and contract version. |

No workout, nutrition, AI, body, adherence, or health value is synthesized in this sprint.

## 5. Feature Availability

Assessment is `action_required` until completion and `available` afterward. Workout, nutrition, AI Coach, and progress remain locked until the assessment prerequisite is satisfied, then become `coming_soon` because their modules are not implemented. Reports remain locked until sufficient real progress data exists. A `STOP` state locks all plan-related modules regardless of assessment completeness.

Only Assessment emits a destination route. Future modules have no links, preventing broken navigation and false affordances.

## 6. Partial Failure Strategy

Authentication and ownership failures are terminal and are never converted to partial success. Assessment aggregation is an optional dashboard source and is isolated behind a reader protocol.

If that source fails:

- The endpoint still returns HTTP success with an owner-safe shell.
- `partial_data` is `true` and freshness is `partial`.
- Assessment state becomes `unavailable` rather than `not_started`.
- The primary action becomes a refresh request.
- Internal exception details are not included.
- No safety-sensitive plan action is enabled.

The frontend announces partial data while retaining valid logout and retry behavior. A total endpoint or network failure renders a dedicated error state. An expired session follows the existing authentication recovery and logout boundary.

## 7. Frontend Structure

| Module | Responsibility |
| --- | --- |
| `DashboardPage` | Fetch lifecycle, retry, error selection, and composition. |
| `dashboardService` | Centralized authenticated request and transport-to-view mapping. |
| `DashboardHeader` | Greeting, account context, theme, locale, and logout controls. |
| `DailyPriorityCard` | Visually dominant backend-selected action and its explanation. |
| `SafetyNoticeCard` | Assertive `STOP` or polite `CAUTION` announcement. |
| `AssessmentSummaryCard` | Server-owned status, completeness, readiness, risk, and missing categories. |
| `FeatureStatusGrid` | Honest availability states and valid Assessment navigation only. |
| `ProgressSnapshotCard` | Real supported progress values and profile-data gaps. |
| `QuickActions` | Current valid navigation and logout. |
| `DashboardSkeleton` / `DashboardErrorState` | Explicit loading, unavailable, and session-expiry experiences. |

The `/app` route remains inside the existing `ProtectedRoute` and is lazy-loaded as its own production chunk.

## 8. Accessibility and Localization

- Semantic headings, landmarks, navigation, lists, progress elements, alerts, and status regions.
- `STOP` uses an assertive alert; partial data and non-blocking safety use status semantics.
- Native progress elements expose labels, minimum, maximum, and current values.
- All actions are keyboard operable with the shared visible focus treatment.
- Layout uses logical properties and supports English LTR and Arabic RTL.
- Static dashboard navigation, status, and control labels are localized; backend explanations remain authoritative.
- Color is never the only indicator of status.
- Mobile controls meet the existing design-system touch-target standard.
- Reduced-motion preferences inherit the application-wide motion override.

## 9. Caching Readiness

No cache or Redis dependency is introduced in Sprint 3.3. The service boundary is ready for a future private aggregate cache.

- Candidate key: `dashboard:v1:user:{user_id}:assessment:{assessment_revision}:profile:{profile_version}`.
- Safe duration: 30–60 seconds for non-safety presentation fragments.
- Required invalidation: assessment start, answer save, completion, safety change, profile preference change, logout/deactivation, and future plan/log/progress changes.
- Safety state must be invalidated immediately and must never be served from a stale cross-user fragment.
- Authentication tokens, passwords, private conversations, and raw sensitive assessment answers must never be cached in the dashboard aggregate.

## 10. Security and Ownership

The client cannot select a dashboard owner. Repository calls receive the authenticated user ID from the server dependency. The dashboard response excludes password hashes, tokens, raw assessment answers, and infrastructure errors. Existing authentication refresh and token invalidation behavior is preserved.

## 11. Future Extension Points

Future modules can add readers behind the aggregation boundary for real workout, nutrition, progress, AI availability, and reports state. Each source must provide explicit availability and freshness, fail independently when safe, and participate in cache invalidation. New actions must point to implemented protected routes before they can become available.

The dashboard contract is versioned so later additions can remain backward compatible. Existing deterministic safety and priority precedence must remain centralized in Python as sources are added.

## 12. Verification

Backend tests cover authentication, owner scoping, no-assessment, in-progress, completed-safe, `STOP`, missing-profile, reassessment, feature availability, partial fallback, priority selection, and stable response shape. Frontend tests mock the HTTP boundary and cover loading, success, start/resume/completed states, `STOP`, locked modules, partial data, backend failure, protected routing, navigation, and accessible status announcements.
