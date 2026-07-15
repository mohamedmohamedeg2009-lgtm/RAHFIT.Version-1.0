# RAHFIT AI — Enterprise Domain Blueprint

**Status:** Official Sprint 2.6 pre-implementation specification  
**Scope:** Business domain, ownership, rules, lifecycle, and policy architecture only. This document contains no code, API, schema, JSON, model, or interface implementation.

## 1. Domain Philosophy

Domain-Driven Design (DDD) makes the business model the centre of the system: the language used by users, product owners, coaches, and engineers becomes explicit concepts, boundaries, rules, and events. For RAHFIT AI, this matters because “generate a plan” is not a technical action alone; it depends on eligibility, consent, assessment freshness, safety status, allergies, available time/equipment, goal priority, and user ownership.

The domain comes before implementation so that controllers, storage, AI providers, and UI choices do not accidentally define business policy. Controllers translate requests; repositories persist governed state; services coordinate use cases; domain entities, value objects, policies, and services own meaning and invariants. Rules must not live in controllers because they would be duplicated across web, mobile, background, admin, and future partner flows, becoming inconsistent and unsafe.

A rich domain model expresses behaviour, lifecycle, and constraints near the concepts they govern. An anemic model merely moves raw data through technical layers and leaves essential rules scattered in handlers. Python is the primary home for domain rules because it is the backend’s authoritative business language and can apply deterministic safety, permissions, calculations, lifecycle transitions, and AI boundaries independently of a client or model provider.

## 2. Bounded Contexts

| Context | Purpose and responsibilities | Dependencies / owner | Growth and competition priority |
| --- | --- | --- | --- |
| Identity | Account lifecycle, sessions, verification, credential/security status, and role assignment. | Owns identity state; supplies authenticated actor to all contexts. | Must build; future delegated/enterprise identities. |
| User Profile | User-owned presentation, preferences, locale, units, accessibility, and privacy choices. | Depends on Identity; supplies permitted preferences to Assessment, plans, AI, Notifications. | Must build; future organisation profile overlays. |
| Assessment | Adaptive intake, reassessment, consented context, readiness, and deterministic safety screening. | Depends on Profile, Safety Policy; supplies approved results to planning/AI. | Must build; future sport/clinician flows. |
| Goals and Habits | User intent, priorities, realistic targets, routines, and adherence framing. | Depends on Assessment; informs plans, progress, reports, AI. | Goals must build; habit depth if time allows. |
| Workout | Plan lifecycle, exercise prescription, sessions, completion, substitutions, and pain reporting. | Depends on Assessment, Goals, Safety, Exercise Catalogue. | Must build basic plan/session; future live/sport coaching. |
| Nutrition | Nutrition plan lifecycle, dietary constraints, meal/water logging, and practical adherence context. | Depends on Assessment, Goals, Safety, Food Catalogue. | Must build basic plan/logging; future regional/scan support. |
| Recovery | Non-medical rest, sleep, fatigue, stress, and training-load interpretation. | Depends on Assessment, Workout, Progress, Safety. | Basic conservative signals if time allows; future wearable support. |
| Progress | User observations, derived trends, goal progress, and data completeness. | Depends on Goals, Workout, Nutrition, Recovery. | Must build basic measurement/progress; future advanced comparisons. |
| AI Coach | Governed, explainable, bounded coaching and recommendations. | Depends on approved Assessment/Profile/Plans/Progress, Rules and Safety. | One bounded flow must build; future multi-modal coaching. |
| Reports | Periodic, data-sufficient summaries and next-focus guidance. | Depends on Progress, Plans, Goals, AI policy. | Weekly if time allows; future export/monthly. |
| Notifications | User-controlled reminders and lifecycle communications. | Depends on Preferences, plans, reports, events. | If time allows; future multi-channel delivery. |
| Subscriptions | Entitlement, trial, billing-state, and commercial access rules. | Depends on Identity; supplies entitlement checks. | Post-competition implementation; domain boundary documented now. |
| Administration and Support | Least-privilege operational care, moderation, feature governance, and audit review. | Depends on Identity/Permission Policy; never owns user health data. | Minimal operational health if time allows; advanced admin future. |
| Analytics | Privacy-aware product, quality, safety, and operational measurement. | Consumes domain events; cannot author user facts. | Basic server events must build; warehouse/experiments future. |
| System | Feature flags, policy versions, operational configuration, and service health. | Supplies controlled configuration to all contexts. | Minimal configuration must build; enterprise operations future. |
| Future Vision | Consent-governed media assistance for meal/form support. | Depends on Profile, Consent, Safety, AI. | Post-competition only. |

