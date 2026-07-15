# RAHFIT AI — Enterprise Database Blueprint

**Status:** Official pre-implementation database specification  
**Scope:** Architecture and governance only. This document deliberately contains no implementation, database schema, JSON, models, or code.

## 1. Database Philosophy

### Why MongoDB

MongoDB is suitable for RAHFIT AI because the product manages evolving, user-centred records: assessments change by version, plans vary by goal and context, activity logs are time-series-like, and AI interactions contain flexible context. Its document model supports cohesive aggregates that are commonly read together, while avoiding premature relational joins across a rapidly changing product domain.

MongoDB is not a reason to abandon disciplined data design. Each collection has one clear owner, lifecycle, validation policy, access boundary, and query purpose. Cross-collection duplication is permitted only when it makes a critical read path safer or faster, and every copied value has a defined source of truth and refresh policy.

### Scalability strategy

The initial design favours a single logically central deployment with replica-based availability, well-bounded documents, carefully selected indexes, and asynchronous treatment of expensive reporting and analytics. Scale is reached in stages: archive high-volume history; isolate analytical workloads from operational workloads; split media from operational records; then introduce partitioning or sharding only after measured growth and access patterns justify a shard key.

No collection may rely on unbounded embedded arrays, unbounded conversations, unbounded event history, or user-wide scans. High-write logs, notifications, audit events, AI usage, and analytics are designed for time-bounded access and retention from the beginning.

### Document strategy

- Embed small, bounded data that is owned by one aggregate and read or written atomically with it.
- Reference independently growing records, reusable catalogue data, confidential data, cross-user data, and time-series-like logs.
- Preserve immutable versions for assessments, plans, recommendations, reports, consent, and material derived results.
- Treat user-entered observations as distinct from derived scores and AI-generated advice.
- Store media content outside operational documents; retain only controlled metadata and ownership references in the database.
- Use soft deletion for user-facing operational records where recovery/audit is needed; use hard deletion or irreversible anonymisation when a verified privacy-deletion workflow requires it.

### Naming conventions

Collection names use lowercase plural nouns. Field names use lower camel case. Identifiers are immutable and opaque. Timestamp names use `createdAt`, `updatedAt`, `deletedAt`, and `occurredAt` according to their meaning. References are named for the owned entity, such as `userId`, `planId`, or `organisationId`. Boolean fields read as a condition. Enumerated states use controlled, documented values. All stored times are UTC; presentation converts to the user’s locale and timezone.

### Versioning strategy

Every changing business artefact carries an explicit version or revision identity where historical interpretation matters. An approved plan, assessment, recommendation, consent record, report, prompt template, and feature configuration must remain interpretable after newer versions exist. Changes that alter user-facing guidance are append-only revisions, linked to superseded records and a reason for change. Data migrations are governed as backward-compatible, observable, reversible transformations with ownership and retirement criteria.

## 2. Collections

| Domain | Collections | Responsibility |
| --- | --- | --- |
| Identity and governance | users, userConsents, userSessions, organisations, organisationMemberships, roles, auditLogs, systemSettings, featureFlags, supportTickets | Identity, permission boundaries, user choices, operational control, and traceability. |
| Assessment and planning | assessments, assessmentAnswers, goals, habits, planTemplates, workoutPlans, nutritionPlans, recoveryPlans, planChangeRequests | Baseline, goals, approved coaching plans, and controlled plan evolution. |
| Fitness catalogue and execution | exercises, exerciseMedia, workoutSessions, workoutSetLogs, activityLogs | Reusable exercise knowledge and user training activity. |
| Nutrition and wellbeing | meals, foodCatalog, foodLogs, waterLogs, sleepLogs, bodyMeasurements, healthScores, progressPhotos | Nutrition guidance/logging and user-authorised wellbeing observations. |
| Progress and engagement | progressSnapshots, reports, achievements, notifications, notificationDeliveries | Derived progress, review cycles, motivation, and user communication. |
| AI governance | aiSessions, aiMessages, aiMemory, promptTemplates, promptLogs, recommendations, aiFeedback, aiUsage | Safe, traceable, cost-aware coaching interactions and recommendation lifecycle. |
| Commercial and operations | subscriptions, paymentEvents, entitlementHistory, analyticsEvents, dataExportRequests, deletionRequests | Entitlements, billing traceability, privacy operations, and product measurement. |
| Future-capability boundary | wearableConnections, wearableDataImports, visionAssets, visionAnalyses, communityPosts, communityModerationEvents | Deferred integrations and features with separate consent, retention, and safety controls. |

