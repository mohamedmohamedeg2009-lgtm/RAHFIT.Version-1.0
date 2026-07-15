# RAHFIT AI — Enterprise Implementation Plan

**Status:** Official Sprint 2.8 implementation roadmap  
**Scope:** Sequencing, delivery governance, risk, quality, and release planning only. This document contains no implementation, code, APIs, schemas, or frontend artefacts.

## 1. Development Strategy

Implementation follows the product’s dependency chain rather than the order in which features look impressive: first verify the foundation; then establish identity, ownership, consent, and safety; then build assessment as the authoritative personalisation input; then plans, daily execution, progress, and the dashboard; finally add bounded AI explanations, reports, and operational polish. This ordering prevents later features from embedding unsafe assumptions or duplicating profile/assessment logic.

Risk reduction is deliberate. Each sprint produces a demonstrable vertical capability with explicit tests, while high-risk cross-cutting concerns—security, user isolation, data lifecycle, deterministic safety, observability, and accessibility—arrive before AI or broad feature expansion. AI is added only after approved assessment, plan, context, and safety boundaries exist; it explains or suggests within Python-controlled rules rather than becoming the system of record.

Incremental delivery means a sprint is complete only when its feature works through the intended user path, rejects invalid/unauthorised/safety-restricted paths, is documented, and passes its test gate. The competition strategy targets a polished 70% vertical slice: a user can safely register, complete an adaptive assessment, receive and use a basic plan, log progress, see a dashboard, and use one bounded AI Coach flow. Commercial strategy preserves stable contracts, versioned rules, auditability, observability, and explicit deferred contexts so future payments, organisations, integrations, and advanced AI do not require a rewrite.

## 2. Sprint Roadmap

| Sprint | Goal | Estimated duration | Dependencies | Deliverables | Definition of Done | Competition priority / risk |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | Verify foundation and delivery controls. | 2–3 days | Existing Phase 1 scaffold. | Passing quality gates, environment validation, documentation index, baseline CI. | Backend/frontend checks pass; known warnings/issues triaged; no architecture regression. | Must build / low. |
| 1 | Secure identity, session, consent, and user ownership baseline. | 1–1.5 weeks | Sprint 0. | Authentication lifecycle, profile basics, consent/privacy state, owner authorisation, audit events. | A user can securely access only own records; auth/security tests pass. | Must build / high. |
| 2 | Implement adaptive assessment and deterministic safety. | 1.5–2 weeks | Sprint 1. | Quick Start/Full Assessment, save/resume, branching, completion, safety/readiness result, reassessment trigger. | Core assessment and red-flag tests pass; result is versioned and explainable. | Must build / high. |
| 3 | Establish goals, dashboard shell, and plan-readiness experience. | 1 week | Sprint 2. | Goal lifecycle, Today aggregation, safety/missing-data states, profile/preferences/units/timezone. | Dashboard gives one accurate next action from real state; partial/empty states work. | Must build / medium. |
| 4 | Deliver basic workout plan and execution loop. | 1.5–2 weeks | Sprints 2–3. | Exercise catalogue subset, deterministic plan generation, session start/log/pause/complete, substitution, pain report. | Safe eligible user completes a session; pain pauses/restricts flow; ownership/state tests pass. | Must build / high. |
| 5 | Deliver basic nutrition and hydration loop. | 1–1.5 weeks | Sprints 2–3. | Restriction-aware plan, meal/water logging, daily summary, dietary-preference update. | Allergy/restriction and missing-data paths are safe; logs update dashboard/progress. | Must build / high. |
| 6 | Deliver progress and reporting-ready derived views. | 1–1.5 weeks | Sprints 3–5. | Measurements, check-ins as scoped, progress summaries, goal trend, data-completeness indicators. | Trends are deterministic, owner-scoped, and never overclaim with sparse data. | Must build / medium. |
| 7 | Add bounded AI Coach and explanation layer. | 1–1.5 weeks | Sprints 1–6. | Context builder, Python rule/safety gate, one Coach flow, feedback, availability/fallback, usage telemetry. | AI cannot bypass safety/consent; timeout/unavailable paths work; evaluation/safety tests pass. | Must build / high. |
| 8 | Add competition polish: reports, notifications, and limited operations. | 1–1.5 weeks | Sprints 3, 6, 7. | Weekly report if eligible, notification preference/inbox, limited admin health/audit/AI usage view. | Background/error states are observable; reports handle insufficient data; role tests pass. | If time allows / medium. |
| 9 | Release hardening, accessibility, performance, and deployment rehearsal. | 1–2 weeks | All must-build sprints. | Full regression suite, security review, RTL/accessibility pass, load smoke tests, monitoring, backup/restore rehearsal, demo release. | Release checklist and judge walkthrough pass in a production-like environment. | Must build / high. |