## 3. Core Domain Entities

| Context | Entities |
| --- | --- |
| Identity/Profile | User, Session, Consent Record, Organisation, Membership, Role Assignment, Privacy Request. |
| Assessment/Goals | Assessment, Assessment Session, Assessment Result, Safety Review, Goal, Habit. |
| Workout | Exercise, Exercise Prescription, Workout Plan, Workout Session, Set Log, Pain Report. |
| Nutrition/Recovery | Nutrition Plan, Meal, Food Log, Water Log, Sleep Observation, Recovery Check-in, Dietary Restriction. |
| Progress/Reports | Body Measurement, Progress Snapshot, Health Score, Recovery Score, Progress Report, Achievement. |
| AI | AI Conversation, AI Message, Coach Memory, Recommendation, AI Feedback, AI Usage Record. |
| Engagement/Commercial/System | Notification, Subscription, Entitlement, Payment Event, Audit Event, Analytics Event, Support Ticket, Feature Flag, System Setting. |
| Future integrations | Wearable Connection, Wearable Import, Vision Asset, Vision Analysis, Community Post, Moderation Event. |

## 4. Entity Specifications

The specifications below focus on business meaning, not storage structure. “Audit” means meaningful lifecycle/privileged actions are traceable; “soft deletion” means removal from normal use while governed history remains where policy permits.

### Identity, profile, and governance entities

| Entity | Meaning, owner, lifecycle, and states | Rules, relationships, deletion, expansion, priority |
| --- | --- | --- |
| User | Primary person/account aggregate; owns personal profile and health-adjacent domain records. States: pending verification, active, suspended, deletion pending, anonymised/closed. | Only active, authorised users may use protected product functions. Transitions are policy/audit governed. Owns consent, assessment, goals, plans, logs, AI, and privacy requests. Soft delete/anonymise through verified workflow. Must build. |
| Session | Time-bounded authenticated access instance owned by User. States: active, refreshed, revoked, expired. | Cannot outlive identity/security policy; revocation is immediate for protected actions. Relates to User and audit. Expires rather than ordinary deletion. Must build. |
| Consent Record | Immutable evidence of a user decision for a versioned purpose. States: granted, withdrawn, superseded, expired where applicable. | A feature may use sensitive/AI/media context only with current applicable consent. Links User to policy version. Retained per legal policy; no casual deletion. Must build. |
| Organisation | Future tenant such as gym, university, employer, or club. States: pending, active, suspended, closed. | Does not own a member’s private health data by default. Links Memberships and tenant settings. Contractual retention on closure. Post-competition. |
| Membership | Explicit relationship granting User a scoped Organisation role. States: invited, active, revoked, expired. | No access outside granted scope; one active scope per relationship rule. Links User, Organisation, Role Assignment. Revocation is auditable. Post-competition. |
| Role Assignment | Controlled permission grant for a principal. States: active, revoked, expired. | Least privilege and separation of duties; permission is server-enforced. Links User/Membership to Role. Retain audit history. Must build only admin role basics. |
| Privacy Request | Verified user request for export, correction, deletion, or consent action. States: requested, verified, in progress, completed, rejected/held. | Requires identity verification and clear retention exceptions. Links User and Audit Event. No silent cancellation after irreversible stage. High. |
| Audit Event | Immutable record of security, privacy, administrative, safety, and material lifecycle action. | Does not replace business entity history; links actor, target, action, outcome. Never casually deleted; access restricted. Build critical events. |
| Support Ticket | User-requested support case. States: open, triaged, waiting, resolved, closed. | Support access is purpose-bound and does not confer general health-data access. Links User and authorised support actor. High. |
| Feature Flag | Governed capability switch. States: proposed, enabled, disabled, retired. | Changes require owner, scope, expiry/review, audit, and rollback. Does not bypass safety or permission policy. Post-competition management. |
| System Setting | Versioned operational/policy configuration. States: proposed, approved, active, retired. | Privileged changes are reviewed/audited; settings cannot silently redefine historical decisions. High. |

### Assessment, goal, and habit entities