## 3. Collection Specifications

The following catalogue defines the minimum architectural contract for each collection. “Audit” means standard creation/update actor and time metadata, with immutable audit events for sensitive actions. Retention periods are policy categories; exact durations must be approved by legal, product, and security owners before implementation.

### Identity and governance

| Collection | Purpose and required information | Optional information and relationships | Validation, indexes, deletion, audit, retention, and expansion |
| --- | --- | --- | --- |
| users | Account owner; immutable identifier, verified contact identifier, account state, locale, timezone, accepted-policy state, created/updated times. | Profile preferences, display name, units, accessibility settings; owns nearly all personal records. | Contact identifier is unique; account state is controlled. Soft delete/anonymisation workflow; full audit. Retain while active plus policy period. Future: delegated accounts and regional residency. |
| userConsents | Versioned evidence of consent and withdrawal; user reference, policy type/version, decision, occurrence time. | Collection channel, locale, legal basis. | One current decision per user/policy type; historical records immutable. No ordinary soft delete; retain per legal policy. Future: jurisdiction-specific consent. |
| userSessions | Security session/device lifecycle; user reference, session state, issued/expiry/revocation times. | Device and risk metadata, never raw secrets. | Lookup by user/state and expiry; TTL after security-retention period. Revocation is auditable. Future: device trust. |
| organisations | Future gym, university, employer, or enterprise tenant; identifier, name, state, owner, created/updated times. | Branding, locale, billing settings. | Unique tenant identity; active-state validation. Soft delete with contractual retention; full audit. Future: reseller hierarchy. |
| organisationMemberships | Grants a user scoped access to an organisation; organisation/user references, role, state, effective dates. | Team, coach-client scope, invitation source. | Unique active membership per organisation/user; indexes in both access directions. Soft delete/revocation, audit retained. Future: attribute-based permissions. |
| roles | Controlled permission definitions; role name, scope, permission set, version, state. | Description and delegated constraints. | Unique role/scope/version; only authorised operators may change. Audited and retained as governance history. Future: custom enterprise roles. |
| auditLogs | Immutable record of sensitive action; actor, action, target type/reference, occurrence time, outcome, correlation reference. | Reason, redacted context, originating service. | Time and actor/target indexes; access restricted. No soft delete; retention is security/legal policy, then archive. Future: external security-event export. |
| systemSettings | Versioned global operational settings; setting key, approved value reference, version, state, approval metadata. | Rollout window and rationale. | Unique active key; privileged access only; immutable history. Retain for operational history. Future: regional overrides. |
| featureFlags | Controlled capability rollout; flag key, state, targeting policy version, owner, timestamps. | Experiment reference, expiry, rationale. | Unique flag key; expiry review required. Audited; archive retired flags. Future: organisation and cohort targeting. |
| supportTickets | User support case; requester, category, state, priority, created/updated times. | Sanitised conversation, assigned operator, attachments references. | Access limited to authorised support scope; state transitions controlled. Soft delete only where appropriate; retention policy by category. Future: SLA and enterprise support. |

### Assessment and planning

