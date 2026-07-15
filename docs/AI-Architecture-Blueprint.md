# RAHFIT AI — Enterprise AI Architecture Blueprint

**Status:** Official Sprint 2.4 pre-implementation specification  
**Scope:** AI product, safety, operational, and system architecture only. This document contains no implementation, prompts, APIs, models, schemas, or code.

## 1. AI Vision

AI exists in RAHFIT AI to turn approved user context into clearer, more relevant coaching: explain a plan, help the user choose a feasible next action, summarise progress, surface constraints, and maintain a supportive conversation across fitness, nutrition, recovery, habits, and performance. It solves the gap between static trackers and expensive one-to-one coaching by making guidance responsive to changing goals, time, equipment, progress, and preferences.

AI must never diagnose disease or injury, prescribe treatment, replace a doctor, physiotherapist, dietitian, or emergency service, guarantee health/performance outcomes, override deterministic safety rules, invent user facts, make payment/privacy/access decisions, or autonomously apply high-consequence plan changes without governed user review.

Human oversight is risk-proportionate. Users remain in control of goals, preferences, memories, and plan acceptance. Safety-sensitive cases are paused or routed to appropriate professional advice. Product, safety, and domain owners review policies, high-risk incidents, output quality, and material rule changes. The system is designed to say “I do not have enough information” or “seek professional advice” when that is the safe answer.

## 2. AI Principles

| Principle | Architectural consequence |
| --- | --- |
| Safety first | Deterministic safety rules run before and after any generative step; no model output can weaken a stop or caution state. |
| Explainability | Meaningful recommendations identify their source context, constraints, assumptions, and a user-friendly reason. |
| Personalisation | Approved, current, minimum-necessary profile data drives guidance; missing data reduces certainty rather than causing fabrication. |
| Privacy | Consent, purpose limitation, minimisation, redaction, access isolation, and editable/deletable memory govern AI context. |
| Reliability | The product degrades gracefully when an AI provider is unavailable; core safety, logging, and user actions do not depend on a successful model call. |
| Cost awareness | Model use must be intentional, bounded, observable, cached when safe, and routed according to task risk and value. |
| Deterministic rules before LLM | Python domain logic owns eligibility, safety, calculations, constraints, permissions, lifecycle decisions, and output validation. |
| Human review when needed | Escalation policy covers severe safety signals, reported harmful output, policy uncertainty, and high-impact future use cases. |
| Evaluation over intuition | New AI behaviour requires explicit quality, safety, privacy, and cost evaluation before release. |
| User dignity | Tone is supportive, non-shaming, culturally respectful, and avoids coercive or obsessive health behaviours. |

## 3. AI System Architecture

| Layer | Responsibility | Inputs and outputs |
| --- | --- | --- |
| Assessment layer | Produces versioned, consented, safety-screened context and explicit missing-data indicators. | Receives assessment outputs; provides only current approved facts and safety status. |
| User profile layer | Maintains user-controlled goals, preferences, constraints, schedule, locale, and entitlement context. | Supplies scoped, current personalisation facts. |
| AI memory layer | Retains compact, approved, reviewable durable context and session summaries. | Supplies relevant memory with source, confidence, expiry, and consent scope. |
| Context builder | Selects, ranks, redacts, normalises, and bounds information for a single AI task. | Produces a minimum-necessary task context and records what sources were used. |
| Rules engine | Applies Python-owned eligibility, safety, plan constraints, calculations, policy, and deterministic decisions. | Produces permitted actions, restrictions, and structured facts for recommendation generation. |
| Recommendation engine | Orchestrates rule output, model routing, validation, lifecycle state, user review, and explanation. | Produces a bounded candidate recommendation or a safe fallback. |
| LLM layer | Generates natural-language explanation, coaching dialogue, bounded options, summaries, and structured suggestions within allowed constraints. | Receives only approved task context; returns non-authoritative candidate content. |
| Safety layer | Enforces input screening, content restrictions, output checks, confidence/uncertainty handling, and escalation. | May block, redact, transform, or route output; never relies on LLM judgement alone for hard rules. |
| Analytics and evaluation layer | Measures quality, safety, performance, user feedback, cost, and drift while protecting sensitive data. | Uses redacted/pseudonymised events and approved evaluation samples. |

