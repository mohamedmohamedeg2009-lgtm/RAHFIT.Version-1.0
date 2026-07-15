# RAHFIT AI — Enterprise API Blueprint

**Status:** Official Sprint 2.5 pre-implementation specification  
**Scope:** REST interface contracts, security, operations, and test requirements only. This document contains no implementation, route files, models, schemas, or code.

## 1. API Philosophy

REST is appropriate because RAHFIT AI exposes stable, resource-centred operations to a web client and future mobile/partner clients. It maps naturally to user-owned profiles, versioned assessments, plans, logs, reports, notifications, and administrative resources. Long-running work is represented as an accepted operation with a status resource rather than holding a request open.

The platform is API-first: each user-visible capability has a documented contract, ownership rule, lifecycle, validation boundary, error behaviour, and observability expectation before implementation. Controllers translate HTTP concerns only. Python services orchestrate use cases; domain rules own safety, state transitions, calculations, and business invariants; repositories isolate persistence access. No controller or client is authoritative for permissions, safety, calculations, or AI decisions.

The public contract is backward compatible within a major version. Additive fields and optional capabilities are preferred; removing or changing meaning requires a deprecation notice, migration period, successor contract, and version strategy. The initial base is `/api/v1`; a new major path is used only for incompatible public changes. Requests are stateless: all required authentication, idempotency, and resource references travel with the request, while durable state remains in governed backend records.

Idempotency is required for creation, completion, generation, upload finalisation, payment-adjacent, and other retry-prone actions. Consistency is explicit: immediate operations return current state; background work returns accepted status and a retrievable outcome. Security is default-deny, owner-scoped, and safety-aware. The competition API builds a coherent vertical slice; enterprise tenancy, payments, marketplace, vision, wearables, and broad administration remain future contracts.

## 2. API Conventions

| Convention | Specification |
| --- | --- |
| Base path and version | All public endpoints begin `/api/v1`. The version is path-based and changes only for breaking contracts. |
| Resource naming | Lowercase plural nouns, hyphenated only where clarity requires. Resource identity appears in the path; actions are narrowly used for state transitions or commands. |
| HTTP methods | `GET` reads; `POST` creates or starts a command; `PATCH` changes permitted fields/state; `DELETE` removes or requests removal. `PUT` is reserved for complete replacement only when explicitly documented. |
| Status codes | Use standard success, validation, authentication, authorisation, conflict, rate-limit, and server-failure semantics. Accepted work returns an operation/status reference. |
| Date/time | ISO 8601 UTC timestamps in responses. Clients submit offset-aware timestamps where an event time is supplied; user timezone controls presentation, not stored truth. |
| Pagination | Cursor pagination for collections: a bounded `limit`, opaque `cursor`, and metadata describing next/previous availability. Offset pagination is not used for growing private logs. |
| Sorting/filtering/search | Explicit allowlisted `sort`, `filter`, and `q` parameters only. Unsupported fields fail validation; search is scoped to authorised, non-sensitive fields. |
| Request/correlation IDs | Server issues a `request_id` for every request; clients may supply a correlation identifier for a multi-step flow, which is validated and propagated. |
| Idempotency keys | Client supplies a unique idempotency key for documented retry-prone commands. Same actor/key/payload returns the original outcome; same key with different payload is a conflict. |
| Content types | JSON is used for ordinary requests/responses. Multipart upload is used only for approved file endpoints. Content negotiation defaults to JSON. |
| File uploads | Metadata, type/size validation, ownership, scan status, and storage references are controlled; clients never choose storage paths. |
| Localisation | `Accept-Language` selects supported response language. User preference takes precedence when policy permits. User-generated content is not automatically translated without consent. |
| Timezone | A validated timezone header or current profile setting may guide scheduling and date-boundary summaries. Conflicting values use the documented request precedence. |

## 3. Standard Response Format

Every JSON response includes a server-generated `request_id` and timestamp. Successful single-resource responses contain `data`, an optional human-readable `message`, and `metadata` such as resource version, freshness, or operation state. Lists contain `data` as the result set and `pagination` with cursor, limit, and next/previous availability. Created resources include location/reference information and their initial state. Accepted background operations include an operation reference, current state, and a status retrieval path. No-content responses intentionally omit a body while retaining request identifiers in response headers.

Errors contain a stable `error code`, a user-safe `message`, `request_id`, timestamp, optional field-level validation details that do not leak internals, and safe next-action metadata such as retry timing or required reassessment. Authentication, authorisation, not-found, conflict, rate-limit, and internal failures use the corresponding status class. Internal errors never expose stack traces, provider responses, prompts, secrets, or private identifiers. AI-unavailable responses explain that AI assistance is temporarily unavailable and may offer deterministic content where permitted. Safety-restricted responses identify the restricted capability and an appropriate non-diagnostic next step without exposing sensitive rule internals.

## 4. Authentication API

All authentication responses avoid account-enumeration disclosures. Password and token material are never returned in logs or ordinary error details. Social login is post-competition.

