# RAHFIT AI — Product Blueprint & System Design

**Status:** Official product specification for pre-implementation planning  
**Scope:** Product, business, and system-level requirements only. This document intentionally contains no implementation, API, database, or code design.

## 1. Product Goal

RAHFIT AI is a personalised health, fitness, nutrition, and performance platform that helps people turn an intention—lose weight, gain muscle, get fitter, or perform better—into a safe daily plan they can follow. It combines structured assessment, adaptive plans, progress tracking, and an AI coach in one coherent experience.

It exists because most users face fragmented tools: one app for workouts, another for calories, generic online advice, and little accountability. Beginners do not know where to start; experienced gym users waste time translating goals into programmes; athletes need plans that respect a training schedule; busy people need guidance that fits real life.

The product differentiates itself by treating coaching as a continuous feedback loop rather than a static plan. Assessment establishes a baseline, behaviour and progress provide evidence, and the coach explains and adjusts recommendations within defined safety boundaries. Users pay for time saved, higher confidence, personal relevance, accountability, and a single premium experience that evolves with their goals.

## 2. Business Value

| Area | Value |
| --- | --- |
| User value | Clear next actions, plans matched to goals and constraints, visible progress, and coaching support without the cost or scheduling friction of one-to-one coaching. |
| Business value | Recurring subscription revenue, engagement-driven retention, and future B2B opportunities for trainers, gyms, universities, and sports organisations. |
| Competitive advantage | A unified, evidence-aware coaching loop across training, nutrition, recovery, habits, and performance—rather than isolated trackers or generic content. |
| Long-term vision | Become a trusted personal health operating system: multilingual, culturally relevant, privacy-respecting, and able to serve consumers and professional coaching organisations. |

The commercial promise must remain credible: recommendations should be explainable, users retain control, and the platform must never position itself as a substitute for qualified medical care.

## 3. User Personas

| Persona | Goals | Pain points | Motivations | Typical routine |
| --- | --- | --- | --- | --- |
| Beginner | Establish a sustainable routine and learn correct basics. | Intimidated by gyms; conflicting advice; does not know what to track. | Confidence, energy, early visible wins. | School/work, irregular exercise, short available sessions. |
| Gym User | Gain muscle or strength efficiently. | Plateaus; programme uncertainty; inconsistent nutrition and recovery. | Measurable progression and better physique. | Trains 3–6 times weekly, logs lifts, plans meals around training. |
| Weight Loss User | Reduce weight safely while preserving adherence. | Restrictive diets, discouraging scale changes, social eating. | Health, confidence, long-term habits. | Balances home/work obligations; needs quick meals and flexible activity. |
| Football Player | Improve match fitness, strength, conditioning, and recovery. | Training load conflicts; seasonal variation; injury concern. | On-field performance and availability. | Team sessions, matches, gym work, variable travel and recovery needs. |
| Busy Employee | Maintain health with limited planning time. | Long workdays, sedentary habits, fatigue, unpredictable schedule. | Energy, stress relief, convenience. | Commute/work blocks, 20–40 minute windows, meal decisions on the go. |
| University Student | Build affordable habits around a changing timetable. | Limited budget, inconsistent sleep, exams, shared meals. | Confidence, social wellbeing, athletic goals. | Classes, study periods, campus activity, schedule changes by term. |

All personas need adjustable goals, time availability, equipment access, dietary preferences, cultural food context, language, and accessibility needs. Personas guide prioritisation; they do not replace individual assessment.

## 4. End-to-End User Journey

| Stage | Experience and purpose |
| --- | --- |
| Landing page | Communicates the outcome, target users, trust principles, pricing value, and appropriate health disclaimer. It converts interest into an informed registration decision. |
| Register | Creates an account and captures required consent, terms acceptance, and a verified communication channel. It establishes identity and account ownership. |
| Login | Restores secure access to the user’s private health and progress information. |
| Onboarding | Collects preferences such as goal, schedule, units, language, equipment, dietary pattern, and notification preferences. It reduces later friction and makes the experience relevant from day one. |
| Assessment | Collects the baseline: objective, experience, activity level, constraints, relevant health screening, current habits, measurements the user chooses to provide, and performance context. It determines what recommendations are appropriate. |
| AI analysis | Produces a plain-language summary of the assessment, assumptions, priorities, and proposed plan. The user reviews and confirms it; AI output is advisory and safety constrained. |
| Dashboard | Provides a calm daily command centre: today’s actions, progress signals, check-ins, and coach guidance. It avoids overwhelming the user with every metric. |
| Workout | Delivers an actionable session with exercise guidance, substitutions, completion logging, perceived effort, and feedback. It closes the loop between programme and execution. |
| Nutrition | Offers goals, meal guidance, food logging options, hydration/habit support, and adherence-oriented feedback. It supports, rather than shames, real-life eating decisions. |
| Progress | Visualises trends in adherence, performance, measurements, wellbeing, and goal milestones. It distinguishes trend from day-to-day noise. |
| Reports | Summarises a meaningful period, achievements, blockers, and next focus. It turns accumulated data into a useful review conversation. |
| Achievements | Recognises healthy consistency and meaningful milestones without encouraging unsafe behaviour or obsessive tracking. |
| Subscription | Explains free versus paid value, offers transparent billing and cancellation, and permits plan management. It must not gate essential safety information. |