Data flow is unidirectional for a task: approved assessment/profile/memory and current activity enter the context builder; Python rules decide boundaries; a permitted LLM task may generate a candidate; deterministic and policy checks validate it; the recommendation engine stores lifecycle metadata and presents the safe final result. Feedback and confirmed user corrections can create a reviewable memory candidate, never an automatic uncontrolled fact.

## 4. AI Modules

| Module | Purpose | Inputs | Outputs | Dependencies and expansion |
| --- | --- | --- | --- | --- |
| AI Coach | Provide supportive, contextual conversation and explain next actions. | Approved profile, current plan, progress, selected memory, safety state, user question. | Bounded response, clarifying question, explanation, or safe escalation. | Depends on all core layers. Future: multilingual voice and coach handoff. |
| Workout AI | Explain or adapt a permitted workout within established constraints. | Plan, experience, time, equipment, completion feedback, limitation/safety state. | Exercise explanation, permitted substitutions, session rationale, change request. | Depends on exercise catalogue and rules engine. Future: validated sport modules. |
| Nutrition AI | Explain practical nutrition guidance consistent with approved plan and restrictions. | Nutrition profile, allergies/restrictions, goal, food context, safety state. | Meal ideas, adherence support, clarification, or professional-advice route. | Depends on nutrition rules and catalogue. Future: regional food and dietitian review. |
| Recovery AI | Encourage recovery-aware choices and explain conservative plan adjustments. | Sleep, fatigue, stress, recent load, user feedback, safety state. | Non-medical recovery guidance and a permitted plan-review suggestion. | Depends on derived indicators. Future: wearable-informed context. |
| Habit AI | Help users translate goals into manageable routines and reminders. | Goal, time, obstacles, preferences, adherence history. | Small action options, check-in wording, reminder preference suggestions. | Depends on notification preferences. Future: adaptive experimentation. |
| Motivation AI | Provide respectful encouragement and reflection without manipulation. | User-selected tone, achievements, adherence, stated motivation. | Supportive acknowledgement and next-action framing. | Depends on safety/tone policy. Future: cohort/community boundary. |
| Report Generator | Convert approved progress facts into a clear periodic narrative. | Report period, snapshots, plan history, completeness/confidence, safety status. | Explainable summary, progress limits, next-focus options. | Depends on reporting rules. Future: shareable coach reports. |
| Goal Optimizer | Help review goal priority, feasibility, and changes. | Goal profile, timeline, constraints, progress, safety status. | Discussion prompts and plan-review recommendation, never autonomous goal change. | Depends on realism rules. Future: scenario planning. |

## 5. Hybrid Decision Engine

Python always decides account/role/consent eligibility; assessment validity and version; safety status; age and policy gates; plan availability; data access scope; numerical and unit normalisation; deterministic calculations; food/exercise restriction filters; notification entitlement; recommendation lifecycle; storage/audit decisions; and whether an LLM may be called at all.

The LLM may generate plain-language explanations, encouragement, summaries, clarifying questions, non-authoritative options drawn from allowed context, and wording that adapts to the user’s selected communication tone and language. It may suggest a review or permitted change request, but cannot make the change authoritative.

The LLM is never delegated medical triage, diagnosis, serious-symptom classification, professional-clearance decisions, allergy safety guarantees, age-policy enforcement, unsafe-goal detection, exact nutritional/clinical calculations, permission decisions, payment decisions, legal/privacy decisions, data retention, or final enforcement of safety policy.

Examples: Python determines that a user with a serious red flag cannot receive normal workout guidance; the LLM may explain the pause calmly. Python filters a no-equipment, beginner-safe exercise set; the LLM may explain why the options fit the user’s time. Python identifies insufficient progress data; the LLM may state that a trend cannot yet be concluded rather than inventing insight.