| Method and path | Purpose / access | Request and response fields | Validation, limits, errors, idempotency, priority |
| --- | --- | --- | --- |
| POST `/auth/register` | Create a pending user account; guest. | Contact identifier, password, consent/terms version, locale; returns user reference, verification state, session policy summary. | Validate contact/password/policy; per-IP and per-contact throttling; generic duplicate response; idempotency required; must build. |
| POST `/auth/login` | Start authenticated session; guest. | Contact identifier, password, device context; returns session/authentication result and user-safe state. | Brute-force controls, verified-state handling, generic invalid-credential error; no idempotency; must build. |
| POST `/auth/logout` | Revoke current session; authenticated user. | Optional current-session confirmation; returns no content. | Ownership of session; safe repeat is no-content; must build. |
| POST `/auth/refresh` | Rotate/refresh authenticated session; valid refresh context. | Refresh credential carried by secure policy; returns renewed session state. | Rotation, replay detection, device/session validation; strict per-session/IP limit; must build. |
| GET `/auth/session` | Get current session/account state; authenticated user. | No body; returns user/session reference, expiry, verification, relevant role scopes. | Current-session validation; must build. |
| POST `/auth/password-reset-requests` | Request reset delivery; guest. | Contact identifier; returns generic acceptance. | Enumeration-safe, strict per-IP/contact throttling; idempotent acceptance; must build. |
| POST `/auth/password-resets` | Complete verified reset; guest with reset proof. | Reset proof, new password; returns generic completion/session policy. | One-time proof, password policy, revoke other sessions; strict rate limit; must build. |
| POST `/auth/email-verifications` | Verify contact using verified proof; guest/pending user. | Verification proof; returns verified state. | One-time/expiry/replay protections; idempotent if already verified; must build. |
| POST `/auth/email-verification-resends` | Resend verification; guest/pending user. | Contact identifier or authenticated context; returns generic acceptance. | Enumeration-safe throttle; must build. |
| POST `/auth/password-changes` | Change password from active session; authenticated user. | Current password, new password; returns completion. | Recent-auth/session checks, password policy, audit, rate limit; must build. |
| POST `/auth/sessions/revoke-all` | Revoke all sessions, optionally preserving current one by policy; authenticated user. | Confirmation; returns operation result. | Recent-auth requirement, audit; idempotent; high priority. |

## 5. User and Profile API

All profile endpoints require the current user unless an explicitly documented privileged scope exists. A user may access only their own profile. Avatar operations use the file policy in section 16.

| Method and path | Contract | Validation and priority |
| --- | --- | --- |
| GET `/users/me` | Returns current profile, public account state, and safe preference summary. | Owner scope; must build. |
| PATCH `/users/me` | Updates permitted profile fields such as preferred name and non-sensitive presentation data. | Allowlisted fields, optimistic version check, audit; must build. |
| PATCH `/users/me/preferences` | Updates communication, accessibility, workout-style, and reminder preferences. | Allowlisted values; must build. |
| PATCH `/users/me/units` | Updates display/measurement unit preference. | Valid supported unit system; high. |
| PATCH `/users/me/language` | Updates supported language preference. | Locale allowlist; must build. |
| PATCH `/users/me/timezone` | Updates timezone for schedules and summaries. | IANA timezone validation; must build. |
| POST `/users/me/avatar` | Creates approved avatar upload/finalisation request. | File policy, idempotency, ownership; build if time allows. |
| DELETE `/users/me/avatar` | Removes current avatar reference. | Owner scope; safe repeat; build if time allows. |
| POST `/users/me/data-exports` | Starts verified personal-data export. | Recent-auth, background operation, audit/rate limit; build if time allows. |
| POST `/users/me/deletion-requests` | Requests account deletion. | Recent-auth, confirmation, hold/retention disclosure; high. |
| DELETE `/users/me/deletion-requests/current` | Cancels a pending deletion before irreversible stage. | Owner/state validation and audit; high. |
| GET `/users/me/privacy-settings` | Returns consent, processing choices, export/deletion state, and user controls. | Owner scope; must build. |

## 6. Assessment API

Assessment endpoints require an authenticated owner and use versioned question/rule sets. A draft progresses through active, reviewable, completed, cancelled, or superseded states. Only one active assessment of a given applicable mode may exist per user; creation/completion commands require idempotency. Safety outcomes are computed deterministically in Python and may pause dependent plan generation.