| Entity | Meaning, owner, lifecycle, and states | Rules, relationships, deletion, expansion, priority |
| --- | --- | --- |
| Assessment | Versioned adaptive intake owned by User. States: started, in progress, reviewable, completed, cancelled, superseded, archived. | One applicable active assessment per user/mode. Completion validates required branches and invokes deterministic safety. Links Assessment Session, Result, Safety Review. Draft may be cancelled; completed content is superseded, not overwritten. Must build. |
| Assessment Session | Bounded attempt/resume context for an Assessment. States: active, paused, resumed, completed, abandoned. | Save/resume must preserve valid work; duplicate completion does not create conflicting result. Links User/Assessment. Expired drafts follow policy. Must build. |
| Assessment Result | Approved, interpretable output of completed Assessment. States: current, stale, superseded, blocked. | Carries readiness, missing-data, and safety outcome; feeds planning/AI. Cannot be silently altered. Retain as history; must build. |
| Safety Review | Deterministic assessment/workout/nutrition safety disposition. States: normal, caution, clearance required, paused, resolved. | Hard restrictions override preferences, entitlement, and AI. Never represents diagnosis. Links User/Assessment/Pain Report. Audit and retain; must build. |
| Goal | User-owned desired outcome and priority. States: draft, active, paused, achieved, abandoned, archived. | One active primary goal per applicable domain; secondary goals must not contradict hard safety rules. Links Assessment, plans, Progress Snapshot. Supersede/retain history. Must build. |
| Habit | User-owned recurring behaviour commitment. States: proposed, active, paused, completed, retired. | Habit must be feasible for stated schedule and must not reward unsafe behaviour. Links Goal, reminders, progress. Soft delete/retire. If time allows. |

### Workout, nutrition, recovery, and progress entities

| Entity | Meaning, owner, lifecycle, and states | Rules, relationships, deletion, expansion, priority |
| --- | --- | --- |
| Exercise | Curated reusable movement knowledge, owned by product content governance. States: draft, approved, retired. | Referenced plans retain the approved version; retired exercise remains interpretable for history. Links prescriptions/media. Must build catalogue subset. |
| Exercise Prescription | Immutable planned use of an Exercise within a plan/session. States: proposed, active, substituted, skipped, completed. | Must respect equipment, experience, time, limitation, and safety constraints. Links Workout Plan/Session/Exercise. High. |
| Workout Plan | User-approved training programme aggregate. States: draft, generated, awaiting review, active, paused, completed, superseded, archived. | Requires current eligible Assessment Result; one active applicable plan. A material change creates a revision. Links Goal, prescriptions, sessions, Safety Review. Must build. |
| Workout Session | One planned or actual execution of a Workout Plan. States: scheduled, active, paused, completed, skipped, cancelled. | Only active/scheduled session may log sets; complete once; pain report can pause/limit it. Links Set Logs and Pain Reports. Must build. |
| Set Log | User observation of one prescribed exercise effort. States: recorded, corrected, voided. | Must belong to authorised active/completed session and be plausible; correction preserves history. Links Workout Session/Prescription. Must build basic. |
| Pain Report | User-reported discomfort/limitation during activity. States: reported, reviewed, caution, clearance required, resolved. | Triggers Safety Review; no diagnosis; may restrict session/plan. Links User, Session, Assessment Result. Must build. |
| Nutrition Plan | User-approved nutrition guidance aggregate. States: draft, generated, awaiting review, active, paused, completed, superseded, archived. | Requires eligible assessment and current dietary restriction context; must never violate known allergies/restrictions. Links Goal, Meals/Food Logs. Must build basic. |
| Meal | User-owned planned or grouped eating occasion. States: planned, logged, updated, deleted/removed. | May group Food Logs; time and ownership must be valid. Soft deletion only under policy. High. |
| Food Log | User observation of consumed/planned food. States: logged, corrected, removed. | Must respect user ownership; uncertain entries remain uncertain and never create false nutrition precision. Links Meal/Nutrition Plan. Must build basic. |
| Water Log | User hydration observation. States: logged, corrected, removed. | Positive plausible amount and user-local date context. Links User/Progress. Must build basic. |
| Sleep Observation | User-authorised sleep observation. States: logged, corrected, removed. | Supports non-medical recovery context; interval plausibility required. Sensitive retention/consent. If time allows. |
| Recovery Check-in | User report of energy/fatigue/stress/recovery. States: submitted, superseded. | Produces conservative indicator, not diagnosis. Links User/Assessment/Workout/Recovery Score. If time allows. |
| Dietary Restriction | User-confirmed allergy, intolerance, preference, cultural or religious constraint. States: active, uncertain, withdrawn, superseded. | Allergy/serious restriction constrains all nutrition guidance immediately; uncertainty prompts safe limitation. Links User/Assessment/Nutrition Plan. Must build. |
| Body Measurement | User-authorised physical observation. States: recorded, corrected, removed. | Values require plausible units/ranges; no coercion to provide. Links User/Goal/Progress. Must build basic. |
| Progress Snapshot | Derived, versioned summary for a period. States: calculated, published, superseded, insufficient data. | Must identify source period/data completeness; no causal/medical claims. Links User, Goal, logs, Report. Must build basic. |
| Health Score | Explainable non-medical derived indicator. States: calculated, superseded, unavailable. | Only computed with approved input sufficiency; never diagnoses. Links Progress Snapshot/Assessment. Post-competition unless narrowly defined. |
| Recovery Score | Explainable non-medical recovery indicator. States: calculated, superseded, unavailable. | Uses current authorised recovery/load context; conservative and not clinical. Post-competition. |
| Achievement | Sustainable milestone recognition. States: earned, displayed, withdrawn. | Cannot reward starvation, dangerous volume, or unhealthy weight outcomes. Links evidence from progress/habit/session. If time allows. |
| Progress Report | Periodic user-facing review. States: requested, generating, available, insufficient data, failed, superseded, removed. | Requires minimum data; metrics are deterministic, AI narrative is bounded. Links snapshots/plans/goals. Weekly if time allows. |