## 6. Memory Architecture

Short-term memory is bounded to the active conversation or immediate task: recent turns, task state, unresolved user questions, and the current plan/assessment version. It expires quickly after task/session usefulness ends and is not promoted automatically to long-term context.

Long-term memory holds only user-approved, durable facts that improve future coaching: stable preferences, confirmed goals, known constraints, communication preference, explicitly accepted plan context, and compact summaries of meaningful prior interactions. Each memory has a source, purpose, confidence, creation/review time, expiry or review date, consent scope, and user-visible edit/delete control.

Injuries and limitations are not treated as casual conversational memory. They remain governed safety/assessment facts with stricter access, currentness, and professional-clearance semantics. Conversation summaries retain only useful, minimal continuity: what the user wanted, confirmed preference/constraint changes, unanswered needs, and agreed next steps. Raw histories are bounded, redacted, and retained only under policy.

Memory improves personalisation by avoiding repetitive questions and preserving agreed context, but it never substitutes for reassessment. A changed goal, injury, schedule, or user correction supersedes older memory, triggers review when needed, and records why context changed.

## 7. Context Builder

Before an AI request, the context builder collects only task-relevant, approved information in this priority order:

1. Hard safety, consent, access, and age-policy status.
2. Current task intent and explicit user request.
3. Current assessment version, goal, plan, restrictions, and missing-data/confidence state.
4. Recent task-relevant user activity, progress, or feedback.
5. Relevant durable memory and short session summary.
6. Approved catalogue or policy facts needed to ground the response.
7. Presentation preferences such as language, units, and coaching tone.

The builder uses a strict context budget appropriate to the selected model and task. It favours concise derived facts and source references over raw histories; if the budget is exceeded, it drops lower-priority context, creates a concise approved summary, or asks the user a targeted clarifying question. It never silently excludes hard safety constraints.

Sensitive information is minimised, redacted where detail is not needed, and excluded when consent or task purpose does not permit use. The builder records context categories and versions, not unnecessary raw content, for explainability and investigation. If required context is missing, stale, conflicting, or unavailable, the fallback is a safe limitation message, targeted reassessment prompt, or non-AI product path—not guessed personalisation.

## 8. Recommendation Pipeline

**Assessment → Python validation → Rules engine → Context builder → permitted LLM task → safety/output validation → final recommendation lifecycle.**

1. **Assessment:** supplies approved, current user facts, readiness, safety status, consent, and missing-data indicators.
2. **Python validation:** verifies identity/scope, data freshness, input validity, task eligibility, and required versions.
3. **Rules engine:** calculates fixed constraints, safety restrictions, permitted actions, and whether guidance must be paused, conservative, or normal.
4. **Context builder:** selects minimum necessary facts, grounded catalogue information, and relevant governed memory within a context budget.
5. **Permitted LLM task:** generates a candidate explanation, summary, clarification, or allowed option only inside the boundary supplied by the rules engine.
6. **Safety/output validation:** checks structure, policy, unsafe claims, contradictions, prohibited content, hallucination risk indicators, user-language fit, and confidence/uncertainty disclosure. A failed check is blocked, replaced with a safe fallback, or routed for review.
7. **Final recommendation:** stores source versions, safety outcome, state, explanation basis, user response, and any supersession relationship. Users can accept, decline, correct, or request a plan review.

No stage assumes that LLM availability is required. If it is unavailable, the system preserves the user action, provides deterministic plan information where permitted, and presents a transparent pending or fallback state.

## 9. AI Safety

Unsafe requests include medical diagnosis/treatment requests, emergency symptoms, rehabilitation instructions beyond approved boundaries, extreme weight-loss or training requests, self-harm content, eating-disorder indicators, doping/illegal performance enhancement, harassment, explicit content involving minors, privacy invasion, attempts to bypass access controls, and requests to reveal system/private data.