| Method and path | State / contract | Validation, safety, and priority |
| --- | --- | --- |
| POST `/assessments` | Starts Quick Start, Full, Injury-Aware, Athlete, or reassessment draft; returns draft/version/progress. | Valid mode/eligibility; duplicate active-draft protection; must build for core modes. |
| GET `/assessments/active` | Returns current authorised draft and visible branch state. | Owner only; branch excludes irrelevant/sensitive fields; must build. |
| PATCH `/assessments/{assessment_id}/answers/{question_key}` | Saves one answer and recalculates dependent branches. | Required type/range/cross-field validation; invalidates dependent answers; rate-limited but save-friendly; must build. |
| PATCH `/assessments/{assessment_id}/sections/{section_key}` | Saves a bounded section checkpoint. | Active/review state only; validates section completeness; idempotency/version check; must build. |
| POST `/assessments/{assessment_id}/resume` | Reopens/resumes authorised draft. | Active draft and owner only; safe repeat; must build. |
| GET `/assessments/{assessment_id}/progress` | Returns completion, required/missing, branch, and readiness indicators. | Owner only; must build. |
| GET `/assessments/{assessment_id}/review` | Returns review-safe answer summary, missing-data impact, and safety summary. | Owner only, redacted where appropriate; must build. |
| PATCH `/assessments/{assessment_id}/answers/{question_key}` | Updates a prior answer; same path/semantics as save. | Version/concurrency check; recomputes branches and safety immediately; must build. |
| POST `/assessments/{assessment_id}/complete` | Validates and finalises assessment; returns result reference/readiness. | Only active/review state; idempotency required; hard safety may complete as paused/clearance-required; must build. |
| GET `/assessments/{assessment_id}/result` | Returns approved result, confidence, safety state, missing-data effects, and module eligibility. | Completed/superseded owner record; must build. |
| GET `/assessments` | Lists own assessment history with cursor/filter by type/state. | Owner scope; high. |
| POST `/assessments/reassessments` | Starts targeted reassessment from a valid current result. | Material-change/review trigger; source version retained; high. |
| POST `/assessments/{assessment_id}/cancel` | Cancels active draft without deleting governed history. | Active draft only; safe repeat; high. |
| DELETE `/assessments/{assessment_id}/data` | Requests deletion of eligible assessment data. | Verified privacy workflow, retention exceptions, audit; post-competition UI may use account deletion instead. |

## 7. AI Coach API

The competition flow is bounded conversation around the current approved assessment, plan, safety status, selected preferences, relevant progress, and user-approved memory. Python validates access, consent, safety, task eligibility, context freshness, rate/cost quota, and prompt-injection policy before any model call. The LLM may provide a constrained explanation, clarification, or permitted coaching option; it never receives or exposes prompts, chain-of-thought, secrets, or cross-user data.

| Method and path | Contract | Safety, limits, and priority |
| --- | --- | --- |
| POST `/ai/conversations` | Starts user-owned bounded conversation; returns conversation state and approved purpose. | Context/safety/consent gate; idempotent creation; must build. |
| POST `/ai/conversations/{conversation_id}/messages` | Sends one user message and returns accepted/final safe coach response. | Validate size/content, injection handling, per-user/IP burst and quota, timeout/fallback, idempotency; must build. |
| GET `/ai/conversations/{conversation_id}/messages` | Returns authorised, paginated conversation history. | Owner only; retention/redaction policy; high. |
| GET `/ai/conversations/{conversation_id}/summary` | Returns governed compact summary where available. | Owner only; never chain-of-thought; build if time allows. |
| POST `/ai/conversations/{conversation_id}/feedback` | Records usefulness/correction/safety feedback. | Owner scope, target-message validation, escalation for harm; must build. |
| DELETE `/ai/conversations/{conversation_id}` | Deletes/requests deletion of eligible conversation content. | Owner, retention exceptions, audit; high. |
| DELETE `/ai/memory/{memory_id}` | Clears one user-editable durable memory. | Owner/consent check; immediate future-context exclusion; high. |
| GET `/ai/availability` | Returns safe capability/provider availability by feature, not internal provider detail. | Public or authenticated read by policy; cacheable short-lived; must build. |

If a model times out, is unavailable, exceeds budget, or fails output validation, the message endpoint returns a user-safe AI fallback and, where permitted, deterministic plan/assessment information. Conversation and prompt logs retain minimal operational metadata; raw sensitive content, hidden instructions, secrets, and chain-of-thought are excluded from logs.

## 8. Workout API

Workout access requires a current assessment whose safety/readiness permits the requested action. Plan generation is a service/domain command, not a controller decision; it uses Python constraints and may include bounded AI explanation only after deterministic validation. Advanced live coaching is post-competition.

| Method and path | Contract | Validation/state/idempotency/priority |
| --- | --- | --- |
| POST `/workout-plans` | Generates initial permitted plan from current assessment. | Assessment/safety/entitlement dependency; idempotency; must build. |
| GET `/workout-plans/active` | Returns current active user plan. | Owner/current-plan rule; must build. |
| GET `/workout-plans` | Lists plan history. | Cursor, owner scope; high. |
| GET `/workout-sessions/{session_id}` | Returns own planned/in-progress/completed session. | Owner and state validation; must build. |
| POST `/workout-sessions` | Starts session from active plan. | Plan/state checks; idempotent start; must build. |
| POST `/workout-sessions/{session_id}/set-logs` | Records an exercise set. | Session active, exercise belongs to session, plausibility checks; idempotency; must build. |
| POST `/workout-sessions/{session_id}/pause` | Pauses active session. | Valid transition; safe repeat; high. |
| POST `/workout-sessions/{session_id}/complete` | Completes session with feedback. | Valid state, duplicate protection, pain screen; idempotency; must build. |
| POST `/workout-sessions/{session_id}/exercises/{exercise_id}/skip` | Records a skip/reason. | Active session/allowed exercise; high. |
| POST `/workout-sessions/{session_id}/exercises/{exercise_id}/substitutions` | Requests/selects permitted substitution. | Equipment, experience, limitation, plan rules; high. |
| POST `/workout-sessions/{session_id}/pain-reports` | Records pain/limitation and invokes safety assessment. | Immediate deterministic safety handling; must build. |
| GET `/exercises` | Lists approved exercise catalogue with authorised filters/search. | Cacheable catalogue, pagination; high. |
| GET `/exercises/{exercise_id}` | Returns approved exercise detail/version. | Public/authenticated policy; high. |
| PATCH `/users/me/training-preferences` | Updates training preferences that may require plan review. | Allowlisted fields, current plan impact; high. |
| POST `/workout-plans/{plan_id}/regenerations` | Requests a new plan revision. | Assessment/safety/plan state, idempotency, reason; build if time allows. |