Reassessment is a recurring journey, not a one-time event. Significant goal, lifestyle, injury, or training-context changes should prompt review before plan changes are applied.

## 5. Core Modules

| Module | Responsibility |
| --- | --- |
| Identity and access | Account lifecycle, authentication, authorisation, consent, device/session control, and privacy controls. |
| User profile | Personal preferences, units, locale, goals, constraints, and communication settings. |
| Assessment | Versioned intake, screening, baseline capture, reassessment, and readiness state. |
| Plan orchestration | Coordinates approved workout, nutrition, recovery, and habit plans; tracks plan versions and change rationale. |
| Workout | Programme presentation, exercise library use, session logging, substitutions, load/progression feedback, and completion. |
| Nutrition | Nutrition targets, meal guidance, food and habit tracking, dietary preferences, and adherence feedback. |
| AI coach | Context-aware conversational guidance, explanation, recommendation generation, safety escalation, and feedback capture. |
| Progress and reports | Trend calculation, milestones, goal reviews, shareable/exportable reports, and coaching insights. |
| Notifications | User-controlled reminders, plan prompts, check-in requests, report availability, and operational messages. |
| Achievements | Consistency-oriented badges, milestones, and motivational feedback with anti-gaming safeguards. |
| Subscription and billing | Entitlements, trials, pricing plans, invoices, cancellation, refunds, and billing-provider reconciliation. |
| Community (future) | Moderated peer groups, challenges, content sharing, reporting, and safety policy enforcement. |
| Admin and support | Role-controlled operational support, content stewardship, moderation, audit review, and user-request handling. |
| Analytics | Privacy-aware product events, funnels, cohort analysis, experiments, and service-health indicators. |
| Future vision AI | Optional vision-assisted form feedback or meal support, only after dedicated consent, validation, privacy review, and safety controls. |

## 6. Feature Prioritisation

| Priority | Features | Rationale |
| --- | --- | --- |
| Critical | Identity/access; consent; profile; onboarding and assessment; goal creation; safe plan delivery; workout completion; basic nutrition guidance; dashboard; progress logging; core reports; safety messaging; observability; privacy controls. | Required to deliver one complete and trustworthy user outcome. |
| High | Adaptive plan adjustments; AI coaching with guardrails; notifications; achievements; subscriptions; detailed analytics; coach/trainer access with explicit client permission. | Strongly improves retention, personalisation, and commercial viability after the core loop is reliable. |
| Medium | Wearable integrations; expanded exercise and food content; calendar support; multilingual localisation beyond launch languages; advanced exports; challenges. | Valuable differentiation but not required to validate core behaviour. |
| Future | Community; B2B organisation console; marketplace; vision AI; live human coaching; advanced performance prediction; partner integrations. | High complexity, safety/privacy considerations, or dependence on validated product-market fit. |

## 7. Critical-Module User Stories

| Module | User story |
| --- | --- |
| Identity and access | As a user, I want to create, access, and securely recover my account so that my personal information and progress remain private. |
| Consent and privacy | As a user, I want to understand and control how my health-related information is used so that I can make informed choices. |
| Profile and onboarding | As a user, I want to provide my goals, constraints, preferences, and schedule once so that the platform starts with relevant guidance. |
| Assessment | As a user, I want to complete a clear baseline assessment so that recommendations are appropriate to my starting point. |
| AI analysis | As a user, I want the proposed priorities and assumptions explained in plain language so that I can approve or correct my plan. |
| Plan delivery | As a user, I want a manageable plan with a clear next action so that I can make progress without deciding everything myself. |
| Workout | As a user, I want to view, adapt, and complete a workout based on my available time and equipment so that missed conditions do not end my routine. |
| Nutrition | As a user, I want practical nutrition guidance that respects my preferences and lifestyle so that I can follow it consistently. |
| Progress | As a user, I want to record relevant outcomes and see trends over time so that I know whether my effort is working. |
| Reports | As a user, I want a periodic summary of results, adherence, and next priorities so that I can reflect and adjust with confidence. |
| Notifications | As a user, I want to choose useful reminders and silence unwanted ones so that support fits my life rather than interrupts it. |
| Subscription | As a subscriber, I want transparent plan benefits, billing, and cancellation so that I can make a fair purchasing decision. |
| Admin/support | As an authorised support operator, I want limited, audited tools to assist users so that issues can be resolved without unnecessary exposure of private data. |