| Collection | Purpose and required information | Optional information and relationships | Validation, indexes, deletion, audit, retention, and expansion |
| --- | --- | --- | --- |
| assessments | Immutable assessment header; user, assessment type/version, completion state, completion time, safety disposition. | Plan context, reassessment reason, reviewer reference. | One current approved assessment per applicable type; user/time and state indexes. Never silently mutate completed content; retain while account exists plus policy period. Future: clinician-reviewed flows. |
| assessmentAnswers | Answer-level assessment record; assessment and user references, question version, answer classification, occurrence time. | Normalised answer values and user-provided notes. | Must match a valid assessment version; sensitive answers access-controlled. Append-only after completion; retention follows assessment. Future: adaptive assessments. |
| goals | User-stated objective; user, goal type, target direction, state, start date, review date. | Target range, motivation, constraints, priority. | One active primary goal rule; indexes by user/state/review date. Soft delete/revision with audit. Retain with user history. Future: team/coached goals. |
| habits | Recurring user behaviour target; user, habit type, schedule, state, start date. | Reminder preference, flexible completion criteria. | Schedule and state validation; user/state index. Soft delete and audit. Retain until user deletion policy. Future: habit groups. |
| planTemplates | Curated reusable plan blueprint; owner, plan domain, version, approval state, applicability criteria. | Content metadata, localisation, evidence notes. | Unique template/version; privileged publishing, immutable published versions. Archive superseded versions. Future: expert marketplace content. |
| workoutPlans | User-approved training plan; user, source assessment, plan version, effective period, approval state. | Template reference, equipment/time constraints, change reason. | Only one active plan per applicable context; user/effective-state index. Supersede rather than overwrite; retain historical plans. Future: coach-owned plans. |
| nutritionPlans | User-approved nutrition guidance; user, source assessment, version, effective period, approval state. | Preferences, cultural context, substitutions, target rationale. | Safety and preference validation; current-plan lookup index. Supersede rather than overwrite; retention as plan history. Future: dietitian review. |
| recoveryPlans | Guidance for sleep, mobility, rest, and recovery; user, source assessment, version, state, effective period. | Sport/training-load context, reminders. | User/state/effective-period index; controlled safety language. Versioned retention. Future: wearable-informed recovery. |
| planChangeRequests | User, coach, or system-initiated request to alter a plan; target plan, requester, reason category, state, created time. | Proposed constraints, reviewer notes. | Controlled state transitions; target-plan/state index. Audit required; retain with plan lineage. Future: approval workflows. |

### Fitness, nutrition, and wellbeing

| Collection | Purpose and required information | Optional information and relationships | Validation, indexes, deletion, audit, retention, and expansion |
| --- | --- | --- | --- |
| exercises | Curated exercise catalogue; identifier, name, movement category, safety level, publishing state, version. | Equipment, alternatives, instructions, localisation. | Unique canonical identity/version; privileged publishing. Archive retired content, never remove referenced versions. Future: sport-specific catalogue. |
| exerciseMedia | Metadata for approved exercise media; exercise reference, media type, storage reference, version, state. | Captions, locale, accessibility descriptions. | Storage reference unique; access controlled; retain with exercise version. Future: expert review and licensing. |
| workoutSessions | One planned or completed user session; user, plan reference/version, scheduled or occurred time, state, completion result. | Perceived effort, duration, modification reason. | User/time and plan/state indexes; state transitions controlled. Soft delete for drafts only; audit completed changes. Retain for progress history. Future: coach review. |
| workoutSetLogs | Detailed bounded set/exercise execution; user, session, exercise reference/version, sequence, occurrence time. | Load, repetitions, duration, effort, notes. | Unique session/exercise/sequence; session and user/time indexes. Correct by revision, not silent overwrite; retain with session. Future: wearable source. |
| activityLogs | General activity observation; user, activity type, start/occurrence time, source, duration or quantity. | Route/media reference, intensity, device provenance. | User/time/type index; source validation. Soft delete/revision; retention by source and consent. Future: imported wearable activity. |
| meals | User meal-plan or meal-log grouping; user, meal date/time, meal type, state. | Plan reference, title, notes, cultural context. | User/time index; child food logs must share ownership. Soft delete draft records; retain with nutrition history. Future: shared meal templates. |
| foodCatalog | Curated food reference; canonical identity, source, serving basis, publishing state, version. | Nutrient detail, locale aliases, brand data. | Unique source/canonical identity; provenance required. Archive superseded entries. Future: regional providers. |
| foodLogs | User food observation; user, meal reference when present, food reference or user description, occurrence time, quantity basis. | Estimated nutrition, confidence, image reference. | User/time and meal indexes; source and confidence required for derived entries. Correct by revision; retain per user nutrition policy. Future: barcode and vision assist. |
| waterLogs | Hydration observation; user, occurrence time, amount, unit/source. | Reminder context and notes. | Positive quantity and valid unit; user/time index. Soft delete/correction audit; retain for defined wellbeing history. Future: smart-bottle import. |
| sleepLogs | User-authorised sleep observation; user, sleep interval, source, record state. | Quality, notes, device provenance. | Valid chronological interval; user/time index. Sensitive access handling; retention depends on consent/source. Future: sleep-stage import. |
| bodyMeasurements | User-authorised body measurement; user, measurement type, value/unit, occurrence time, source. | Context and confidence. | Valid unit/range policy and user/time/type index. Correct by revision; sensitive retention and deletion controls. Future: regional units. |
| healthScores | Derived, non-diagnostic wellbeing/progress score; user, score type/version, source-window reference, calculated time, confidence/data completeness. | Explanation and contributing categories. | Must identify derivation version; user/score/time index. Immutable calculation record; retention follows progress policy. Future: validated score models. |
| progressPhotos | User-controlled progress media metadata; user, storage reference, capture time, consent state, visibility. | Body-area category and comparison preference. | Private by default; explicit consent for processing/sharing; strict user/time index. Delete on verified request; limited retention. Future: vision feature only with separate consent. |