## 9. Nutrition API

Nutrition endpoints are owner-scoped. Plan generation requires current goal, dietary preference, allergy/intolerance status, and safety/readiness data; missing data returns an explicit readiness/follow-up response rather than a generic plan. The system never guarantees allergen safety, prescribes medical diets, or gives medication/supplement advice.

| Method and path | Contract | Safety/validation/priority |
| --- | --- | --- |
| POST `/nutrition-plans` | Generates permitted nutrition plan from approved assessment. | Allergy/restriction and safety gate; idempotency; must build. |
| GET `/nutrition-plans/active` | Returns current active plan. | Owner/current-plan rule; must build. |
| GET `/nutrition-plans` | Lists plan history. | Cursor and owner scope; high. |
| POST `/meal-logs` | Creates user meal log. | Date/quantity/ownership validation; idempotency; must build. |
| PATCH `/meal-logs/{meal_log_id}` | Updates own meal log. | Allowlisted edits, concurrency check; high. |
| DELETE `/meal-logs/{meal_log_id}` | Removes eligible own meal log. | Owner and retention rule; high. |
| POST `/water-logs` | Creates hydration log. | Positive plausible quantity/unit; idempotency; must build. |
| GET `/nutrition/daily-summary` | Returns user-local-day summary and data completeness. | Timezone validation, no false precision; must build. |
| GET `/nutrition/macro-targets` | Returns active-plan targets with version/explanation. | Owner/current-plan/safety scope; high. |
| PATCH `/users/me/dietary-preferences` | Updates preferences/restrictions and may request review. | Allergy confirmation and plan impact; must build. |
| POST `/users/me/allergy-reports` | Adds/reports allergy or intolerance for safety review. | Immediate restriction update; audit; must build. |
| POST `/nutrition-plans/{plan_id}/regenerations` | Requests new plan revision. | Current assessment and safety gate; idempotency; build if time allows. |

Meal scanning is post-competition; future image handling follows section 16 and requires separate consent.

## 10. Progress API

| Method and path | Contract | Privacy, validation, and priority |
| --- | --- | --- |
| POST `/body-measurements` | Logs own authorised measurement. | Unit/range/time validation, sensitive owner scope, idempotency; must build. |
| GET `/body-measurements` | Lists measurement history with cursor/filter. | Owner scope and sensitive response controls; must build. |
| POST `/daily-check-ins` | Records mood/energy/adherence-style daily check-in within approved bounds. | Non-medical language, one-per-period rule, idempotency; high. |
| GET `/progress/summary` | Returns current derived progress and data-completeness status. | Python-derived metrics, owner scope; must build. |
| GET `/progress/weekly` | Returns bounded weekly trend/snapshot. | Minimum-data rule; high. |
| GET `/goals/{goal_id}/progress` | Returns progress against own active/historical goal. | Owner/goal-state validation; high. |
| POST `/progress-photos` | Starts/finalises consented private progress-photo upload. | Strict file/consent/access/retention policy; build if time allows. |
| DELETE `/progress-photos/{photo_id}` | Deletes own eligible photo/reference. | Owner, audit, durable deletion workflow; build if time allows. |
| GET `/progress/comparisons` | Compares approved periods. | Minimum-data/no misleading inference rule; build if time allows. |

Progress photos are private by default, never included in ordinary analytics or AI context without separate consent, and have restrictive retention/deletion controls.

## 11. Dashboard API

GET `/dashboard` returns a single owner-scoped, user-local-day aggregate: assessment/readiness status, today’s workout, nutrition/water summary, recent progress, permitted AI recommendation or availability state, safety notice, goal progress, and unread notification count. Aggregation prevents the client from coordinating many inconsistent calls and makes partial-data states explicit.

The endpoint may cache short-lived, non-sensitive derived fragments keyed by user/context versions. It must invalidate when assessment, plan, safety, logging, notification, or preference state changes. Partial failure returns the available safe sections with per-section freshness/status metadata; a stale section is labelled with last updated time and never masks a current safety change. Competition target: a typical authorised dashboard response should be available within a user-perceptible interactive budget under normal load; expensive report/AI work is never on the critical path.

