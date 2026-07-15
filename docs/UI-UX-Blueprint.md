# RAHFIT AI — Enterprise UX/UI Blueprint

**Status:** Official Sprint 2.7 pre-implementation specification  
**Scope:** Experience, interface, accessibility, and visual-system architecture only. This document contains no components, markup, styles, code, or design-file implementation.

## 1. UX Philosophy

RAHFIT AI should feel like a calm, capable personal coach: clear about today’s next action, respectful of uncertainty, and never judgmental. User-first design means every screen starts from a user need—understand, decide, act, recover, or review—not from the platform’s data structure. The experience reduces cognitive load through a single obvious next step, concise language, meaningful defaults, and progressive disclosure of advanced detail.

Trust is central. The interface explains why information is requested, what an AI recommendation is based on, what data is missing, and when the product cannot safely personalise. Safety notices are prominent without being alarming; they state a practical next step and never imply medical diagnosis. AI is transparent: it is labelled as assistance, exposes relevant assumptions and sources of context, and has a visible fallback when unavailable.

The product is mobile-first because workouts, meals, check-ins, and coach conversations happen away from a desk. It remains fully usable on larger screens through responsive layouts, not by shrinking a desktop dashboard. Consistency makes the product learnable; delight comes from small acknowledgement of real progress, considerate microcopy, responsive feedback, and a confident visual rhythm—not excessive animation or gamification.

## 2. Design Principles

| Principle | Design meaning |
| --- | --- |
| Minimal | Show the most relevant action and information first; hide secondary settings until requested. |
| Premium | Use generous whitespace, intentional hierarchy, polished states, clear data handling, and no visual clutter. |
| Clean | Use short labels, clear grouping, predictable actions, and restrained decoration. |
| Modern | Prefer responsive cards, contextual actions, understandable charts, and adaptive content over dense control panels. |
| Professional | Communicate safety, privacy, accuracy, and limitations plainly; never use exaggerated health claims. |
| Human | Use supportive, culturally respectful language and acknowledge real-life constraints, misses, and changes. |
| Friendly | Explain unfamiliar terms, offer examples, and make recovery from errors easy. |
| Motivational | Reward sustainable consistency and completed actions, never shame or reward unsafe restriction/overtraining. |
| Explainable | Pair recommendations and scores with “why this matters,” data completeness, and change controls. |
| Inclusive | Treat Arabic/RTL, English/LTR, accessibility, device constraints, and varied fitness experience as first-class requirements. |

## 3. Information Architecture

### Primary navigation

On mobile, the primary navigation prioritises **Today**, **Plan**, **Progress**, and **Coach**, with a profile/settings entry in the account area. On larger screens, these remain the stable primary destinations with contextual secondary navigation. A user should never need to know whether a feature belongs to workout, nutrition, recovery, or AI before finding their next action.

| Area/page | Purpose and primary content | Relationships |
| --- | --- | --- |
| Landing | Explain value, trust, audience, pricing direction, and clear start action. | Leads to registration; references safety/privacy without overload. |
| Authentication | Registration, sign-in, verification, password recovery, and session state. | Returns user to intended destination; does not mix product onboarding with credential recovery. |
| Onboarding / Assessment | Build a safe, adaptive profile with save/resume and transparent data use. | Produces readiness/safety state for Today, Plan, Coach, and Settings. |
| Today / Dashboard | Daily command centre: current priority, safe next action, summary, and notices. | Aggregates workout, nutrition, water, progress, coach, and notifications. |
| Plan | Current workout/nutrition/recovery plan and future schedule; change/review entry. | Opens sessions, meal actions, plan rationale, and reassessment when needed. |
| Workout | Current session, exercise library, history, and pain/reporting path. | Uses plan and assessment safety status; completion updates Progress/Today. |
| Nutrition | Current guidance, meal logging, water, daily summary, preferences. | Uses dietary restrictions; updates Today/Progress. |
| Progress | Trends, measurements, goals, achievements, and data-completeness explanation. | Opens Reports and goal review; avoids unsupported conclusions. |
| Reports | Periodic summaries, data sufficiency, next focus, and history. | Draws from Progress/Plans; uses AI narrative only as labelled explanation. |
| AI Coach | Bounded conversation, suggestions, context/memory controls, safety/fallback state. | Links to relevant Plan, Assessment update, or safe non-AI action. |
| Notifications | Read/unread actionable reminders and preference access. | Links to the originating safe destination; no dead-end alerts. |
| Profile and Settings | Identity presentation, units/language/timezone, privacy, accessibility, notifications, preferences, data controls. | Changes may affect all presentation and planning experiences. |
| Support | Help, issue reporting, privacy help, and non-emergency safety guidance. | Distinct from AI Coach and clearly not emergency care. |
| Admin | Strictly role-gated operational health, user status, audit/flag access, and support workflows. | No sensitive health details by default; separate from consumer navigation. |