### Progress, AI, commercial, and future domains

| Collection | Purpose and required information | Optional information and relationships | Validation, indexes, deletion, audit, retention, and expansion |
| --- | --- | --- | --- |
| progressSnapshots | Periodic derived view of progress; user, period, calculation version, data-completeness status, calculated time. | Trend summaries and source references. | Unique user/period/calculation version; immutable output, recalculation creates revision. Retain as report lineage. Future: coach comparison. |
| reports | User-facing weekly/monthly review; user, report type/period, source snapshot, version, publication state. | Narrative, next focus, acknowledgement time. | Unique user/report type/period/version; only publish with data-completeness rule. Supersede revisions; retain progress history. Future: export/share scope. |
| achievements | Sustainable milestone record; user, achievement type/version, earned time, source evidence. | Display state and user acknowledgement. | Unique user/achievement/source rule; prohibit unsafe incentive classes. Retain unless user deletes account. Future: team challenges. |
| notifications | Intended user communication; user, notification type, channel, state, scheduled time, priority. | Localised content reference, deep-link target. | User/state/schedule and delivery indexes; preference and consent checks required. TTL/archive after operational retention; audit critical notices. Future: organisation campaigns. |
| notificationDeliveries | Channel delivery attempt; notification reference, provider reference, outcome, occurrence time. | Failure category and retry context. | Unique provider attempt reference; time/outcome indexes. TTL/archive after operational retention. Future: provider failover. |
| aiSessions | Governed coaching conversation/session; user, purpose, state, started/ended time, applicable consent and safety state. | Plan/assessment context references. | User/time/state index; safety disposition required. Soft delete is not used for security-relevant sessions; retention is configurable and consent-bound. Future: coach handoff. |
| aiMessages | Bounded conversation messages; session, actor type, occurrence time, content classification, safety status. | Redacted content reference, attachments references. | Session/time sequence index; content access restricted and redacted for operations. Archive or delete per AI-memory consent/retention. Future: multilingual evaluation. |
| aiMemory | User-approved durable coaching memory; user, memory category, source reference, confidence, state, review time. | Expiry, user edit, consent scope. | One active item per user/category/source rule; user/category/state index. User can review/delete; minimal retention. Future: retrieval service. |
| promptTemplates | Approved AI instruction template; purpose, version, approval state, owner, effective time. | Evaluation notes and localisation. | Unique purpose/version; published versions immutable. Archive history; privileged audit. Future: model-specific variants. |
| promptLogs | Trace metadata for AI invocation; session/reference, template version, model/provider identity, safety outcome, occurrence time. | Redacted context fingerprint and latency. | Time/provider/outcome indexes; never store secrets. TTL/archive under AI governance policy. Future: evaluation datasets. |
| recommendations | AI or rule-based advice lifecycle; user, recommendation type, source context/version, state, created time, safety status. | Explanation, user response, superseding reference. | User/state/time and source-version indexes; immutable approved content, transitions audited. Retain for explainability. Future: human review. |
| aiFeedback | User or reviewer evaluation of AI output; user, target reference, feedback type, occurrence time. | Rating, comment, harm/safety flag. | Target/time indexes; safety flags escalate. Retain as quality evidence, redacted for analytics. Future: structured evaluator feedback. |
| aiUsage | Cost and capacity metering; user/tenant scope, invocation reference, model, usage period, token/cost category. | Provider latency and quota context. | Invocation uniqueness; time/user/model indexes. Archive after finance/operations retention. Future: chargeback. |
| subscriptions | Subscription lifecycle; account scope, plan identity/version, state, effective dates, provider customer reference. | Trial, cancellation reason, commercial terms reference. | One active entitlement source rule; account/state/effective indexes. No silent deletion; finance retention and audit. Future: organisation billing. |
| paymentEvents | Immutable billing provider event record; provider event reference, account scope, event type, occurrence time, processing state. | Redacted reconciliation detail. | Provider event reference unique; time/state indexes. No soft delete; retain per financial policy. Future: multiple providers. |
| entitlementHistory | Immutable history of access grants; account scope, entitlement, source, effective interval, state. | Reason and related subscription. | Account/entitlement/time index; consistency with billing decision required. Retain commercial history. Future: partner entitlements. |
| analyticsEvents | Privacy-aware product event; pseudonymous actor scope, event name/version, occurrence time, context category. | Aggregated experiment or platform context. | Event/time and event/version indexes; prohibited sensitive payload policy. TTL/archive and aggregation strategy. Future: warehouse export. |
| dataExportRequests | Privacy export request lifecycle; user, request state, requested time, verification state. | Delivery reference and expiry. | One active request rule; user/state index; access audited. TTL for delivered package metadata; retain request evidence per policy. Future: organisation export. |
| deletionRequests | Verified account/data deletion workflow; user, scope, state, requested/verified/completed times. | Holds, exceptions, completion evidence. | Controlled state transitions and privileged review; user/state index. Retain evidence after deletion/anonymisation. Future: legal-hold workflow. |
| wearableConnections | Future third-party connection consent; user, provider, state, consent scope, connected time. | Provider account reference, sync settings. | Unique user/provider connection; secret material externalised. Revoke and delete per consent. Future: organisation device programmes. |
| wearableDataImports | Imported wearable batch metadata; user, connection, data period, source, processing state. | Provenance, error summary. | Unique connection/source-period rule; user/time index. Retention by consent/source agreement. Future: streaming ingestion. |
| visionAssets | Future image/video processing asset metadata; user, storage reference, consent scope, capture time, state. | Media classification and expiry. | Separate explicit consent; storage reference unique; private by default. Short retention/deletion controls. Future: form or meal assistance. |
| visionAnalyses | Future derived vision output; asset, analysis version, purpose, result state, created time. | Confidence and user feedback. | Must reference valid consent and asset; asset/time index. Immutable result with expiry; no medical claims. Future: human review. |
| communityPosts | Future moderated community content; author, visibility scope, state, created time. | Media reference and topic. | Content policy/moderation state required; visibility/time indexes. Soft delete/moderation audit; retention policy. Future: groups/challenges. |
| communityModerationEvents | Immutable community safety action; actor, target, action, reason, occurrence time. | Appeal state. | Target/time and actor/time indexes; restricted access. Retain moderation history. Future: automated triage. |