## 12. Reports API

| Method and path | Contract | Requirements and priority |
| --- | --- | --- |
| POST `/reports/weekly-generations` | Starts weekly report generation for eligible period. | Minimum-data and idempotency checks; accepted background operation; build if time allows. |
| GET `/reports/weekly/{period_key}` | Gets current weekly report. | Owner, period/version, data-completeness explanation; build if time allows. |
| POST `/reports/monthly-generations` | Starts monthly report generation. | Background status/eligibility; post-competition. |
| GET `/reports` | Lists report history. | Cursor/filter by type/state; high. |
| GET `/reports/{report_id}/download` | Obtains authorised export/download reference. | Owner, signed/short-lived access, audit; post-competition. |
| DELETE `/reports/{report_id}` | Deletes eligible user-facing copy or requests deletion. | Owner/retention policy; post-competition. |
| GET `/report-generations/{operation_id}` | Gets generation state, retry/failure information. | Owner scope; high. |

Python calculates metrics and data sufficiency. AI may turn approved metrics into a bounded narrative but must not infer causal or medical conclusions. On generation failure, return metrics-only result if available or transparent pending/failure state; never fabricate a report.

## 13. Notification API

| Method and path | Contract | Rules and priority |
| --- | --- | --- |
| GET `/notifications` | Lists own notifications with cursor, unread/type/date filters. | Owner scope, bounded pagination; build if time allows. |
| GET `/notifications/unread-count` | Returns unread count. | Owner scope, short cache; high. |
| POST `/notifications/{notification_id}/read` | Marks one notification read. | Owner/state validation; idempotent; high. |
| POST `/notifications/read-all` | Marks current filtered/all notifications read. | Owner scope, idempotent; build if time allows. |
| DELETE `/notifications/{notification_id}` | Removes eligible notification from user view. | Owner/retention policy; high. |
| GET `/users/me/notification-preferences` | Returns allowed notification preferences. | Owner scope; high. |
| PATCH `/users/me/notification-preferences` | Updates preference/channel/schedule choices. | Consent/timezone/allowlist validation; high. |

## 14. Admin API

Administration is strictly RBAC-controlled, audited, purpose-limited, and not a back door to sensitive health data. Competition scope requires only system administration; trainer and organisation administration are post-competition.

| Method and path | Contract | RBAC / priority |
| --- | --- | --- |
| GET `/admin/users` | Lists limited user administrative summaries. | Admin only; filters/pagination; no sensitive details by default; build if time allows. |
| GET `/admin/users/{user_id}/summary` | Returns minimal support/operational summary. | Admin with support purpose scope, audited; high. |
| POST `/admin/users/{user_id}/suspensions` | Suspends account. | Privileged admin, reason/review/audit; high. |
| DELETE `/admin/users/{user_id}/suspensions/current` | Restores eligible suspended user. | Privileged admin, audit; high. |
| POST `/admin/users/{user_id}/soft-deletions` | Starts soft-delete/administrative removal process. | Highest privilege, policy/audit; post-competition. |
| GET `/admin/audit-events` | Lists authorised audit events with strict filters. | Admin/auditor scope; immutable evidence; build if time allows. |
| GET `/admin/system-health` | Returns safe operational health summary. | Admin/system scope; no secrets; build if time allows. |
| GET `/admin/ai-usage-summary` | Returns aggregate cost/latency/safety measures. | Admin scope, aggregate/redacted; build if time allows. |
| GET/PATCH `/admin/feature-flags/{flag_key}` | Reads/changes approved feature flag. | Restricted role, validation/audit/rollback; post-competition. |

## 15. Analytics API

There is no public analytics API. Most product events are generated server-side from authenticated domain actions: assessment completion, safety state, plan creation, session completion, report state, and AI lifecycle. The frontend may submit only a small allowlisted set of low-risk experience events, such as page/view flow or client rendering error category, through a controlled internal endpoint. It cannot submit health facts, arbitrary event names, identities for another user, financial outcomes, or raw free text.

Frontend events are schema-allowlisted, rate-limited, size-limited, pseudonymised where possible, and validated against the current session. Sensitive fields, raw assessment answers, messages, photos, secrets, and unredacted errors are prohibited. Analytics is used to improve flow, reliability, retention, cost, and safety—not to make unsupported health claims.

## 16. File Upload API

| Asset | Rules | Competition scope |
| --- | --- | --- |
| Avatar | Permit a small allowlist of image types, strict size/pixel limits, generated storage name, metadata stripping, ownership check, and short-lived signed upload/download references. | Build if time allows. |
| Progress photo | Same controls plus explicit separate consent, private-by-default access, stricter retention/deletion/audit, and no AI use without further consent. | Build if time allows. |
| Meal image | Future optional image input; requires nutritional-safety and consent policy. | Post-competition. |
| Form-check video | Future high-risk media path; requires strict duration/size/type limits, malware scan, moderation/safety policy, and no medical/injury claim. | Post-competition. |