### AI, commercial, analytics, and future entities

| Entity | Meaning, owner, lifecycle, and states | Rules, relationships, deletion, expansion, priority |
| --- | --- | --- |
| AI Conversation | User-owned bounded coaching interaction. States: started, active, closed, deleted/retention-held. | Requires consent, safety/eligibility, task purpose, and user isolation. Links Messages, summary, feedback. Must build one flow. |
| AI Message | One user or system/coach message within Conversation. States: accepted, generated, blocked, failed, redacted. | User content is untrusted; generated output is candidate content validated by policy. Links Conversation/Recommendation. Must build. |
| Coach Memory | User-approved durable coaching context. States: proposed, active, expired, edited, withdrawn, superseded. | Must have source/purpose/expiry and user control; no cross-user memory. Links User/AI Conversation/Assessment. High. |
| Recommendation | Governed advice lifecycle. States: proposed, validated, presented, accepted, declined, superseded, blocked. | Must cite current source context/safety outcome; cannot enact high-consequence change autonomously. Links Assessment/Plan/AI. Must build basic. |
| AI Feedback | User/reviewer evaluation of AI output. States: recorded, safety escalated, resolved. | Harmful output triggers review; feedback does not automatically rewrite policy/memory. Links Recommendation/Message. Must build basic. |
| AI Usage Record | Operational/cost record of permitted AI work. States: recorded, reconciled, archived. | Contains minimum necessary task/cost/latency metadata, not raw secrets or private content. Links AI Conversation/Recommendation. High. |
| Subscription | Commercial plan relationship. States: trial, active, past due, paused, cancelled, expired. | Entitlement follows verified commercial state; cannot override safety/consent. Links User/Organisation/Entitlement/Payment Event. Post-competition. |
| Entitlement | Granted capability right. States: pending, active, suspended, expired, revoked. | Derived from subscription/admin/partner source; evaluated at capability use. Links User/Organisation/Subscription. Post-competition. |
| Payment Event | Immutable external commercial event. States: received, verified, applied, disputed, reconciled. | Provider event is idempotent; never casually changed/deleted. Links Subscription/Entitlement/Audit. Post-competition. |
| Analytics Event | Privacy-aware observation of product/operational behaviour. States: accepted, aggregated, archived/expired. | Cannot author domain facts or carry prohibited sensitive payload. Links event source/version only. Must build minimal server events. |
| Wearable Connection | User-authorised external-device relationship. States: connected, paused, revoked, expired. | Consent and provider scope required; revocation stops future use. Links imports/User. Post-competition. |
| Wearable Import | Bounded imported period/provenance. States: received, validated, applied, rejected, expired. | Must not silently overwrite user observations; conflicts are explainable. Post-competition. |
| Vision Asset | Consent-governed user media asset. States: requested, uploaded, approved, rejected, deleted. | Private by default; separate processing consent; no medical claims. Post-competition. |
| Vision Analysis | Derived future media assistance result. States: queued, processed, presented, rejected, expired. | Requires valid asset/consent and safety validation; not a diagnosis. Post-competition. |
| Community Post | Future user-created community content. States: draft, published, hidden, removed. | Visibility/moderation policy applies; no automatic health authority. Post-competition. |
| Moderation Event | Immutable moderation action. States: applied, appealed, upheld, reversed. | Links actor/target/policy reason; restricted audit. Post-competition. |

## 5. Aggregates