## 4. Relationships and Data Ownership

The user is the primary owner of personal profile, consent, assessment, goals, plans, activity, nutrition, wellbeing, progress, AI, notification, support, and privacy-request records. An organisation owns its own configuration and membership boundary, never the user’s private health record by default. A membership grants defined access; it does not transfer ownership.

The principal relationship flow is:

**User → consent/profile → assessment → goals and approved plans → sessions/logs → progress snapshots → reports/achievements.**

AI sessions, messages, memory, prompt logs, usage, feedback, and recommendations link to the user and to the specific assessment/plan/context version that informed them. This enables explanation without mutating historical context. Subscription and payment records link to the individual or organisation account scope and create entitlement history; they do not become the authority for personal-health ownership.

Parent-child records use references when children can grow independently: assessment to answers; workout session to set logs; meal to food logs; notification to deliveries; AI session to messages; organisation to memberships. Children must carry enough owner context to enforce access safely and to support efficient owner-scoped queries.

Many-to-many relationships are represented through explicit relationship records rather than uncontrolled arrays. Examples include users and organisations through memberships, users and roles through memberships/role assignments, plans and reusable catalogue items through bounded plan content references, and future users and community groups/challenges through membership records. These relationship records carry scope, state, effective dates, and auditability.

## 5. Data Lifecycle