## 4. User Flows

| Flow | Steps and experience requirements |
| --- | --- |
| Registration | Landing value/trust → registration → verification state → choose Quick Start or Full Assessment → return to intended safe destination. Show password/verification errors inline without account disclosure. |
| Assessment | Welcome and purpose → mode choice → adaptive sections → save/resume → review answers/missing-data impact → deterministic safety outcome → completion/readiness summary → transition to Today or AI analysis. Earlier edits visibly refresh dependent questions. |
| Workout | Today/Plan → session preview → start → exercise cards and set logging → rest/next exercise → pain report or substitution when needed → completion reflection → updated progress/next recovery action. |
| Nutrition | Today/Nutrition → daily target/context → quick meal or water action → optional detail → confirmation → updated summary; restriction update routes to plan review when relevant. |
| Daily check-in | Today prompt → energy/fatigue/adherence answer → confirm → adjusted daily emphasis or neutral acknowledgement. It must never diagnose or overreact to one entry. |
| AI conversation | Coach entry → visible purpose/context indicator → message or suggestion → loading/response → explanation/source cues → feedback, correction, or linked action → memory control. Safety/timeout routes to a clear fallback. |
| Goal update | Progress/Profile → review current goal → describe change → impact explanation → targeted reassessment where needed → confirm revision → plan review rather than silent plan replacement. |
| Subscription | Feature value explanation → plan comparison → consented purchase flow → verified state → entitlement confirmation/manage/cancel path. It never blocks safety or data-control actions. |
| Profile editing | Profile → grouped preference/privacy sections → edit → validation → save confirmation → impact notice if plan, language, timezone, or consent changes. |

All flows include a back path, recoverable error state, loading state, success acknowledgement, and clear handling for session expiry or limited connectivity. Destructive actions require confirmation and explain their effect.

## 5. Dashboard Experience

The dashboard is the daily “what matters now?” view, not a dense report. It uses a vertical priority order on mobile and an adaptive grid on larger displays. The first viewport should answer: What should I do today? Is anything safety-sensitive or missing? How am I progressing?

| Widget/card | Content and behaviour |
| --- | --- |
| Daily focus | One primary next action—start workout, log meal, complete assessment, recover, or review safety notice—with time/context explanation. |
| Safety/readiness notice | Persistent when caution, clearance, incomplete assessment, or stale plan matters. Uses clear non-diagnostic language and a safe action. |
| Today’s workout | Session title, duration, equipment context, state, and start/resume action; shows conservative status when needed. |
| Nutrition and water | Practical daily summary, meal/water quick actions, and data-completeness cue; no shaming progress indicator. |
| Goal progress | One meaningful trend or milestone, period label, and link to Progress. Includes insufficiency state when evidence is weak. |
| Recovery check | Optional compact energy/fatigue prompt and permitted recovery guidance. |
| AI Coach card | Contextual suggestion or safe availability/fallback state; opens Coach, never forces chat. |
| Quick actions | Log water, log meal, start workout, check in, update availability, or reassess—limited to highest-value actions. |
| Notifications | Count and most relevant actionable item, with link to full inbox. |

Health/recovery scores are never presented as medical facts. Any score includes plain-language meaning, trend period, data completeness, and a “how this is calculated” entry. Dashboard partial failure preserves usable cards with last-updated/freshness labels; safety state is never treated as a stale optional widget.

## 6. Assessment UX

The assessment begins by explaining its benefit, time estimate, privacy, and Quick Start versus Full Personalization choice. Progress uses clear section names and an estimated remaining effort rather than a misleading fixed question count, because adaptive questions vary. Consequential and sensitive prompts use one question per screen; related low-risk preferences may be grouped to reduce friction.

Save is automatic after meaningful input and also explicitly available. Resume returns to the last safe checkpoint with a brief summary of completed sections. The user can go back, edit, skip optional questions, or choose “I don’t know” when valid. Required questions explain why they are needed; sensitive questions include a concise purpose link before input. Editing a branch-driving answer explains what later answers will need review.