Clients never set filenames, MIME trust, storage location, visibility, or retention. The service validates declared and inspected type, size, dimensions/duration, ownership, upload intent, and malware-scan readiness before final availability. Failed/expired uploads are quarantined or removed. Signed URLs are scoped, short-lived, and never grant list access. Upload endpoints have tighter user/IP burst limits than ordinary API calls.

## 17. Authorization Matrix

| Role | Permitted modules/actions | Ownership rule |
| --- | --- | --- |
| Guest | Registration, login, verification, password-reset initiation/completion, public safe availability content. | No private-resource access. |
| User | Own profile, consent, assessment, AI, plans, logs, progress, reports, notifications, deletion/export requests. | Must match authenticated user; cannot select another user ID. |
| Trainer | Post-competition: explicitly granted client summaries/plans within organisation/client scope. | Grant is scoped, time-bound/audited; no implied access to all client health data. |
| Admin | Limited operations, user status, audit/health/aggregate AI usage, feature governance by privilege. | Default excludes private health/AI content; every sensitive action is audited. |
| System service | Background jobs and internal domain operations using narrow service identity. | Least privilege and no broad user impersonation. |

Authorisation is enforced server-side in middleware/service/domain boundaries and rechecked at resource access. Frontend role visibility is never a security control.

## 18. Validation Strategy

| Validation | Location | Responsibility |
| --- | --- | --- |
| Request validation | Controller boundary | Content type, required transport fields, basic type/shape/size, request identifier. |
| Domain validation | Service and domain rules | Business meaning, state transitions, plan/assessment eligibility, calculations, invariants. |
| Cross-field validation | Domain rules | Time/target/unit coherence, dependent assessment answers, allergy/restriction effects. |
| State validation | Service/domain rules | Draft/complete/session/plan/report transitions and allowed command timing. |
| Ownership validation | Authentication/authorisation middleware plus service | Actor role/scope and resource ownership; prevents broken object-level authorisation. |
| Safety validation | Deterministic Python rules | Red flags, age policy, injury/allergy/goal restrictions; precedence over AI. |
| Duplicate detection | Idempotency/service/repository boundary | Same actor/key/payload replay versus conflicting duplicate. |
| Concurrency handling | Service/repository boundary | Version/precondition checks, safe retries, conflict response, no silent lost update. |

Repositories enforce persistence constraints and do not own product policy. Controllers do not encode business/safety rules. Middleware handles common authentication, request context, rate limiting, and low-level protections, not resource-specific decisions.

## 19. Error Catalogue

| Code | Status | User-safe message | Developer meaning / retry / severity / audit |
| --- | --- | --- | --- |
| `AUTH_INVALID_CREDENTIALS` | 401 | “The sign-in details are not valid.” | Generic credential failure; do not retry automatically; warning; security event. |
| `AUTH_SESSION_EXPIRED` | 401 | “Your session has expired. Please sign in again.” | Refresh/session invalid; user re-authenticates; info/warning; audit when replay suspected. |
| `AUTH_FORBIDDEN` | 403 | “You do not have permission for this action.” | Scope/role/ownership denial; no retry; warning; audit for sensitive attempt. |
| `RESOURCE_NOT_FOUND` | 404 | “The requested item is not available.” | Missing or intentionally undisclosed resource; no retry; info. |
| `VALIDATION_FAILED` | 422 | “Please review the highlighted information.” | Request/domain field validation; correct and retry; info. |
| `ASSESSMENT_INCOMPLETE` | 409 | “Complete the required assessment information first.” | Required readiness absent; reassess then retry; info. |
| `SAFETY_RESTRICTED` | 403 | “This action is currently restricted for safety.” | Deterministic safety/clearance gate; no automatic retry; warning/audit. |
| `RESOURCE_CONFLICT` | 409 | “This item changed. Refresh and try again.” | Version/state conflict; refresh/correct; info. |
| `DUPLICATE_REQUEST` | 409 | “This request was already processed differently.” | Idempotency-key payload conflict; do not retry with same key; warning. |
| `AI_UNAVAILABLE` | 503 | “AI assistance is temporarily unavailable.” | Provider/capability unavailable; retry after hint or use fallback; error. |
| `AI_TIMEOUT` | 504 | “AI assistance took too long. Please try again.” | Timed-out bounded task; safe retry where allowed; warning/error. |
| `FILE_INVALID` | 422 | “This file cannot be accepted.” | Type/size/content/scan/intent invalid; correct file; warning. |
| `RATE_LIMITED` | 429 | “Too many requests. Please try again shortly.” | Applicable limit exceeded; honor retry header; warning/security audit if abusive. |
| `INTERNAL_FAILURE` | 500 | “Something went wrong. Please try again.” | Unhandled/internal failure; retry only if safe; error/incident correlation. |

## 20. Rate-Limiting Strategy

Limits are enforced per IP and per authenticated user where applicable, with short burst protection and longer rolling windows. Values are configuration-managed, monitored, and initially conservative rather than pretending internet-scale capacity. Responses provide standard retry guidance without exposing internal thresholds.