1. **Registration:** a user account, consent evidence, and short-lived security session are created under controlled access and audit rules.
2. **Onboarding and assessment:** preferences, answers, and a completed assessment version establish the current personalisation baseline. Safety-sensitive outcomes may pause automation.
3. **Plan and recommendation approval:** goals and approved plan revisions link to the assessment and applicable constraints. AI recommendations retain source context and user response.
4. **Daily activity:** workouts, meals, food/water/sleep/activity logs, and measurements are recorded as user-owned observations. Corrections are revisions or auditable state changes.
5. **Derived progress:** scheduled or requested processing creates versioned progress snapshots, health scores where appropriate, and reports only when data sufficiency rules are met.
6. **Engagement:** notifications, achievements, and AI follow-up use current consent, preference, entitlement, and safety state.
7. **Analytics:** privacy-aware events are separated from operational records, aggregated, and archived on a shorter/high-volume lifecycle.
8. **Lifecycle closure:** inactive operational data is archived according to policy. Export and deletion requests follow verified workflows; legal/financial/security exceptions are documented, minimised, and disclosed.

## 6. Index Strategy

### Unique indexes

Use unique indexes for canonical identity and replay protection: verified user contact identifiers; active organisation identity where applicable; active membership per organisation/user; role and published-template versions; exercise and food source identity; provider payment-event references; provider delivery-attempt references; feature-flag keys; and idempotent external import references. Unique indexes enforce business invariants that cannot be safely delegated to application timing.

### Compound indexes

Compound indexes serve the core owner-scoped product paths: user plus state plus effective date for plans/goals; user plus occurrence time for logs; user plus period/version for snapshots and reports; session plus sequence for set logs and AI messages; organisation plus role/state for membership checks; and account plus entitlement/state/effective time for access decisions. Index order follows observed equality filters first, then sort fields, and must be validated against actual query plans before release.

### TTL indexes

TTL is appropriate only for data whose expiry is automatic and policy-approved: expired sessions, temporary notification-delivery operational detail, short-lived export-package metadata, temporary processing artefacts, selected high-volume prompt metadata, and analytics-event raw detail after aggregation. TTL is not appropriate for audit evidence, payments, approved plans, assessments, reports, or user records whose removal requires verified policy workflows.

### Performance considerations

- Every index has an owner, query justification, size budget, and review date; unnecessary indexes slow writes and increase cost.
- Critical screens use bounded, owner-scoped pagination; no offset-based large scans or unrestricted search across private records.
- Reporting, analytics, and AI evaluation use asynchronous/derived views so they do not compete with daily logging.
- Documents remain bounded; large media, conversation histories, and dense event streams are externalised or partitioned by time.
- Index usage, slow queries, document size, write latency, archival throughput, and storage growth are monitored continuously.

## 7. Security and Privacy

Sensitive classes include identity/contact data, credentials, consent, assessment answers, health-adjacent observations, body measurements, progress media, AI conversation content, payment-provider references, support content, and audit evidence. Data collection follows minimisation: collect only what supports an explicit product purpose and explain that purpose to the user.

Passwords are never stored as recoverable values; only a modern, salted, adaptive password-verification representation is retained. Secrets, payment instruments, and provider credentials are not stored in ordinary application records. Sensitive data is encrypted in transit and at rest, with additional field-level protection or external secret handling for the most sensitive values. Keys are separated from encrypted data, access is least-privilege, and key rotation is governed and tested.

Health-adjacent data is private by default and must not be treated as a medical diagnosis. Access is enforced by user ownership, organisation membership scope, role, purpose, and consent. Trainer/coach access requires explicit grant and is auditable. Support access is purpose-bound, limited, and logged. Analytics uses pseudonymous or aggregated signals and excludes raw sensitive content unless there is a specific approved purpose.

Audit logs record sensitive reads where appropriate, permission changes, exports/deletions, plan overrides, financial events, administrative changes, and safety-relevant AI events. Audit records are immutable, access-controlled, redacted, and retained under security/legal policy. Privacy operations provide consent withdrawal, export, correction where applicable, deletion, retention exceptions, and transparent status.

## 8. Backup Strategy

Automatic encrypted backups run on a defined schedule with point-in-time recovery where supported. Backup coverage includes operational data, configuration/metadata needed for restoration, and documented dependencies for externally held media and secrets without copying raw secrets into backups unnecessarily. Backup access is restricted, monitored, and tested separately from production access.