Validation appears near the relevant input, uses plain language, preserves entered content, and offers a recovery action. Interrupted/offline behaviour preserves only securely permitted draft progress and communicates sync status; a duplicate completion never creates competing results. Completion celebrates the effort, then presents readiness, missing-data effect, safety state, and the next safe action—not a generic “perfect plan” promise.

Animations are subtle, optional, and never the only indicator of progress/state. Accessibility includes semantic progress, predictable focus after branches/errors, screen-reader announcements, touch target size, keyboard completion, and RTL-aware order/alignment.

## 7. AI Coach UX

AI Coach is a purpose-led conversation, not an unbounded chatbot. The entry state shows what it can help with, a short context indicator such as “using your current plan and preferences,” and easy suggested intents: explain today’s workout, adapt to time/equipment, review nutrition guidance, or reflect on progress. The user can inspect and correct relevant context through linked profile/assessment controls rather than trusting hidden memory.

Messages distinguish user, coach, system, and safety notices visually and semantically. Suggestions are action-oriented and link to a reviewable Plan, Workout, Nutrition, or Assessment destination. A memory indicator explains when a durable preference is being used or proposed; the user can inspect, edit, or remove eligible memory. The UI never claims that AI knows something it cannot show as approved context.

Loading uses a concise progress state and cancel/continue option where appropriate; typing animation is optional/reduced-motion aware and never disguises a long wait. Timeout/unavailability displays a respectful fallback: explain that AI assistance is unavailable, preserve the user message, and provide deterministic plan or help-path content where permitted. Confidence is communicated as data readiness/uncertainty (“I need an update to personalise this safely”), not a fabricated percentage.

Safety warnings interrupt normal recommendation display, use calm non-diagnostic language, state the restriction, and link to reassessment/support/professional-advice guidance. The coach must not create urgency, shame, dependency, or medical authority.

## 8. Workout UX

Workout begins with a calm preview: purpose, estimated duration, equipment, session state, safety constraints, and a start action. Exercise cards prioritise name, simple instruction, prescribed effort, completion state, alternatives, and a link to approved guidance. Advanced technique detail is progressive, never required to complete a basic session.

During a session, the interface focuses one exercise/set at a time with visible overall progress, easy set logging, pause, substitution, skip, and pain-report actions. Rest timer is useful but never traps the user; it can be adjusted, muted, or dismissed and is accessible without relying on colour or motion. Substitution explains why the alternative fits equipment/time/limitation context. Pain reporting is always prominent and routes to the safety flow without blame.

Completion asks for concise reflection such as perceived effort or issue, recognises completion/valid modification, and shows the next recovery or schedule action. It does not reward extreme load, compare users, or imply that skipped/modified sessions are failure.

## 9. Nutrition UX

Nutrition screens reduce logging friction while respecting that nutrition data is personal and sometimes sensitive. The daily view presents current guidance, an easy meal/water action, a practical summary, dietary restrictions, and a clear distinction between logged facts and estimates. Meal logging begins with the smallest useful input and progressively reveals amount, timing, meal grouping, or note options.

Water tracking supports common quick amounts plus an accessible custom entry. Calories/macros, where included, use plain-language labels, target source/period, and neutral feedback; they never use red/green judgement alone or frame under-eating as success. Dietary restrictions are visible in plan-related contexts with an easy update path and a warning that changes can require plan review. Future meal scanning is explicitly post-competition and must not be implied by the core UI.

## 10. Visual Design System

| Element | System direction |
| --- | --- |
| Typography | A legible, highly supported type family with clear scale for display, section, body, label, and numeric data. Arabic and Latin pairing must have comparable weight, rhythm, and readability. |
| Spacing/layout | A small, consistent spacing scale; generous mobile breathing room; responsive content width; stable alignment and predictable section rhythm. |
| Colour philosophy | Calm neutral foundation with one confident primary action colour, supportive semantic colours, and restrained accent colour. Colour is never the only status signal. |
| Light/dark modes | Both are first-class themes with equivalent hierarchy, contrast, semantic state visibility, chart readability, and media treatment. System preference is respected with user override. |
| Icons | Familiar, simple icons paired with labels for critical actions; mirrored/locale-aware where direction is semantic; never the sole meaning for safety/destructive actions. |
| Cards | Cards group one coherent concept, use consistent padding/title/action placement, and avoid nesting cards excessively. |
| Buttons | Clear primary, secondary, tertiary, destructive, and disabled states. One primary action per context; labels describe outcome rather than vague verbs. |
| Forms | Persistent labels, helpful descriptions, visible required/optional status, inline validation, accessible error summary, and safe input formatting. |
| Charts | Start with a question (“How is my trend changing?”), label period/unit/source, support text alternatives, and show insufficient-data state. Avoid dense dashboards or implied causality. |
| Feedback states | Loading, empty, success, warning, error, offline, blocked, and stale states use shared language, iconography, layout, and recovery actions. |