Medical limitations are expressed clearly and consistently: RAHFIT AI is not a medical provider. Injury and serious-symptom handling follows the Smart Assessment safety status. A stop status blocks normal workout/nutrition generation and directs the user to appropriate professional help; a caution status allows only conservative, constraint-aware guidance. Nutrition safety rejects dangerous restriction, unverified supplement/medication advice, and allergy guarantees. Minor users receive age-appropriate, policy-gated experiences and cannot use extreme-plan paths.

Prompt-injection protection treats all user-supplied content, imported content, and external text as untrusted data, not instructions. System policy, rule outputs, tool/catalogue boundaries, permissions, and hidden context are never exposed or overridden by user content. Hallucination mitigation grounds output in approved facts, uses constrained task scope, requires explicit uncertainty when evidence is incomplete, validates against deterministic constraints, and avoids citing nonexistent sources or measurements.

Confidence is a product signal, not a claim of truth. The system exposes when personalisation is limited by missing/stale/conflicting input and chooses clarification, conservative guidance, or escalation over false precision. Safety incidents, harmful-output reports, and policy-violation attempts are minimised, audited, and reviewed by accountable owners.

## 10. Personalization Strategy

| Context | How it changes recommendations |
| --- | --- |
| Goals and priorities | Selects the plan focus, explanation framing, review cadence, and permitted trade-off discussions. |
| Age and policy state | Applies eligibility, minor safeguards, age-appropriate language, and restricted paths. |
| Experience | Changes complexity, instruction depth, initial progression boundary, and need for clarification. |
| Equipment/environment | Filters to feasible options and explains substitutions; never assumes gym access. |
| Sleep, recovery, and fatigue | Encourages conservative workload/recovery emphasis when indicators are poor; never diagnoses. |
| Lifestyle and time | Adapts session length, schedule, reminder strategy, and habit scale to practical availability. |
| Nutrition context | Respects dietary preferences, allergies, cultural/religious restrictions, food access, and stated eating challenges. |
| Sport context | Uses training/match schedule, position, and selected priorities for bounded football/goalkeeper guidance. |
| Previous progress | Explains trends only where data sufficiency is met; otherwise asks for more data or frames uncertainty. |

Personalisation is based on current approved data and user correction, not opaque profiling. Safety and user preference always constrain convenience and optimisation.

## 11. Explainability

Every consequential recommendation should state what it is recommending, why it fits, what user information it relied on, what constraints it respected, what uncertainty remains, and what the user can change or clarify. Example explanation patterns are “based on your available time and no-equipment setting,” “because you reported fatigue, this is intentionally conservative,” and “I need a current assessment update before changing this plan.”

The system retains a compact explanation record: assessment/plan/recommendation versions, relevant context categories, rule outcome, safety status, and user feedback. It does not expose internal hidden instructions, private data from another scope, or unreviewed model reasoning. Explainability is a user experience and governance requirement, not a claim that the LLM’s internal reasoning is fully inspectable.

## 12. Cost Optimization

| Strategy | Design decision |
| --- | --- |
| Avoid unnecessary calls | Use deterministic rules, existing plan content, and static guidance for routine states; invoke AI only where natural-language adaptation adds clear value. |
| Model routing | Select the smallest approved model capable of the bounded task; reserve higher-capability models for reviewed, high-value complex explanations. |
| Context budgeting | Send concise approved summaries and task-specific facts, not full histories or entire profiles. |
| Caching | Cache safe, non-personal or appropriately scoped deterministic-derived results; invalidate on plan, assessment, consent, or relevant context version change. |
| Conversation summarisation | Replace stale raw conversation turns with minimal, user-governed summaries; expire unused short-term context. |
| Batching and asynchronous work | Generate periodic narrative reports outside interactive paths; avoid generating duplicate explanations for the same state. |
| Usage controls | Apply per-user and per-tenant quotas, rate limits, budgets, anomaly alerts, and graceful lower-cost fallbacks. |
| Competition discipline | Use a small number of high-impact AI paths: assessment explanation, bounded coach response, and report summary. Measure usage before expanding. |