Sprint durations are planning ranges for a small graduation team. If time compresses, Sprint 8 is cut first; Sprints 1, 2, 4, 5, 6, 7, and 9 are not replaced by feature breadth.

## 3. Sprint Details

### Sprint 0 — Foundation verification

Confirm the existing Python/React foundation, configuration, CI, formatting, typing, test baseline, documentation links, environment setup, logging, and security middleware assumptions. Establish an issue register for genuine defects rather than rebuilding working scaffolding. Definition of done is a reproducible local/CI quality baseline and a clear release branch convention.

### Sprint 1 — Authentication, users, and privacy baseline

Implement identity/session lifecycle, verification/recovery flows, current user profile, units/language/timezone, consent state, owner-scoped authorisation, privacy request entry points, and audit events. This sprint establishes the only trusted actor context used by later assessment, plans, logs, AI, and admin. Test unauthenticated, expired-session, forbidden, cross-user, consent-withdrawal, and rate-limit paths before moving on.

### Sprint 2 — Smart Assessment

Implement Quick Start and Full Personalization first. Build required/optional questions, deterministic branching, save/resume, editing dependent answers, review/completion, versioned result/readiness, and the normal/caution/clearance-required safety boundary. Use the assessment blueprint as the acceptance source; do not start athlete, media, or broad reassessment features until this core is proven. The sprint demo is an ordinary user plus an injury/serious-symptom restricted path.

### Sprint 3 — Dashboard and user readiness

Implement Goal lifecycle, current-profile preferences, and a single Today dashboard that aggregates assessment state, next action, safety notice, plan placeholders/current state, and basic progress. The dashboard uses real data and communicates partial, stale, missing, and blocked states. It is not a static marketing screen and must remain useful before every later module is complete.

### Sprint 4 — Workout

Implement the smallest safe workout loop: an approved exercise catalogue subset, plan creation from current assessment/goal/equipment/time constraints, active plan view, one session flow, set logging, completion, skip/substitute, and pain report. Python owns eligibility, plan boundaries, substitutions, and pain safety. Do not implement live form coaching, unbounded adaptive progression, or broad sport modules in this sprint.

### Sprint 5 — Nutrition

Implement a practical, restriction-aware nutrition plan, dietary preferences/allergy reporting, meal logging, water logging, and daily summary. The plan must honour current approved restrictions and explicitly handle missing information. Do not implement meal-image scanning, medical diets, medication/supplement advice, or exhaustive food-catalogue coverage.

### Sprint 6 — Progress

Implement body-measurement logging, a limited check-in if capacity permits, deterministic goal/progress summaries, data-completeness messaging, and dashboard updates. Progress uses user-authorised observations and does not claim causality, diagnosis, or precision that inputs do not support. Prepare the derived-data and period conventions that reports will use later.

### Sprint 7 — AI Coach

Implement exactly one bounded, high-value Coach conversation path. Establish context selection from current approved assessment, plan, goal, preferences, and selected recent activity; enforce Python safety/consent/permission checks before invoking an LLM; validate outputs; retain recommendation/feedback/usage lifecycle metadata; and display a safe fallback. The sprint is not complete until AI timeout, provider failure, prompt-injection attempt, missing-context, safety-restricted, and user-isolation tests pass.

### Sprint 8 — Reports, notifications, and administration

If schedule allows, implement a weekly report based on sufficient deterministic progress data, notification preferences/inbox for selected events, and a limited administrator view of safe operational health, audit events, and aggregate AI usage. Background operations have visible pending, failure, retry, and insufficient-data states. Monthly reports, extensive admin operations, and commercial controls stay deferred.

### Sprint 9 — Testing, deployment, and competition rehearsal

Run full regression, accessibility/RTL checks, security/rate-limit tests, API contract tests, mobile journey tests, and production-like deployment validation. Verify monitoring, safe logs, error tracking, backup/restore procedure, environment secrets, rollback, and release notes. Rehearse a judge demonstration that includes successful, invalid, forbidden, safety-restricted, and AI-fallback outcomes.

## 4. Feature Dependencies

Foundation / CI / configuration
        ↓
Identity + session + consent + owner authorisation
        ↓
Adaptive Assessment + deterministic Safety Result
        ↓
Goals + preferences + Today dashboard
        ↓
Workout Plan/Session ───────┐
Nutrition Plan/Logging ─────┼──→ Progress / data completeness ──→ Reports
Recovery/check-in (optional)┘
        ↓
Bounded AI Context Builder + Rules/Safety Gate → AI Coach explanation/fallback
        ↓
Notifications / limited administration / release operations

Authentication, user ownership, consent, audit, and safety are prerequisites for all protected personal features. Assessment is required before plan generation and full AI personalisation. Workout/nutrition logging are sources for progress; progress sufficiency is required before reports. The dashboard can start early with assessment/readiness content, then aggregate each completed module. AI is downstream of the approved domain state and never a dependency for safety, plans, or basic product availability.