The system is governed by reusable tokens and component behaviour specifications in later implementation, but this blueprint does not prescribe a technical styling solution. Consistency is assessed across state, language, RTL direction, keyboard behaviour, and data/safety semantics—not only visual resemblance.

## 11. Accessibility

The experience targets WCAG 2.2 AA intent before competition. All primary flows work with keyboard-only navigation, logical focus order, visible focus, skip mechanisms, semantic headings, labelled controls, error summaries, and screen-reader announcements for branch changes, saving, timers, and validation. Touch controls have sufficient target size and never rely on hover.

Text and essential graphics meet contrast needs in light and dark mode; status uses text/icon/shape in addition to colour. Large text, browser zoom, and narrow screens retain readable hierarchy without clipping, forced horizontal scrolling, or lost actions. Reduced-motion preference removes nonessential animation while preserving state changes through text and layout. Rest timers and progress feedback have non-motion alternatives.

Arabic is not a translated afterthought: RTL layout mirrors navigation, alignment, icon direction, progress order, charts where meaning requires, and form behaviour; numerals, dates, units, and mixed-language content remain understandable. English/LTR receives equivalent quality. Locale changes do not accidentally alter stored facts, only presentation and user-local interpretation.

## 12. Competition Scope

| Must Build Before Competition | If Time Allows | Post Competition |
| --- | --- | --- |
| Premium mobile-first shell; landing/auth states; adaptive assessment UX with save/resume/validation/safety; Today dashboard; basic workout session; basic meal/water logging; Progress summary; one bounded Coach flow with loading/fallback; profile/settings; shared light/dark and Arabic/RTL-ready visual language; core accessibility states. | Weekly reports, notification inbox, goal review, recovery check-in, football/goalkeeper UX, avatar/progress-photo flow, deeper motion/detail polish. | Subscription purchase, coach/organisation workspace, vision/meal scan/form video, wearables, voice coach, community, marketplace, advanced analytics/admin. |

The competition experience should demonstrate a complete polished loop: onboarding and safe assessment, clear daily dashboard, a practical workout or nutrition action, a progress update, and explainable bounded AI assistance. This earns more credibility than many incomplete screens.

## 13. Judge Review

| Dimension | Evaluation |
| --- | --- |
| Originality | Strong: the “trusted adaptive coach” framing differentiates the experience from generic tracker dashboards. |
| Usability | Strong if the primary daily action is always clear and assessment remains short/recoverable. |
| Consistency | Strong: shared state, card, form, safety, and navigation principles are explicit. |
| Accessibility | Strong at specification level through keyboard, screen-reader, contrast, reduced-motion, Arabic, and RTL requirements. |
| Competition readiness | Good when the team implements the focused vertical slice rather than every future page. |

**Strengths:** safety/AI transparency is visible, mobile constraints are respected, and product flows are connected rather than separate screens.  
**Weaknesses:** a premium visual system requires disciplined implementation and usability testing; no design can compensate for slow or unreliable underlying features.  
**Risks:** overloading the dashboard, making AI too chat-centric, using gamification that harms users, and treating RTL as a final translation task.  
**Score:** 92/100 as a UX blueprint. A first-place result needs a coherent prototype/implementation with real accessibility checks and a polished safety flow.

## 14. Startup Review

Users may pay when the product reliably saves planning time, makes daily actions feel feasible, explains why guidance fits them, and shows meaningful progress without judgement. They return when Today is useful in under a minute, reminders are helpful rather than intrusive, plans adapt to real constraints, and the coach remembers only what the user wants it to remember.

Retention improves through a strong activation moment after assessment, realistic daily actions, visible streak alternatives that reward flexibility, weekly reflection, respectful re-engagement after absence, and transparent progress/data completeness. The premium opportunity is not decorative UI; it is trusted adaptive coaching, deeper reports, sport-specific value, and smooth support across a user’s changing life. The first release should avoid visual complexity that obscures the core daily loop.

## 15. Definition of Done

Sprint 2.7 is complete only when UX philosophy, design principles, information architecture, user flows, dashboard, assessment, AI Coach, workout, nutrition, visual system, accessibility, competition scope, judge/startup reviews, and README link are documented; no implementation code or interface artefacts are created; and the competition scope remains a realistic, testable vertical slice.