| Category | Policy |
| --- | --- |
| Registration / login / password reset | Strict per-IP and per-contact limits, low burst allowance, escalating cool-downs, enumeration-safe responses. |
| Assessment saves | Generous authenticated per-user limit with modest burst protection so autosave/resume remains usable; malformed/abusive traffic is limited. |
| AI Coach messages | Per-user and per-IP burst/window limits plus daily task/cost quota; lower limits for unverified/risk states. |
| Plan generation | Low per-user window and idempotency requirement; regeneration requires reason/state check. |
| File uploads | Tight per-user/IP count/size-rate limits, concurrent-upload cap, and signed-upload expiry. |
| Admin operations | Low per-admin burst/window, recent-auth requirement for sensitive commands, and full audit. |

Trusted internal calls use separate authenticated service identity and narrow allowlisted limits, never a blanket bypass. Rate limits are not a substitute for authorisation, validation, or cost controls.

## 21. Caching Strategy

Cache approved exercise catalogue reads, feature flags, short-lived AI availability status, report-generation status, and carefully bounded dashboard fragments. User preferences may be cached only in a private, owner-scoped form with immediate invalidation on change. Dashboard aggregation cache keys include user, locale/timezone, assessment/plan/safety versions, and freshness window.

Never carelessly cache authentication tokens, credentials, private AI conversations, raw sensitive profile/assessment data, or safety state across requests/users. Safety changes invalidate affected plan, dashboard, and recommendation caches immediately. Assessment/plan/preference/log/consent updates invalidate dependent entries; cache misses always return to the authoritative Python domain path. A future Redis-style shared cache is an operational option, not a competition dependency.

## 22. Background Jobs

| Operation | Trigger / status | Retry and failure | Priority |
| --- | --- | --- | --- |
| Report generation | Eligible user/admin schedule or explicit request; operation status visible to owner. | Bounded retries; metrics-only/pending fallback; high. |
| AI summarisation | Conversation threshold or explicit approved request; governed summary state. | Retry only when safe; retain raw content minimally; build if time allows. |
| Notification delivery | Scheduled/event-driven preference-qualified notification; delivery state tracked. | Provider-aware retry/dead-letter policy; build if time allows. |
| Data export | Verified user request; status and expiry visible to owner. | Retry generation, no duplicate disclosure; post-competition. |
| Account deletion | Verified request after grace/hold policy; state tracked. | Explicit review/failure escalation, never silent partial deletion; high. |
| File processing | Upload completion; scan/strip/derive state tracked. | Quarantine on failure; build if time allows. |
| Backup tasks | Operations schedule; internal status only. | Escalate failed backup/restore validation; commercial operations. |

Queues are an implementation choice for later. The API contract exposes operation state and safe retry semantics without assuming a specific queue technology.

## 23. Observability

Every request records structured request ID, correlation ID where supplied, route template, status, latency, authenticated role category, rate-limit outcome, and safe error category. Distributed tracing links controller/service/repository/background/AI boundaries without storing private payloads. Metrics include request/error/slow-request rates, assessment completion, plan/report operation status, cache behaviour, file-processing status, authentication failures, authorisation denials, and rate-limit events.

AI monitoring includes task category, latency, availability, timeout/fallback/block rate, model/provider category, usage/cost band, safety outcome, feedback, and evaluation regression. Audit events cover sensitive access, role/consent/safety changes, exports/deletion, admin actions, and policy/flag changes. Logs must never contain passwords, tokens, secrets, raw assessment answers, health-detail prose, private conversation content, media, full personally identifiable contact data, prompts, chain-of-thought, or unredacted provider errors.

## 24. Security Review

JWT/session security uses short-lived access context, secure refresh/session rotation, revocation, replay detection, recent-auth for sensitive operations, and server-side session-state enforcement. Cookie use, if selected, requires secure/HTTP-only/same-site policy and CSRF protection for state-changing browser flows. CORS is an explicit allowlist; XSS is mitigated through safe response encoding, no trusted HTML from user/AI content, and strict frontend rendering boundaries.

NoSQL injection is prevented by typed/allowlisted request interpretation and repository-controlled query construction. Mass assignment is prevented by explicit writable-field allowlists. Broken object-level authorisation is prevented by server-side owner/scope checks for every resource reference. File uploads use intent/ownership/type/size/scan/storage restrictions. Replay attacks use idempotency, nonce/expiry/rotation where applicable. Brute force uses rate limits and generic errors. Secrets are externalised and never returned/logged.

Prompt injection and AI abuse are contained by treating user/imported text as untrusted data, keeping Python rules authoritative, minimising context, filtering disallowed tasks, validating output, limiting quotas, and never exposing prompts/system details. Sensitive response leakage is controlled by field-level response shaping, minimum necessary context, redaction, safe errors, and audit.

## 25. API Testing Strategy

Unit tests cover domain calculations, safety rules, validation, response mapping, state transitions, idempotency, and error categorisation. Service tests cover orchestration, ownership, concurrency, background-operation state, cache invalidation, and AI boundary/fallback decisions. Repository tests cover persistence constraints, cursor/filter semantics, and isolation without duplicating domain policy.