## 5. Risk Management

| Risk category | Risk | Mitigation and trigger |
| --- | --- | --- |
| Technical | Architectural drift or rules duplicated in UI/controllers. | Enforce domain/service ownership in review; trace each feature to blueprint rule; stop/rework when safety/permission logic appears outside Python domain layer. |
| Technical | Data version/concurrency errors after edits or retries. | Use version/idempotency strategy, state-transition tests, and explicit conflict UX from Sprint 1 onward. |
| AI | Hallucination, unsafe suggestion, prompt injection, costly/unavailable provider. | Rules-first gate, minimum context, output validation, safe fallback, rate/cost quotas, red-team safety tests, and clear non-medical language. |
| Security | Broken owner isolation, leaked secrets/logs, brute force, unsafe uploads. | Default deny, server-side ownership checks, secret scanning/handling, safe structured logs, rate limits, security tests, deferred media intelligence. |
| Performance | Dashboard/AI/report work slows core daily actions. | Aggregation/cache policy, async background work, limits, observability, and early latency smoke tests. |
| Competition | Broad incomplete feature set or fragile demo. | Lock must-build scope, cut Sprint 8 extras first, maintain demo script/test account, rehearse fallbacks. |
| Product | Assessment abandonment or overwhelming UX. | Quick Start, progressive disclosure, save/resume, usability review, section drop-off analytics. |
| Team | Unclear ownership or late integration. | Sprint owner, acceptance checklist, daily integration, small pull requests, risk review at each sprint close. |

## 6. Testing Strategy

Every sprint adds tests before declaring completion: unit tests for new domain rules and value boundaries; service tests for orchestration, ownership, state, and idempotency; integration/contract tests for the exposed behaviour; and a short end-to-end user journey for the sprint’s vertical capability. Existing tests always run as a regression gate.

| Sprint area | Minimum test focus |
| --- | --- |
| Foundation | Formatting, linting, typing, baseline tests, configuration failure modes. |
| Identity | Authentication/session/verification, password/reset limits, owner/role denial, consent, audit. |
| Assessment | Branches, requiredness, plausibility, save/resume/edit, versioning, every safety status. |
| Dashboard | Aggregate truth, empty/partial/stale/safety states, preference/timezone display. |
| Workout/Nutrition | Eligibility, restriction/equipment constraints, state transitions, duplicate commands, pain/allergy paths. |
| Progress/Reports | Data sufficiency, deterministic trend, correction, no unsupported conclusion, background failure. |
| AI | Context isolation/minimisation, rule precedence, output block, fallback, timeout, quota, feedback/memory control. |
| Release | Full regression, accessibility, RTL, mobile, security, load smoke, backup/restore, observability. |

The competition minimum is automated coverage for all hard safety and owner-isolation rules, critical happy paths, invalid/state-conflict paths, and a demonstrable end-to-end flow. Manual exploratory testing supplements, never replaces, these gates.

## 7. Documentation Updates

| After sprint | Required documentation review/update |
| --- | --- |
| 0 | Setup, Architecture, Folder Structure, CI/quality instructions, known assumptions. |
| 1 | API Blueprint authentication/profile status, Domain identity/consent rules, Database ownership/retention decisions, security operational notes. |
| 2 | Smart Assessment rules/branches/safety matrix, Domain state/event decisions, API contracts, test matrix. |
| 3–6 | Product/Domain/API/UI flows for goals, dashboard, plans, logs, progress, data-completeness language, and decisions made. |
| 7 | AI Architecture model-routing/safety/evaluation decisions, AI data lifecycle, API fallback/error behaviour, privacy review. |
| 8 | Reports/notifications/admin boundaries, job/operational runbooks, retention and audit implications. |
| 9 | Deployment/runbook, release notes, tested recovery evidence, final API documentation, known limitations, competition demo guide. |

Documentation updates record a decision, rationale, owner, effective version, and any user-visible implication. They do not silently rewrite prior approved specifications; material changes are called out as revisions.

## 8. Git Strategy

The protected `main` branch represents releasable work. Short-lived branches use a clear category and scope, such as `feature/assessment-save-resume`, `fix/safety-clearance-state`, `docs/implementation-plan`, or `chore/ci-check`. Every change enters main through a focused pull request with linked sprint item, summary, test evidence, security/privacy impact, documentation impact, and rollback note when relevant.

Commit messages use a consistent imperative convention: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, with a short domain scope where useful. Commits are small, buildable, and do not mix unrelated formatting/refactoring with feature logic. Review requires at least one peer check for ordinary changes and explicit security/domain review for authentication, safety, privacy, AI, permissions, or destructive lifecycle work.