| Aggregate root | Transaction boundary and rationale |
| --- | --- |
| User | Coordinates account state, profile preferences, consent references, and ownership boundary. A change must preserve identity, eligibility, and privacy invariants together. |
| Assessment | Coordinates session progress, relevant answers, branching, completion, and resulting safety/readiness state. Completion is atomic at the business level: one coherent version or no completed result. |
| Goal | Coordinates priority, state, realism, and relationship to active plan intent. Goal change may trigger plan review but does not silently mutate plans. |
| Workout Plan | Coordinates its revision, prescriptions, activation/pausing, and eligibility. Sessions are separate aggregates because execution history grows independently. |
| Workout Session | Coordinates session state, set logs, substitutions, completion, and pain reporting. It prevents logging after completion/cancellation. |
| Nutrition Plan | Coordinates guidance version, active state, and restriction-aware applicability. Meal/Food/Water observations are separate user-owned aggregates for independent logging. |
| AI Conversation | Coordinates bounded messages, safe session context, summary state, and deletion request. Durable memory and recommendations are separate because each has independent consent/lifecycle. |
| Recommendation | Coordinates source versions, validation, presentation, user response, and supersession; it protects explainability. |
| Progress Report | Coordinates request/generation/availability/insufficiency state and source snapshot version. |
| Subscription | Coordinates commercial lifecycle and entitlement changes; payment events remain immutable external facts. |

Aggregate boundaries protect business consistency, not a guarantee that every related record changes in one physical transaction. Cross-aggregate work uses explicit domain events, idempotent handlers, version checks, and visible pending/failure states.

## 6. Value Objects

Value objects are immutable, self-validating concepts compared by meaning rather than identity. Replacing one creates a new value and may trigger controlled review; this prevents hidden changes to historical plans, assessments, and reports.

| Value object | Meaning and rule |
| --- | --- |
| Height / Weight / Measurement | Valid quantity plus unit and observation context; conversions are explicit and plausible ranges are enforced. |
| Goal Target / Timeline | Intended outcome, direction, priority, and feasible review window; never authorises unsafe target. |
| Calorie or Nutrition Target | Bounded, explainable plan target with source version; not medical prescription. |
| Macro Target | Optional nutritional composition target consistent with plan/restrictions and user context. |
| Exercise Prescription | Exercise version, permitted form, effort/volume boundary, substitution constraints, and safety notes. |
| Workout Duration / Schedule | Available time, frequency, days, and timezone-aware preferred windows. |
| Equipment Profile | Declared environment, equipment access, space, travel constraint, and flexibility. |
| Dietary Restriction Set | Confirmed allergies, intolerances, preferences, cultural/religious restrictions, and uncertainty. |
| Safety Status | Normal, caution, clearance required, paused, or resolved with reason category and review condition; never diagnosis. |
| Units / Language / Timezone | Supported presentation preferences used consistently by all contexts. |
| Reminder Settings | Opt-in channel, schedule, quiet period, and content preference, always consent-bound. |
| Progress Period / Data Completeness | Defined time window and evidence sufficiency used to prevent misleading reports. |
| Permission Scope | Role, organisation/client boundary, capability, effective period, and purpose. |

## 7. Domain Services

| Domain service | Responsibility and Python ownership |
| --- | --- |
| Assessment Orchestrator | Applies adaptive branches, validation, requiredness, completion, reassessment, and output/readiness rules. Python owns all deterministic behaviour. |
| Safety Evaluator | Evaluates red flags, age/clearance, injury, allergy, dangerous goal, and restrictive states; returns non-diagnostic permitted-action boundary. Python only. |
| Workout Generator | Creates/revises an eligible plan from assessment, goal, equipment, schedule, exercise catalogue, and safety constraints. Python owns filtering and progression rules; AI may explain only. |
| Nutrition Generator | Creates/revises practical guidance respecting restrictions, goal, access, and safety. Python owns restriction/eligibility rules; AI may explain only. |
| Goal Optimizer | Evaluates priority, feasibility, conflicts, and required review; it suggests, never autonomously changes, user goals. Python owns realism thresholds. |
| Recovery Calculator | Produces explainable non-medical conservative recovery category from authorised inputs. Python owns calculation and sufficiency. |
| Health/Progress Score Calculator | Produces versioned, non-medical derived metrics only when data is sufficient. Python owns formula/version. |
| Progress Analyzer | Produces trends, comparisons, data completeness, and report-ready facts without causal claims. Python owns computation. |
| Recommendation Engine | Coordinates rules/context/allowed AI candidate/output validation/recommendation lifecycle. Python owns boundaries, safety, and final validation. |
| Habit Analyzer | Matches small feasible habits and reminders to user constraints/preferences; never uses coercive or harmful incentive logic. |
| Report Composer | Combines deterministic metrics with optional bounded AI narrative; refuses report conclusion when data is insufficient. |
| Entitlement Evaluator | Determines commercial capability access from verified state; never overrides consent/safety. |
| Permission Evaluator | Determines actor/resource/scope/purpose access across user, trainer, admin, and system roles. |