## 8. Business Rules

### Eligibility, consent, and safety

- A user must accept current terms and privacy notices before using personalisation features.
- The product must present clear medical and emergency limitations. It does not diagnose, treat, or replace a licensed clinician.
- Health-screening responses that meet defined risk criteria must pause automated exercise/nutrition recommendations and direct the user to appropriate professional advice.
- A user may decline optional data fields; the product must clearly explain the resulting limits on personalisation.
- Minors, regional requirements, and consent requirements must be handled according to the launch market’s applicable policy before availability.

### Assessment and plans

- A user cannot receive a personalised workout, nutrition target, or AI recommendation until the required assessment is complete and accepted.
- Recommendations must use the current approved assessment and plan version; material changes require reassessment or explicit confirmation.
- Plans must respect stated availability, equipment access, preferences, and exclusions whenever sufficient information is supplied.
- AI recommendations must state relevant assumptions and allow the user to correct them.
- A recommendation may not encourage extreme restriction, unsafe exercise progression, self-harm, doping, or other prohibited behaviour.
- Users can pause, replace, or reschedule a planned activity; adherence must distinguish a completed plan from a modified or skipped one.

### Data, progress, and reports

- Only user-authorised measurements and records contribute to progress views.
- Progress reporting must label insufficient data and avoid claiming causation from weak or incomplete data.
- Reports require a minimum, defined period and minimum meaningful data points; otherwise the system provides a data-completeness prompt rather than a misleading conclusion.
- Historical plan versions and meaningful changes must remain traceable so users can understand why advice changed.
- Users can request export and deletion according to the applicable privacy policy; deletion and retention exceptions must be explained.

### Roles, commercial rules, and operations

- Users may access only their own data unless they explicitly grant a defined scope of access to an authorised coach/trainer or organisation.
- A trainer cannot view or modify another trainer’s clients, nor alter a client plan outside their granted role and scope.
- Administrative access follows least privilege and is auditable; support access must be time-bounded or purpose-bound where feasible.
- Subscription entitlements determine premium access; billing status changes must be communicated clearly and never silently discard user data.
- Cancellation takes effect according to the published billing terms; refunds and disputes follow a documented policy.
- Achievement logic must reward sustainable behaviour and must not rank users by weight loss, starvation, unsafe volume, or other harmful incentives.

## 9. Non-Functional Requirements

| Area | Requirement |
| --- | --- |
| Performance | Common interactive views and daily actions should feel immediate under normal network conditions; long-running analysis must show status and never block ordinary logging. Targets are established and tested before launch. |
| Scalability | Services must scale independently where demand differs, especially coaching, notifications, reporting, and analytics. The design must tolerate seasonal and campaign-driven spikes. |
| Availability | User-critical daily functions have explicit availability objectives, graceful degradation, and clear maintenance communication. |
| Reliability | Important user actions are durable, idempotent where retries are possible, and protected from duplicate processing. Data corrections retain an audit trail. |
| Security | Apply least privilege, secure secret handling, encryption in transit and at rest, threat modelling, dependency management, vulnerability response, audit logs, abuse controls, and periodic security review. |
| Maintainability | Use clear domain boundaries, documented decisions, ownership, quality gates, test strategy, versioning, and a controlled deprecation process. Python remains the primary home for domain rules. |
| Accessibility | Meet WCAG 2.2 AA as the release standard: keyboard operation, semantic content, contrast, screen-reader support, focus management, reduced-motion support, and clear error states. |
| Internationalisation | Support locale-aware language, date/time, number, unit, currency, right-to-left readiness, and culturally relevant nutrition content. Never encode launch-market assumptions into product rules. |
| Monitoring | Monitor availability, latency, failures, queue health, data-processing health, AI safety events, billing reconciliation, and user-impacting feature health with actionable alerts. |
| Logging | Use structured, correlation-aware logs. Do not record secrets or unnecessary sensitive health data. Define retention, access, and redaction policy. |
| Backup strategy | Establish encrypted, tested backups with recovery-point and recovery-time objectives based on data criticality. Verify restoration regularly, not only backup creation. |
| Disaster recovery | Maintain incident roles, communication templates, runbooks, tested restoration procedures, dependency-failure plans, and periodic recovery exercises. |