Route integration tests cover authentication, authorisation, request/response contract, validation, request IDs, content type, rate limits, and safe errors. Required specialised tests cover file-upload intent/type/size/ownership, AI timeout/unavailable/output-block fallback, prompt-injection resistance, safety restrictions, privacy export/deletion state, and admin RBAC/audit. Contract tests ensure documented fields/status/error codes remain compatible; end-to-end tests prove the competition vertical slice from registration through assessment, plan, logging, dashboard, and bounded AI coach.

Before competition, all critical endpoints must have happy-path, ownership-denial, invalid-input, state-conflict, idempotency/retry, safety, and unauthorised tests. OpenAPI exploration must be usable with safe test accounts and must not expose production secrets or sensitive sample data.

## 26. Competition Scope

| Must Build Before Competition | Build If Time Allows | Post-Competition |
| --- | --- | --- |
| Authentication; current profile/preferences; Smart Assessment lifecycle; one bounded AI Coach flow; dashboard aggregate; basic workout plan/session logging; basic nutrition plan/meal/water logging; progress measurement/summary; deterministic safety/validation; owner authorisation; rate limits; tests; OpenAPI documentation. | Weekly reports, notifications, football/goalkeeper endpoints, improved private caching, export flow, avatar/progress-photo flow, limited admin health/usage views. | Payments/subscriptions, multi-tenant gyms/trainers, marketplace, meal/vision uploads, wearables, voice, advanced enterprise admin, monthly reports, partner APIs. |

The target is a polished 70% complete vertical slice, not a broad collection of partial endpoints. Every must-build endpoint should demonstrate a real user journey and enforce the documented safety/ownership constraints.

## 27. OpenAPI and Documentation Strategy

The API documentation groups endpoints by tags: Authentication, Users, Assessments, AI Coach, Workouts, Nutrition, Progress, Dashboard, Reports, Notifications, Administration, and System. Each endpoint has a concise summary, detailed description, access requirement, lifecycle/side-effect note, request-field description, success/error field description, status codes, idempotency/rate-limit expectation, and safe illustrative examples that contain no real personal data or secrets.

Authentication schemes, ownership rules, pagination/filtering conventions, localisation/timezone rules, error catalogue, deprecation policy, and file restrictions are documented once and referenced consistently. `/docs` is judge-friendly when it clearly separates public from authenticated endpoints, permits testing through scoped demo accounts, highlights required headers, displays safety-restricted outcomes, and makes no claim that interactive documentation bypasses authorisation or rate limits.

## 28. Definition of Done

Sprint 2.5 is complete only when all competition-critical modules have methods/paths and contract fields described; authentication, authorisation, ownership, validation, deterministic safety, errors, rate limits, file handling, caching, background work, observability, security, testing, OpenAPI, and realistic scope are documented; no implementation code exists; and the README links to this blueprint.

## 29. Judge Review

| Dimension | Review |
| --- | --- |
| API clarity | Strong: REST conventions, response/error contract, endpoint ownership, and operation states are consistently defined. |
| Technical maturity | Strong: idempotency, versioning, concurrency, rate limits, observability, cache invalidation, and job status are considered. |
| Security | Strong if implemented with verified owner checks, safe logging, session controls, and deterministic safety gates. |
| Python ownership | Strong: controller boundaries are thin and business/safety/AI orchestration remain in Python services/domain rules. |
| Feasibility | Good only if the team ships the must-build vertical slice and defers payments, tenancy, media, and wearables. |
| Testability/documentation | Strong: stable errors, states, contracts, and required test types give judges a clear verification path. |

**Strengths:** coherent cross-module contracts, careful security posture, safe hybrid AI boundaries, and an honest commercial roadmap.  
**Weaknesses:** the endpoint surface is extensive; implementation quality depends on keeping controllers thin and tests meaningful.  
**Risks:** implementing too many endpoints, treating OpenAPI as a substitute for tests, leakage through logs/errors, and inconsistent owner checks.  
**Likely questions:** How is idempotency enforced? What happens when AI fails? Which layer decides safety? How are user records isolated? How can a judge safely test the API?  
**Improvement:** demonstrate a small set of documented endpoints live with deliberate invalid, forbidden, duplicate, and safety-restricted requests.  
**Score:** 92/100 as an API blueprint; first-place quality requires a narrow, secure, tested implementation rather than every future module.

## 30. Startup Review

This contract supports growth because it separates stable resource interfaces from Python domain logic, makes mobile clients first-class through stateless/versioned conventions, and prepares background/AI/media work for independent scaling. Cost is controlled through bounded AI contracts, quotas, cache rules, and async operations. Partner readiness is future-facing: tenant and partner APIs are deferred until proven requirements justify a stable external contract.

Build now the identity, ownership, assessment, plan, progress, dashboard, and bounded AI loop that demonstrates repeatable value. Postpone public partner APIs, payments, complex multi-tenancy, media intelligence, and enterprise administration. Premium opportunities include high-quality reports, sport-specific plans, advanced AI coaching, human-coach collaboration, and approved integrations. Long-term platform value comes from trusted APIs with stable contracts, user-controlled data, deterministic safety, and measurable operational quality.