## 8. Business Rules

### Identity, consent, and ownership

- Only an active, authenticated user may create or alter their protected product records.
- Every personal record belongs to one user unless a documented organisation/shared context exists; a role does not imply ownership.
- Consent is purpose/version-specific. Withdrawing optional consent stops future dependent processing and is reflected in the user experience.
- A trainer, support actor, or administrator cannot access private health, AI, or media detail without explicit authorised scope and audit.
- Account suspension blocks protected capability generation while preserving required safety/privacy access routes.

### Assessment and safety

- A personalised workout, nutrition plan, AI recommendation, or derived report requires the applicable current assessment readiness.
- Required safety questions cannot be bypassed for normal personalisation; optional context may be skipped with reduced confidence.
- A completed assessment is immutable in meaning; corrections or changes create a new revision/supersession relationship.
- Hard safety status overrides preferences, plan requests, entitlement, and AI output.
- Serious warning signs, un-cleared significant injury/surgery, dangerous goals, or policy-defined minor risk pause normal generation and direct the user to appropriate professional advice without diagnosis.
- Pain reports immediately trigger safety re-evaluation and may pause a session/plan.

### Goals, workout, nutrition, and recovery

- A user has one active primary goal per applicable planning context; secondary goals are prioritised explicitly.
- A workout plan must respect current equipment, time, experience, stated limitations, and safety status.
- Workout sessions may only log actions that belong to the user’s active/scheduled session; completion cannot be duplicated.
- A nutrition plan may not violate confirmed allergies, intolerances, cultural/religious restrictions, or hard safety boundaries.
- Food/water/measurement/sleep records are observations, not proof of clinical state; corrections retain historical accountability where policy requires.
- Recovery/health indicators are non-medical, explainable, data-sufficient, and conservative; they cannot diagnose conditions.
- Achievements must reward sustainable actions and cannot incentivise starvation, unsafe volume, or harmful weight outcomes.

### Progress, AI, reports, and operations

- Progress claims require minimum relevant data and must distinguish observation from derived trend; no unsupported causal claim is allowed.
- Reports require a defined period, sufficient data, current source versions, and transparent insufficiency behaviour.
- AI may receive only approved, minimum-necessary, current context and cannot access another user’s context.
- AI may explain or suggest permitted options but cannot decide safety, diagnose, change plans/goals, or enforce permissions.
- Every meaningful recommendation retains source context/version, safety outcome, lifecycle state, and user response where applicable.
- AI memory is editable, source-bound, purpose-limited, reviewable, and expires or is superseded when stale.
- Notifications require an applicable preference/consent and must respect quiet/scheduling rules.
- Feature flags, policy changes, privileges, exports, deletions, commercial state, and safety-relevant actions are audited.

## 9. State Machines

| Domain object | States and permitted transitions |
| --- | --- |
| Assessment | Started → In Progress → Reviewable → Completed. In Progress/Reviewable → Cancelled. Completed → Superseded or Archived. In Progress may become Abandoned/Expired by policy but can Resume when eligible. Completion is blocked until required branches/validation are satisfied; completed safety result may be normal, caution, or clearance required. |
| Assessment Result | Current → Stale when review trigger occurs → Superseded when a new approved result exists; Current/Stale may be Blocked by safety. Historical results eventually Archive, never silently change. |
| Safety Review | Normal ↔ Caution as current facts change; Normal/Caution → Clearance Required or Paused on hard rule; Clearance Required/Paused → Resolved only after valid new context/clearance policy. |
| Goal | Draft → Active; Active ↔ Paused; Active → Achieved or Abandoned; any non-archived state → Archived. A new priority/target may create a revision and plan review. |
| Workout Plan | Draft → Generated → Awaiting Review → Active. Active ↔ Paused; Active → Completed or Superseded; any inactive historic state → Archived. A hard safety change moves Active to Paused/review, not silently completed. |
| Workout Session | Scheduled → Active → Paused ↔ Active → Completed. Scheduled/Active/Paused → Skipped or Cancelled. Pain report may force Paused/Restricted review. Completed/Cancelled are terminal except governed correction metadata. |
| Nutrition Plan | Draft → Generated → Awaiting Review → Active; Active ↔ Paused; Active → Completed or Superseded; historic plans → Archived. New restriction causes review/pause. |
| Recommendation | Proposed → Validated → Presented → Accepted or Declined; Validated/Presented → Blocked on safety/policy; Presented/Accepted may become Superseded after relevant change. |
| AI Conversation | Started → Active → Closed; Active → Blocked/Closed on safety or policy; eligible content → deletion requested/retention held. Deletion does not remove required audit evidence. |
| Progress Report | Requested → Generating → Available; Requested/Generating → Insufficient Data or Failed; Available → Superseded/Removed according to policy. Failed may Retry under bounded policy. |
| Notification | Scheduled → Sent → Read or Deleted; Scheduled → Cancelled/Expired; delivery failure may Retry within policy. |
| Subscription | Trial → Active → Past Due → Active or Expired; Active/Past Due → Cancelled/Paused; terminal state may be superseded by a later verified purchase. Entitlement changes follow verified commercial events. |
| Privacy Request | Requested → Verified → In Progress → Completed; Requested/Verified → Cancelled when permitted; In Progress → Held/Rejected only with policy reason and user-safe explanation. |