## 10. Success Metrics

Metrics must be segmented by cohort, acquisition channel, plan, persona, region, and accessibility/language context where appropriate. They must never be used to pressure users into unsafe behaviour.

| KPI | Definition | Decision supported |
| --- | --- | --- |
| Activation rate | Registered users completing onboarding, assessment, and first meaningful action within a defined window. | Whether the first-use journey is understandable. |
| Assessment completion rate | Eligible users completing and accepting assessment. | Where onboarding friction exists. |
| Weekly/Daily active users | Unique users completing a meaningful product action in the period. | Product engagement health. |
| Workout completion rate | Planned sessions completed or validly modified divided by planned sessions. | Plan feasibility and adherence. |
| Nutrition adherence signal | User-selected adherence indicator over a period, interpreted with context. | Whether guidance is practical. |
| Retention | Cohort return and meaningful-action rate at week 1, week 4, month 3, and beyond. | Durable value and product-market fit. |
| AI usefulness | Rate of users rating guidance useful, acting on it, or requesting clarification; includes safety and override signals. | Coaching quality and trust. |
| Report engagement | Eligible users who review a periodic report and take a next action. | Whether insights drive reflection. |
| Subscription conversion | Eligible users starting paid service divided by eligible users, alongside cancellation and refund rates. | Commercial value and pricing fit. |
| Satisfaction | CSAT/NPS plus qualitative feedback and support themes. | Perceived product quality. |
| Safety and trust | Safety escalations, complaint rate, privacy incidents, and resolution time. | Responsible operation. |
| Service quality | Availability, latency, failure rate, support response time, and recovery exercise results. | Operational readiness. |

## 11. Graduation-Project Judge Review

### Evaluation

RAHFIT AI is a strong graduation-project concept because it combines a visible consumer experience with meaningful engineering depth: privacy, recommendation safety, role boundaries, personalisation, analytics, reliability, and a coherent product loop. It has a clear commercial narrative beyond a demo.

### Strengths

- Solves a common, understandable problem with concrete outcomes.
- Offers a disciplined scope: assessment → plan → action → feedback → adjustment.
- Demonstrates enterprise thinking through safety, consent, observability, quality, and operability requirements.
- Supports rich evaluation across product design, backend engineering, AI safety, UX, data handling, and business viability.

### Weaknesses and risks

- The feature surface is large; attempting every module will produce a shallow product.
- Personalisation quality depends on truthful, sufficiently complete user input.
- Health-adjacent guidance creates reputational, ethical, and regulatory risk.
- AI can be inconsistent, overly persuasive, or unsafe without robust constraints and evaluation.
- Retention is difficult: users often abandon fitness products after initial motivation fades.

### Missing parts to resolve before implementation

- Launch market, language strategy, target age policy, legal review, and precise medical-safety escalation policy.
- A concise first-release scope, content strategy, exercise/nutrition evidence-review process, and defined data retention policy.
- Success thresholds, usability research plan, AI evaluation rubric, incident response ownership, and pricing hypothesis.

### Path to first place

Win by building a narrow but complete, polished vertical slice rather than a broad mock-up: one persona-led assessment, transparent and safe plan rationale, excellent daily workflow, measurable progress, privacy controls, an audited quality process, and a live demonstration of graceful handling for incomplete or safety-sensitive inputs. Judges should see both product empathy and engineering discipline.

## 12. Startup Investor Review

### Investment view

The idea is investable in principle, but not yet investment-ready solely on the concept. Fitness and wellness are crowded markets; the investable case is a demonstrated wedge, superior retention, trusted personalisation, and a responsible data strategy—not the presence of AI alone.

### Why it can scale

- Subscription economics can compound when a genuinely useful daily product retains users.
- The coaching loop creates a differentiated experience as users build longitudinal history and preferences.
- A modular product can expand from consumer use into trainers, clubs, employers, universities, and regional partnerships.
- High-quality, consented product signals can improve personalisation and experimentation while preserving user privacy.

### Improvements required before launch

1. Choose one initial beachhead persona and one primary market.
2. Define the smallest paid promise and validate willingness to pay before broad feature expansion.
3. Establish clinical/safety advisory review, prohibited-advice policy, and AI evaluation standards.
4. Validate onboarding, plan adherence, and retention with usability tests and a small pilot.
5. Finalise privacy, consent, retention, security, support, billing, and incident-operating policies.
6. Create a disciplined roadmap with explicit stop/go metrics for each expansion area.

The investment thesis becomes compelling when RAHFIT AI proves that it can safely convert assessment into actions users complete repeatedly, at an acquisition cost and retention profile that support a durable subscription business.