Cost telemetry records task category, model/provider, latency, token/cost category, outcome, cache use, and safety result without retaining unnecessary sensitive content.

## 13. Future AI Roadmap

| Before Competition | After Competition | Future Commercial Version |
| --- | --- | --- |
| Hybrid rules/LLM boundary; assessment-aware AI Coach; safe explanation of existing plans; deterministic safety layer; compact governed memory; bounded report narrative; evaluation and incident feedback. | Football/goalkeeper refinement; deeper nutrition/recovery explanations; targeted reassessment prompts; model routing; richer quality evaluation; optional wearable summary ingestion. | Consent-governed vision assistance; voice coach; smartwatch and wearable integration; multilingual conversational quality; predictive analytics validated against outcomes; human-coach collaboration; organisation-level controls and enterprise audit/reporting. |

Vision, voice, wearables, and prediction are not baseline features. Each requires a separate value case, consent model, safety evaluation, privacy review, cost plan, and rollback path.

## 14. Functional Requirements

| Priority | Requirement |
| --- | --- |
| Critical | The system must apply Python-owned consent, access, assessment-validity, age-policy, and safety checks before any AI task. |
| Critical | AI must receive only minimum necessary, approved, current context and must not override hard safety rules. |
| Critical | Every recommendation must retain source-version, safety, lifecycle, and user-feedback information sufficient for explanation. |
| Critical | AI unavailability or output-validation failure must produce a safe, transparent fallback. |
| Critical | Users must be able to correct relevant profile facts and manage eligible durable AI memory. |
| High | The system must identify missing/stale/conflicting context and ask focused clarification rather than inventing facts. |
| High | AI output must be bounded by module purpose, language, tone, policy, and recommendation constraints. |
| High | Safety reports and high-risk incidents must enter an auditable review workflow. |
| Medium | Users may view a concise explanation of relevant plan/recommendation changes. |
| Medium | Cost budgets, caching, model routing, and quality evaluation can be configured by task category. |
| Future | Voice, vision, wearable context, predictive analytics, coach handoff, enterprise model controls, and advanced experimentation. |

## 15. Non-Functional Requirements

| Area | Requirement |
| --- | --- |
| Performance | Interactive AI requests have a defined user-visible timeout and fallback; context/rule preparation must not dominate ordinary user actions. |
| Scalability | AI requests, report generation, evaluation, and analytics scale independently from the core product; high-volume work is asynchronous. |
| Availability | Core plan access and safety messaging remain available when AI providers fail; provider health is monitored. |
| Reliability | Requests are idempotent where retries occur; lifecycle records prevent duplicate final recommendations; version conflicts are visible. |
| Security | Least privilege, encrypted transport/storage, secret isolation, injection resistance, dependency review, and audit logging are mandatory. |
| Maintainability | Modules, policies, model routing, evaluation sets, and deprecation decisions have owners and versioned documentation. Python remains the authoritative home for business rules. |
| Observability | Measure latency, errors, provider health, token/cost use, cache outcomes, block/fallback rate, safety flags, feedback, and quality regression. |
| Privacy | Consent, minimisation, redaction, retention, memory controls, export/deletion, and regional policy readiness are enforced end to end. |

## 16. Testing Strategy

Testing begins with deterministic unit tests for rules, safety precedence, age/consent gates, context selection, redaction, memory expiry/editing, lifecycle transitions, output validation, caching invalidation, and fallback selection. Integration tests verify approved context flow across assessment, plans, rules, recommendation lifecycle, audit, and provider adapters using controlled test doubles.

Safety tests cover serious symptoms, injury/caution, dangerous goals, minors, allergy/restriction context, self-harm/doping requests, prompt-injection attempts, privacy-access attempts, hallucinated facts, and unavailable providers. Recommendation tests compare outputs to approved task criteria: groundedness, constraint adherence, uncertainty, respectful tone, and correct escalation. Regression tests use curated, consent-safe evaluation cases so quality or policy changes cannot silently degrade known behaviour.