## 10. Domain Events

| Event | Meaning | Consumers |
| --- | --- | --- |
| User Registered / Verified / Suspended | Identity state changed. | Profile setup, notification, audit, entitlement, analytics. |
| Consent Granted / Withdrawn | Processing permission changed. | AI context, media, notifications, privacy/audit, feature gating. |
| Assessment Started / Saved / Completed / Superseded | Assessment lifecycle changed. | Dashboard, planning eligibility, AI context, analytics, notifications. |
| Safety Status Changed / Pain Reported | Permitted-action boundary changed. | Workout/Nutrition/AI restrictions, dashboard, audit, notification. |
| Goal Activated / Updated / Achieved | User intent changed. | Plans, progress, reports, achievements, AI. |
| Workout Plan Generated / Activated / Paused | Training guidance lifecycle changed. | Dashboard, sessions, notifications, reports. |
| Workout Session Started / Finished / Skipped | Execution evidence changed. | Progress, recovery, achievements, reports, analytics. |
| Nutrition Plan Generated / Restriction Updated / Meal Logged | Nutrition context changed. | Dashboard, progress, AI, reports. |
| Progress Updated / Snapshot Calculated | Derived user trend changed. | Reports, dashboard, goals, AI. |
| Report Generated / Insufficient Data | Periodic review outcome changed. | Dashboard, notification, AI, analytics. |
| AI Recommendation Created / Blocked / Feedback Received | Governed AI lifecycle changed. | Dashboard, safety review, quality analytics, audit. |
| Notification Scheduled / Delivered | User communication lifecycle changed. | Notification preference and operational monitoring. |
| Subscription Activated / Entitlement Changed | Commercial access changed. | Capability checks, billing, notification, audit. |
| Privacy Request Verified / Completed | Privacy lifecycle changed. | Access restriction, export/deletion work, audit. |

Events are facts after a successful domain transition. Consumers must be idempotent, preserve ordering expectations where material, and never use an event to bypass the originating aggregate’s current safety/permission state.

## 11. Domain Policies

| Policy | Rule set |
| --- | --- |
| Safety Policy | Defines normal/caution/pause/clearance boundaries, red flags, non-diagnostic language, feature restrictions, escalation, and review conditions. |
| Privacy Policy | Defines minimisation, consent, purpose, access, export, correction, deletion, retention exception, media, and logging controls. |
| Recommendation Policy | Defines eligible context, Python/LLM boundary, source traceability, explanation, user review, prohibited advice, and fallback. |
| Assessment Policy | Defines modes, question versions, requiredness, branching, save/resume, completion, reassessment, and stale-result rules. |
| Workout Policy | Defines eligible plan creation, progression, substitution, pain response, session completion, and sport boundaries. |
| Nutrition Policy | Defines restriction handling, food uncertainty, safe/non-medical guidance, dangerous-goal limits, and plan review. |
| Progress and Report Policy | Defines sufficiency, derived metric interpretation, report periods, correction, retention, and no-causal-claim boundary. |
| AI Policy | Defines permitted tasks, model routing, context minimisation, memory, output validation, injection resistance, cost/usage control, and incident review. |
| Notification Policy | Defines opt-in, channels, quiet periods, safety/transactional exception, frequency, and delivery retry. |
| Permission Policy | Defines roles, scopes, ownership, least privilege, sensitive access, service identity, and audit. |
| Retention Policy | Defines active, archived, expired, deletion, legal/security/financial exceptions, and restoration requirements by domain class. |
| Commercial Policy | Defines trial, entitlement, cancellation, refund/dispute, and access change rules without compromising user safety/privacy. |