Versioning follows semantic intent for releases: patch for compatible fixes, minor for compatible feature increments, major for breaking public contract changes. Tag planned demo/release candidates and production-like releases. Release notes state features, safety/behaviour changes, known limits, migration/deprecation notes, test status, and rollback reference.

## 9. Competition Version

### Must Build Before Competition

- Passing foundation/CI, secure identity/session/consent/ownership, and auditable hard safety rules.
- Quick Start and Full adaptive assessment with save/resume, edit/review, readiness, and injury/serious-symptom restriction.
- Goals, profile/preferences, and a useful Today dashboard.
- Basic deterministic workout plan and session logging, including substitution and pain reporting.
- Basic restriction-aware nutrition plan, meal/water logging, and daily summary.
- Body measurement/progress summary with data-completeness language.
- One bounded, explainable AI Coach flow with Python safety gate, feedback, and safe fallback.
- Core automated tests, accessibility/RTL pass, API documentation, monitoring/logging, and deployment rehearsal.

### Build If Time Allows

- Weekly reports, notification inbox/preferences, recovery check-in, habits/achievements.
- Football/goalkeeper extensions, richer dashboard/polish, controlled Coach memory, private avatar/progress-photo workflow.
- Limited admin health/audit/aggregate AI-usage view, data export, cache/background-job improvements.

### Post Competition

- Payments/subscriptions, organisations/trainers, marketplace, community.
- Vision/meal scan/form video, wearables/smartwatch, voice coach, broad sport suite, prediction claims.
- Monthly reports, advanced administration, partner APIs, multi-region/enterprise compliance work.

## 10. Timeline

Assuming a small focused team and approximately 12–14 weeks to competition, use the following realistic sequence. Weeks include integration and test time rather than treating quality as an afterthought.

| Period | Work | Milestone |
| --- | --- | --- |
| Week 1 | Sprint 0 | Verified development baseline and delivery controls. |
| Weeks 2–3 | Sprint 1 | Secure user/consent/ownership baseline. |
| Weeks 4–5 | Sprint 2 | Demonstrable adaptive assessment and safety outcome. |
| Week 6 | Sprint 3 | Today dashboard and goals/readiness. |
| Weeks 7–8 | Sprint 4 | Workout vertical loop. |
| Week 9 | Sprint 5 | Nutrition/hydration vertical loop. |
| Week 10 | Sprint 6 | Progress/derived summary. |
| Week 11 | Sprint 7 | Bounded AI Coach with fallbacks. |
| Week 12 | Sprint 8 or scope buffer | Highest-value optional polish only. |
| Weeks 13–14 | Sprint 9 | Release hardening, demo rehearsal, contingency fixes. |

If only 10 weeks remain, combine Sprint 3 with the first simple dashboard state, reduce Sprint 8 to zero, and preserve the final two-week hardening window. Do not compress safety, ownership, or release verification to add optional features.

## 11. Definition of Done

The project is ready for implementation when every roadmap sprint has a named goal, dependencies, deliverables, acceptance criteria, owner, risk level, and test gate; the feature graph and cut line are agreed; risk mitigations are owned; documentation update duties and Git/release rules are defined; the competition target is a realistic 70% vertical slice; the README link is present; and no implementation work is claimed by this plan.

## 12. Judge Review

This strategy is strong because it sequences the product around safety and personalisation truth: assessment and deterministic rules precede plans, and plans/progress precede AI explanation. It demonstrates engineering maturity through independent sprint acceptance, explicit cut scope, security/ownership early, and a real release-hardening phase.

**Score: 93/100 as an implementation strategy.** Strengths include risk-first sequencing, clear dependencies, test gates, realistic optional scope, and a judge-friendly demonstration plan. Weaknesses are that delivery still depends on disciplined scope control and adequate team capacity; AI quality and accessibility require practical validation, not documentation alone. The greatest risk is broad feature implementation before Sprint 2 safety/assessment is stable. A judge should ask for evidence that the hard safety and user-isolation tests actually ran, that fallbacks work, and that the delivered demo matches the stated cut line.

## 13. Startup Review

This roadmap can produce a scalable startup foundation because it protects stable domain/API boundaries, keeps Python business rules authoritative, introduces observable operational practices before commercial complexity, and treats AI as a governed capability rather than product infrastructure. It should not attempt payments, multi-tenancy, vision, wearables, or broad content systems until activation, adherence, safety, retention, and cost signals validate the core loop.

The startup value emerges from a trusted recurring experience: assessment → feasible daily action → logged evidence → progress reflection → bounded coaching. Premium expansion should follow proven usage: deeper reporting, sport-specific programmes, advanced coaching, approved integrations, and human-coach collaboration. The roadmap’s long-term advantage is not feature count; it is the ability to evolve personalisation safely while preserving user trust, data control, and operational reliability.