Memory tests ensure no cross-user leakage, expired/withdrawn memory exclusion, correction/supersession, minimal context selection, and deletion/export propagation. Edge cases include incomplete assessment, stale plan, conflicting profile facts, no equipment/limited time, empty history, model timeout, malformed provider response, rate limit, duplicate request, and locale/RTL language needs. Before competition, the minimum suite demonstrates every hard safety rule, every permitted AI module path, fallbacks, and key privacy boundaries.

## 17. Competition Scope

| Must Build Before Competition | If Time Allows | Post Competition |
| --- | --- | --- |
| Rules-first AI boundary; assessment-aware context builder; hard safety/consent gates; one bounded AI Coach flow; explainable workout/nutrition/recovery response within existing plan context; source/lifecycle record; safe fallback; basic memory preference/summary control; tests and evaluation cases. | Periodic report narrative; task-based model routing/caching; football/goalkeeper explanation; richer feedback dashboard; Arabic AI quality review. | Voice, vision, wearables/smartwatch, predictive analytics, human coach handoff, organisation controls, broad multilingual expansion, advanced evaluation/experimentation. |

The competition demonstration should prove that AI is useful but not in charge: changing a user’s safety status or equipment/time changes the permitted answer; a risky request is correctly paused; and an explanation shows which approved context influenced the response.

## 18. Judge Review

| Dimension | Review |
| --- | --- |
| Originality | Strong: the differentiator is governed, explainable personalisation rather than generic chatbot output. |
| Technical depth | Strong: hybrid decision boundaries, context governance, memory lifecycle, safety validation, cost controls, and evaluation are explicit. |
| Engineering quality | Strong if rules are independently testable and the system degrades safely without AI. |
| AI maturity | Strong for a graduation project because it recognises hallucination, injection, privacy, evaluation, and lifecycle risks. |
| Feasibility | Good only when the project limits itself to a few bounded modules and does not pursue vision/wearable/voice features. |

**Strengths:** Python remains authoritative; safety cannot be delegated to the LLM; context is minimum-necessary and explainable; commercial concerns are anticipated without overbuilding.  
**Weaknesses:** output quality depends on external model behaviour and carefully curated content; evaluation effort is substantial; trust must be earned with a polished user experience.  
**Risks:** broad scope, untested safety language, raw conversation retention, provider cost/availability, and claims that exceed the evidence.  
**Judge questions:** What exactly does Python decide? How is a red flag enforced? How do you prevent hallucinations and data leakage? What happens if the model is unavailable? How do users correct memory?  
**Score:** 93/100 as an architecture blueprint. A first-place result depends on demonstrating a small, tested hybrid loop rather than many unverified AI features.

## 19. Startup Review

The commercial value is strong if RAHFIT AI converts assessment context into actions users consistently complete. Personalised explanation and continuity can increase retention and willingness to pay, while a disciplined memory and feedback loop becomes difficult to replicate without trust, data quality, and operational maturity. Premium opportunities include deeper plan adaptation, high-quality reports, sport modules, human-coach collaboration, and approved integrations—not unrestricted chat.

Build first: trustworthy assessment context, deterministic safety/constraints, one helpful coaching use case, feedback, explanation, and cost telemetry. Postpone broad conversational features, vision, voice, wearables, predictive claims, community, and enterprise controls until core activation and retention are validated. Long-term differentiation comes from safely governed longitudinal context, measurable coaching quality, culturally relevant guidance, and a user relationship that is transparent about what AI can and cannot do.

## 20. Definition of Done

Sprint 2.4 is complete only when the AI architecture, hybrid Python/LLM strategy, Python responsibilities, LLM boundaries, safety layer, memory layer, context builder, recommendation pipeline, testing strategy, commercial roadmap, and realistic competition scope are documented; no implementation code exists; and the README links to this document.