## 12. Domain Validation

Entity validation ensures each entity’s own meaning is coherent: a session cannot complete twice, a goal has a valid state, a measurement has a sensible unit, and a recommendation has source context. Business validation applies context rules: an active user requires current consent/assessment to generate a plan, an active plan must be eligible, and a report requires sufficient source data.

Cross-entity validation checks relationships: a set belongs to the user’s session and prescription, a nutrition plan uses the user’s active restrictions, a recommendation references current approved context, and a membership grants the claimed scope. State validation enforces only permitted lifecycle transitions. Permission validation occurs before access and again where resource ownership matters. Safety validation is deterministic Python logic applied before and after relevant transitions; it takes precedence over user preference and AI output.

Transport boundary validation checks basic request shape; domain services and aggregates enforce business meaning; repositories enforce persistence uniqueness/version constraints; middleware handles authentication, request context, common rate limits, and basic security. No validation layer alone is sufficient for a sensitive action.

## 13. Competition Scope

| Must Build | If Time Allows | Post Competition |
| --- | --- | --- |
| User, Session, Consent, Assessment/Session/Result, Safety Review, Goal, Exercise/Prescription subset, Workout Plan/Session/Set Log/Pain Report, Nutrition Plan, Food/Water Log, Dietary Restriction, Body Measurement, Progress Snapshot, bounded AI Conversation/Message/Recommendation/Feedback, Analytics Event, Audit Event, core value objects and safety/permission services. | Habit, Sleep Observation, Recovery Check-in, Achievement, weekly Progress Report, Coach Memory controls, Support Ticket, Notification, limited admin/System Setting. | Organisation/Membership, Subscription/Entitlement/Payment, health/recovery scores, advanced reports, wearables, vision, community/moderation, broad sport and enterprise workflows. |

This scope prioritises a complete domain loop—identity → assessment/safety → goal/plan → execution/logging → progress → bounded AI explanation—over a large catalogue of shallow entities.

## 14. Judge Review

| Criterion | Evaluation |
| --- | --- |
| Business modelling | Strong: core concepts, ownership, aggregates, policies, and lifecycles reflect real product decisions rather than screens or storage tables. |
| Architecture quality | Strong: bounded contexts and domain/event boundaries keep Python business rules independent of controllers, UI, AI providers, and databases. |
| Scalability and maintainability | Strong if aggregate/event boundaries and explicit versioning are retained during implementation. |
| Technical maturity | Strong: safety, privacy, explainability, idempotency, retention, and deferred complexity are named as domain concerns. |

**Strengths:** explicit ownership, deterministic safety, rich lifecycle modelling, coherent AI boundary, and realistic competition focus.  
**Weaknesses:** the full future entity set is large; a team can dilute quality by treating every documented entity as immediate implementation work.  
**Risks:** inconsistent ubiquitous language, rules leaking into controllers, overusing events for simple synchronous decisions, and unvalidated safety policy.  
**Likely questions:** Why are these aggregate boundaries chosen? What happens when assessment changes? How does AI fail safely? How are trainer/admin permissions constrained? Which entities are actually demonstrated?  
**Score:** 93/100 as a domain blueprint. First-place strength requires showing a narrow domain loop with tests proving state, safety, and ownership rules.

## 15. Startup Review

The domain can survive scaling because it separates individual ownership from future organisation tenancy, isolates commercial and AI concerns, preserves versions, and models high-volume observations separately from plan aggregates. It should be simplified in the first release by treating reports, notifications, scores, subscriptions, organisations, wearables, vision, and community as explicit future contexts rather than partial implementations.

Premium candidates are advanced reports, sport-specific programmes, deeper adaptive coaching, approved integrations, and human-coach collaboration. Build now the safety/assessment/plan/execution/progress loop and its audit/permission boundary. Long-term platform value comes from trustworthy longitudinal user context, explainable plan history, safe AI orchestration, and domain rules that can serve consumer, coach, and enterprise products without a rewrite.

## 16. Definition of Done

Sprint 2.6 is complete only when core entities, ownership, lifecycles, transitions, aggregates, value objects, domain services, business rules, domain events, policies, validation boundaries, competition scope, judge/startup reviews, and README link are documented; no implementation code exists; and future complexity is explicitly deferred rather than implied in the competition build.