Manual, labelled backups are permitted before high-risk approved changes and release milestones, with a named owner, expiry date, and restoration instructions. They are not a substitute for automated recovery.

Restore strategy requires documented recovery-point and recovery-time objectives by data class, a staged restore environment, integrity verification, access-control validation, and a business sign-off check before declaring recovery complete. Restore exercises occur regularly and after material architecture changes. Disaster recovery includes incident roles, communication, dependency-failure plans, regional/provider outage assumptions, escalation paths, and a post-incident review process.

## 9. AI Data Layer

| Capability | Database responsibility | Governance requirement |
| --- | --- | --- |
| AI memory | Retain only user-approved, useful, reviewable durable context such as stable preferences or confirmed constraints. | User-visible control, expiry/review, source lineage, purpose limitation, and deletion support. |
| AI sessions | Bound a coaching interaction and associate it with safety, consent, and applicable plan/assessment context. | Explicit purpose, state, access scope, and retention category. |
| Conversation history | Preserve messages needed for continuity, support, or evaluation without unlimited raw history. | Content classification, minimisation, redaction, archive/deletion policy, and restricted access. |
| Prompt history | Preserve approved template/version and trace metadata for reproducibility. | No secrets; raw sensitive context is minimised/redacted; publication is controlled. |
| Recommendation history | Record advice, source context/version, safety disposition, user decision, and supersession. | Explainability, auditability, and prohibition of unsafe autonomous changes. |
| Feedback | Capture usefulness, correction, dissatisfaction, and safety feedback as distinct signals. | Escalation path for harmful/unsafe feedback; analysis uses redaction/pseudonymisation. |
| Token/model usage | Measure model/provider usage, latency, cost category, quota, and failure outcomes. | Financial/operational retention without storing unnecessary user content. |
| Vector readiness | Keep durable memory/context source references and consent scopes independent from any retrieval technology. | Do not introduce vector storage until a validated use case, retrieval evaluation, consent policy, and deletion mechanism exist. |

AI records must never imply a clinical diagnosis, must preserve the constraints used for consequential recommendations, and must support investigation of safety incidents without creating indefinite surveillance of users.

## 10. Future Scalability

For millions of users, scale horizontally only after measured thresholds are reached. Use owner-scoped access patterns, time-bounded collections, archival, asynchronous derivation, media separation, and analytics isolation to delay disruptive redesign. Future partitioning/sharding must follow observed access distribution and avoid keys that create single-user or time-based hotspots.

For gyms, coaches, and enterprise customers, organisations and membership scopes provide the tenancy boundary. Organisation access never overrides private ownership automatically; only defined consent and role grants expose the minimum needed data. Enterprise requirements may add contractual retention, regional residency, audit export, and organisation-specific settings without altering the individual core record ownership.

For a mobile application, stable opaque identifiers, UTC timestamps, revision/version metadata, idempotent import semantics, and sync-aware conflict policy support intermittent connectivity and safe retries. For wearables, connection consent and import provenance keep external feeds isolated from manual records and allow revocation. For AI vision, separate consent, short-lived media metadata, external media storage, analysis-version lineage, and a non-medical safety policy prevent vision features from contaminating the core coaching data lifecycle.

## 11. Definition of Done

Database implementation may begin only when all of the following are approved:

- Every collection has a named business owner, data classification, retention class, access boundary, and source-of-truth decision.
- Critical product journeys have documented read/write access patterns, expected growth, and reviewed index rationale.
- Core ownership and tenant boundaries are approved, including user, coach, support, administrator, and organisation scopes.
- Assessment, plan, recommendation, report, consent, and entitlement versioning/lifecycle rules are unambiguous.
- Privacy requirements cover minimisation, consent, export, correction, deletion, retention exceptions, and sensitive-media handling.
- Security requirements cover least privilege, encryption, credential protection, auditability, secret handling, and incident response.
- Backup, restoration, recovery objectives, and disaster-recovery exercises have accountable owners and acceptance evidence.
- AI data has approved memory, conversation, prompt, recommendation, feedback, safety, and retention policies.
- MVP collections are explicitly marked; deferred enterprise, wearable, community, and vision domains have no accidental dependency in the first release.
- Product, engineering, security, and stakeholder reviewers agree that the blueprint supports a focused first release and a controlled commercial evolution.
