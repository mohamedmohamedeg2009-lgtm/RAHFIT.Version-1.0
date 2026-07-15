# RAHFIT AI — Smart Adaptive Assessment Blueprint

**Status:** Official Sprint 2.3 pre-implementation specification  
**Scope:** Product, safety, UX, and future-service requirements only. This document contains no code, API, database schema, or implementation design.

## 1. Assessment Goal

The Smart Adaptive Assessment is RAHFIT AI’s trusted intake and reassessment experience. It builds a current, user-controlled profile of goals, ability, lifestyle, equipment, preferences, recovery, nutrition context, and safety constraints. Its purpose is to make the first plan useful without making the first experience exhausting.

It solves three core problems: generic advice that ignores context, repeated questioning across product experiences, and unsafe automation when important constraints are absent. The AI Coach, workout generation, nutrition planning, recovery guidance, health/progress views, reports, dashboard priorities, and notifications all depend on its approved outputs.

A fixed questionnaire is insufficient because a busy beginner with no equipment, a football goalkeeper, and a user reporting pain do not need the same questions. Adaptive branching asks only relevant follow-up questions, clearly explains sensitive requests, and records uncertainty when the user chooses not to answer. It improves personalisation by making consequential inputs explicit and versioned rather than inferring them from incomplete data.

For competition judges, it demonstrates responsible AI, domain reasoning, UX discipline, testable rule design, privacy awareness, and realistic scope. For commercialization, it creates reusable structured context that can support retention, premium coaching, coach/organisation workflows, and future integrations without treating users as a static profile.

## 2. User Value and Business Value

| Area | Value |
| --- | --- |
| Better plans | The plan reflects goal, experience, time, equipment, preferences, and constraints rather than a generic template. |
| Safer recommendations | Deterministic screening identifies when automation must be conservative or paused for professional advice. |
| Less repetition | Approved answers become a governed source of context for later coaching conversations and reviews. |
| More relevant AI conversations | The coach starts with validated context, states its assumptions, and asks focused follow-ups instead of re-collecting everything. |
| Clearer goals and tracking | Users see what they are aiming for, what information is missing, and why their plan changes over time. |
| Completion and retention | A short, staged flow lowers first-session burden; reassessment makes the product remain relevant as life changes. |
| Subscription value | Personalisation and plan continuity create a clear premium benefit beyond generic content. |
| Reusable data | Permissioned, structured outputs improve product quality, analytics, reporting, and future service boundaries. |

## 3. Assessment Principles

| Principle | Effect on the assessment |
| --- | --- |
| Progressive disclosure | Start with a short path, then reveal only questions necessary for the selected goal, context, or risk. |
| Minimum necessary data | Do not collect a field because it might be useful someday; collect it only for a stated coaching, safety, or operational purpose. |
| Adaptive branching | Earlier answers determine relevant follow-ups, skipped sections, and safe plan boundaries. Branches must be deterministic and reviewable. |
| Clear consent | Explain data use before sensitive, AI-processing, or media-related questions; consent is separate from ordinary form completion. |
| User control | Users may save, resume, review, edit, skip optional answers, withdraw optional consent, export, and request deletion. |
| Safe defaults | Incomplete, uncertain, or risk-sensitive input results in conservative guidance or a pause—not optimistic assumptions. |
| Explainability | Explain why a sensitive question matters and expose the assumptions behind the resulting profile. |
| Data minimisation | Keep raw sensitive content out of analytics and collect the smallest useful granularity. |
| Accessibility | Support keyboard, screen reader, large text, clear language, contrast, reduced motion, and error recovery. |
| Mobile-first flow | Use short prompts, appropriate input controls, lightweight saving, and interruption tolerance. |
| Save and resume | Persist a draft safely after meaningful progress; never force a user to restart because a session ends. |
| Editable answers | Changing an earlier answer recalculates dependent branches and identifies answers that need review. |
| No medical diagnosis | The system screens for risk and directs users to appropriate professionals; it does not diagnose conditions or prescribe treatment. |
| Human escalation | When rules require professional clearance or a support/safety review, automation is bounded and the user receives clear next steps. |

## 4. Assessment Modes

| Mode | Purpose and target user | Duration and sections | Trigger and expected output | Competition priority |
| --- | --- | --- | --- | --- |
| Quick Start | Let a new user begin with a conservative, basic plan. | About 4–7 minutes; basic profile, goal, experience, time/equipment, essential safety, preferences/consent. Optional nutrition/recovery prompts. | User chooses quick start; produces limited-readiness profile, missing-data list, conservative plan boundary, reassessment prompt. | Must build. |
| Full Personalization | Build a robust profile for users wanting better training/nutrition/recovery relevance. | About 10–15 minutes; all core sections except sport-specific branches unless triggered. | Selected by user, upgrade from Quick Start, or needed for higher personalisation; produces full profile and confidence/readiness result. | Must build. |
| Athlete | Capture sport schedule and performance context for football players, goalkeepers, runners, or similar users. | About 8–12 additional minutes; full core plus sport section. | Goal/sport selection or athlete identity; produces sport profile, training-load constraints, and athlete-plan eligibility. | Build if time allows; football/goalkeeper branch is the preferred competition extension. |
| Injury-Aware | Safely capture a reported limitation without diagnosis. | About 3–7 additional minutes; safety screening and limitation-specific follow-ups. | Pain, injury, surgery, movement limitation, or serious symptom response; produces safety status, restricted features, and clearance requirement. | Must build. |
| Reassessment | Refresh stale or materially changed context. | About 2–10 minutes, limited to changed domains. | Scheduled review or reported goal, weight, schedule, equipment, injury, recovery, or sport change; produces new assessment revision and plan-review requirement. | Must build for a focused set of triggers. |

Competition implementation should support Quick Start, Full Personalization, Injury-Aware branching, and targeted Reassessment. The athlete flow should be limited to football and goalkeeper if included; other sports can remain a declared expansion path.

## 5. Assessment Sections

### A. Basic Profile

| Design element | Specification |
| --- | --- |
| Objective | Establish presentation, measurement, locale, and age-related eligibility context. |
| Questions and answer type | Preferred name (short text); age range or date of birth (date/range); height and weight (numeric with unit); preferred units (selection); country, language, timezone (selection). Biological sex is a conditional selection only when it is technically needed for a transparent, approved calculation or safety context. |
| Required / validation | Preferred name, age eligibility, units, and timezone are required. Height/weight are required only for plans or calculations that need them; positive, plausible values and unit consistency are validated. |
| Branching and rationale | Underage route applies extra safeguards. Locale controls language, units, time-based scheduling, and policy presentation. Missing height/weight narrows personalisation rather than blocking every flow. |
| Python logic use / safety / priority | Future domain logic normalises units and applies eligibility/readiness rules. Do not infer sex or use it where unnecessary. Critical for competition. |

### B. Main Goal

| Design element | Specification |
| --- | --- |
| Objective | Identify the primary outcome and relevant plan path. |
| Questions and answer type | Primary goal and optional secondary goals: weight loss, muscle gain, general fitness, strength, endurance, mobility, sports performance, football, goalkeeper performance, healthy habits, or other (selection plus optional text). |
| Required / validation | One primary goal is required; a controlled number of secondary goals is optional. “Other” requires a short clarification. |
| Branching and rationale | Goal selects detail prompts and may invoke sport, nutrition, time, or safety follow-ups. It avoids one-size-fits-all plans. |
| Python logic use / safety / priority | Future logic selects goal-appropriate constraints and review cadence. No goal authorises unsafe rates or extreme programmes. Critical. |

### C. Goal Details

| Design element | Specification |
| --- | --- |
| Objective | Convert a broad goal into a feasible, user-owned priority. |
| Questions and answer type | Desired outcome, target weight where relevant (numeric/range), desired timeline (date/range), priority ranking, motivation, previous attempts, and success definition (selection/text). |
| Required / validation | Desired outcome and priority are required for Full Personalization. Dates must be future-oriented and targets must pass safe-realism rules; motivation and prior attempts are optional. |
| Branching and rationale | Weight-related goals prompt safe timeline/expectation checks; multiple goals require primary-priority confirmation. |
| Python logic use / safety / priority | Logic produces a goal-realism indicator and plan emphasis, never a medical claim. Unsafe targets create caution or stop status. Critical. |

### D. Experience Level

| Design element | Specification |
| --- | --- |
| Objective | Set starting complexity, instruction depth, and progression conservatism. |
| Questions and answer type | Self-rated level (beginner/intermediate/advanced), training history, exercise familiarity, previous programmes, recent consistency (selection/range/text). |
| Required / validation | Level and recent experience are required; detailed programme history is optional. Conflicting claims prompt a neutral clarification. |
| Branching and rationale | Beginners receive familiarity and confidence prompts; advanced users may receive training-history detail. |
| Python logic use / safety / priority | Logic determines explanatory depth, initial exercise complexity, and conservative progression boundaries. Critical. |

### E. Activity and Lifestyle

| Design element | Specification |
| --- | --- |
| Objective | Fit recommendations into the user’s actual week. |
| Questions and answer type | Daily activity, work/study pattern, sitting time, optional steps, available workout days, session duration, preferred training time (selection/range/multi-select). |
| Required / validation | Available days and session duration are required for workout planning; all time/quantity entries have reasonable bounds. |
| Branching and rationale | Less than 20 minutes triggers short-session options; sedentary lifestyle supports gradual activity prompts. |
| Python logic use / safety / priority | Logic constrains weekly frequency, session length, reminder timing, and habit suggestions. Critical. |

### F. Equipment and Environment

| Design element | Specification |
| --- | --- |
| Objective | Ensure exercises are practical and substitutable. |
| Questions and answer type | Home/gym/outdoor environment, available equipment, space limits, travel frequency (multi-select/selection). |
| Required / validation | At least one environment is required; equipment may be “none.” Travel is optional. |
| Branching and rationale | No equipment or limited space selects bodyweight/low-space options; travel requests portable alternatives. |
| Python logic use / safety / priority | Logic filters and substitutes exercises; it must never assume gym access. Critical. |

### G. Health and Safety Screening

| Design element | Specification |
| --- | --- |
| Objective | Identify whether normal automation may continue, must be conservative, or must pause pending professional advice. |
| Questions and answer type | Current pain, known injury, prior surgery, movement limitation, relevant chronic-condition disclosure, medication relevance, pregnancy-related consideration where applicable, dizziness/chest pain/fainting/serious warning signs, and clearance status (yes/no/unsure with conditional detail). |
| Required / validation | Core screening and serious-warning responses are required before personalised exercise/nutrition plans. Users may decline optional detail but receive reduced readiness. |
| Branching and rationale | Any positive screen reveals only relevant, plain-language follow-ups and a reason for asking. Serious symptoms trigger a stop route; pain/injury triggers Injury-Aware mode. |
| Python logic use / safety / priority | Deterministic safety rules produce normal/caution/stop status and feature restrictions. The platform does not diagnose, treat, or replace a clinician, physiotherapist, or dietitian. Critical. |

### H. Sleep and Recovery

| Design element | Specification |
| --- | --- |
| Objective | Adapt workload and recovery expectations to current wellbeing context. |
| Questions and answer type | Average sleep duration, sleep quality, energy, fatigue, rest days, recovery habits, stress level (range/selection). |
| Required / validation | Sleep duration, fatigue/energy, and rest preference are required for Full Personalization; values have reasonable bounds. |
| Branching and rationale | Poor sleep/high fatigue prompts short recovery follow-up and conservative workload boundary. |
| Python logic use / safety / priority | Logic creates a non-medical recovery-risk indicator and review prompt. It must not diagnose sleep or mental-health conditions. High. |

### I. Nutrition Profile

| Design element | Specification |
| --- | --- |
| Objective | Make nutrition guidance relevant, safe, and culturally practical. |
| Questions and answer type | Dietary preference, allergies, intolerances, religious/cultural restrictions, meals/day, cooking ability, budget, food access, water intake, supplements, eating challenges (selection/multi-select/range/text). |
| Required / validation | Dietary preference and allergy/intolerance status are required before nutrition personalisation; all other fields are optional or Full-mode required. Allergy responses require clear confirmation. |
| Branching and rationale | Allergies/restrictions trigger relevant avoidance and substitution questions; eating-challenge warnings trigger caution/stop review. |
| Python logic use / safety / priority | Logic filters guidance and records limits; it does not prescribe medical diets or advise on medication/supplement safety. Critical for basic preferences/allergies; remaining depth high. |

### J. Habits and Behavior

| Design element | Specification |
| --- | --- |
| Objective | Tailor the level of structure and support needed for adherence. |
| Questions and answer type | Consistency, motivation style, reminder/accountability preference, obstacles, confidence, social support (selection/range/optional text). |
| Required / validation | Reminder preference and one obstacle/confidence measure are recommended in Full mode; all can be skipped. |
| Branching and rationale | Low confidence or time barriers offers simplified routines and opt-in reminders; it does not shame the user. |
| Python logic use / safety / priority | Logic adapts communication cadence and habit emphasis; it never infers mental-health diagnoses. High. |

### K. Sports-Specific Profile

| Design element | Specification |
| --- | --- |
| Objective | Adapt a plan to football/goalkeeper demands and schedule. |
| Questions and answer type | Sport, position, training/match schedule, priorities (speed, agility, strength, jumping, reaction), prior sports injury, competition level (selection/multi-select). |
| Required / validation | Sport and schedule are required only for athlete flow; goalkeeper selection requires position confirmation. |
| Branching and rationale | Football opens position and fixture questions; goalkeeper opens jumping/reaction/shoulder-hip movement context. Injury prompts Injury-Aware screening. |
| Python logic use / safety / priority | Logic protects match-day/recovery windows and selects sport emphasis without guaranteeing performance. Build if time allows. |

### L. Preferences

| Design element | Specification |
| --- | --- |
| Objective | Improve plan usability and communication fit. |
| Questions and answer type | Preferred styles, disliked exercises, intensity preference, coach tone, language, notification and accessibility preferences (selection/multi-select). |
| Required / validation | Language and notification choice are required; exercise/style preferences are optional. Accessibility answers are optional and treated respectfully. |
| Branching and rationale | Disliked exercises seek alternatives; accessibility needs adapt presentation and interaction. |
| Python logic use / safety / priority | Logic filters presentation/options and communication style; safety restrictions override preference. High. |

### M. Consent and Privacy

| Design element | Specification |
| --- | --- |
| Objective | Give users meaningful control over personal, sensitive, and optional AI/media processing. |
| Questions and answer type | Purpose-specific data-use notice, AI-processing consent, sensitive-data acknowledgement where required, progress-photo consent, optional-question rights, edit/delete/export rights (acknowledgement/selection). |
| Required / validation | Required legal notices and core consent must be recorded with version and time. Optional AI/media consent is never bundled. |
| Branching and rationale | Declining optional processing disables only dependent features and explains the effect. |
| Python logic use / safety / priority | Future logic gates AI memory, media processing, and sensitive contextual use by consent and policy version. Critical. |

## 6. Adaptive Branching Logic

| Trigger | Additional questions | Skip or change | Safety response | Personalisation effect |
| --- | --- | --- | --- | --- |
| User is under the applicable age threshold | Age-appropriate eligibility, guardian/market policy path, non-extreme goal clarification. | Skip adult-only assumptions and restrict unavailable features. | Conservative default; block extreme plans; professional/guardian route where policy requires. | Limited profile and age-appropriate guidance only. |
| Pregnancy-related consideration reported | Whether professional clearance is held and whether exercise guidance is already approved. | Skip generic progression/weight-target assumptions. | Caution or stop based on clearance/risk answers; no diagnosis. | Restrict plan to approved conservative scope or pause personalisation. |
| Chest pain, fainting, severe shortness of breath, or comparable serious warning sign | No further fitness detail required beyond immediate safety routing. | Skip workout generation and normal goal planning. | Stop and seek appropriate professional advice; emergency wording where immediate symptoms are described. | No normal exercise/nutrition recommendation. |
| Pain, injury, surgery, or movement limitation | Location/category, severity description, timing, impact, clearance status, movements to avoid. | Skip incompatible exercise preference/progression questions until safe context is known. | Injury-Aware route; caution or stop; request professional clearance where indicated. | Constraints and feature restrictions, not diagnosis. |
| No equipment or limited space | Available space, safe household alternatives, travel context. | Skip gym-machine exercise preferences. | Normal unless other safety issue. | Bodyweight, portable, short-space options. |
| Beginner | Familiarity, confidence, preferred learning format. | Skip advanced-volume/programme detail unless volunteered. | Conservative starting boundary. | More instruction, simpler movement selection, slower progression. |
| Athlete / sport performance | Sport, competition level, weekly training/match schedule, recovery context. | De-emphasise generic fitness questions already answered by sport profile. | Caution when load/recovery signals are poor. | Plan timing respects training and match windows. |
| Football selected | Position, training/match schedule, performance priority, prior sports injury. | Skip unrelated sport detail. | Injury branch if relevant. | Football-oriented strength, mobility, conditioning emphasis. |
| Goalkeeper selected | Goalkeeper confirmation, jumping/reaction priorities, position-specific load context. | Skip outfield-only prompts. | Same injury safety rules. | Goalkeeper-specific emphasis, subject to later content validation. |
| Weight loss selected | Target/timeline, prior approach, eating challenges, preference and food-access context. | Skip muscle-gain-specific target prompts except secondary goal. | Flag dangerous timelines/eating-disorder warnings; do not encourage restriction. | Adherence-oriented nutrition/activity planning. |
| Muscle gain selected | Experience, training frequency, equipment, nutrition preference, realistic timeline. | Skip weight-loss-specific target framing unless a secondary goal. | Caution for unsafe supplementation or unrealistic expectations. | Strength/progression and practical nutrition emphasis. |
| Food allergy or intolerance | Confirm food/category, severity wording, avoidance and cross-contact concern where appropriate. | Skip unsafe generic meal suggestions. | Avoidance constraint; seek professional advice for uncertainty/severe concerns. | Filters food guidance; never guarantees allergen safety. |
| Less than 20 minutes available | Preferred short-session frequency and activity breaks. | Skip long-session volume assumptions. | Normal. | Short sessions, simplified habit plan, flexible schedule. |
| Poor sleep, high fatigue, or high stress | Duration/persistence and user-selected recovery capacity. | Reduce intensity/volume assumptions. | Caution; professional advice route if serious symptoms/safety concern arise. | Conservative workload and recovery emphasis. |
| Optional answer skipped | Ask whether user prefers to continue; identify the capability affected. | Do not repeatedly demand the field. | Safe default if the omission is consequential; required safety fields cannot be skipped. | Lower confidence/readiness and targeted reassessment prompt. |

Changing a branch-driving answer must recompute the visible questions, invalidate only dependent answers, preserve unrelated answers, and show the user what needs review before completion.

## 7. Safety and Red-Flag Rules

| Status | Examples | Application response | AI must not say | Restrictions and persistence |
| --- | --- | --- | --- | --- |
| Normal | No reported limiting symptoms; answers fit safe, supported boundaries. | Continue with ordinary non-medical coaching and clear assumptions. | Do not guarantee outcomes or claim medical certainty. | Assessment can complete; normal personalisation is eligible. |
| Caution | Mild/current pain, known injury with clearance, recovery concerns, uncertain medication relevance, low confidence, poor sleep/high fatigue, unrealistic-but-not-extreme goal. | Explain that recommendations will be conservative; request only necessary clarification; suggest appropriate professional advice when needed. | Do not diagnose, prescribe rehabilitation, dismiss pain, or encourage pushing through symptoms. | Assessment can save/complete; limit intensity, affected movements, autonomous adjustments, or nutrition claims. Clearance flag may be recommended. |
| Stop and seek professional advice | Chest pain, fainting, severe shortness of breath, severe uncontrolled pain, serious recent injury, recent surgery without clearance, dangerous symptoms, eating-disorder warning signs, dangerous weight-loss target, underage request for extreme plan. | Display clear, calm non-diagnostic safety message and appropriate urgency language. Permit saving and later editing. | Do not generate normal workout/nutrition recommendations, provide medical treatment, advise ignoring symptoms, or offer extreme restriction/training. | Personalised generation is paused; professional-clearance flag is required before relevant features resume. Safety event is audited with minimum necessary detail. |

Hard safety rules are deterministic and take precedence over AI suggestions, user preference, subscription state, and goal urgency. The user is never told that the application has diagnosed a condition. Where immediate serious symptoms are described, the message directs the user to seek urgent local medical help rather than waiting for the product.

## 8. Assessment Outputs

| Output | Meaning | Consumers |
| --- | --- | --- |
| Completion status and assessment version | Draft, incomplete, completed, superseded, or blocked state plus the applied question/rule version. | All future modules, support, audit. |
| User goal profile | Primary/secondary goals, priority, outcome definition, timeframe, realism context. | AI Coach, Workout Generator, Nutrition Planner, Dashboard, Reports. |
| Fitness and lifestyle profile | Experience, recent activity, available days/time, environment, equipment. | Workout Generator, Dashboard, Notifications, Health/Progress views. |
| Nutrition profile | Preferences, allergies/intolerances, food context, readiness and limits. | Nutrition Planner, AI Coach, Reports. |
| Recovery profile | Sleep, energy, fatigue, stress, rest context. | Recovery Score, Workout Generator, Dashboard, Notifications. |
| Injury/limitation profile | Reported constraints, clearance status, safety rule outcome; never a diagnosis. | AI Coach, Workout Generator, safety workflow. |
| Sports profile | Sport/position/schedule/priorities where supplied. | Sport-aware workout planning, Reports. |
| Motivation and preference profile | Communication, reminder, accountability, accessibility, exercise preferences. | AI Coach, Notifications, UI presentation. |
| Safety status and professional-clearance requirement | Normal/caution/stop outcome, restricted capabilities, required review condition. | Every recommendation-producing module. |
| Missing-data indicators, confidence, readiness, reassessment date | Explicit coverage/uncertainty and next review trigger. | Dashboard, AI Coach, Reports, Notifications. |

Outputs are structured, versioned facts and derived states for future Python domain services. They do not expose raw sensitive answers to every consumer: each downstream module receives only the minimum approved context it needs.

## 9. Scoring and Derived Metrics

| Metric | Purpose and inputs | Interpretation and limits | Visible / competition priority |
| --- | --- | --- | --- |
| Assessment completeness | Required and relevant optional sections completed, weighted by selected mode. | Indicates usable coverage, not health quality or user commitment. | Visible as progress/readiness; must build. |
| Personalisation confidence | Completeness, answer consistency, currentness, and unambiguous constraints. | Indicates how specifically guidance can be tailored; never implies accuracy of self-reports. | Visible in plain language; must build. |
| Training readiness category | Safety status, experience, time/equipment, and recovery context. | A non-medical planning category such as ready/conservative review/paused; not a physical or medical score. | Visible with explanation; must build. |
| Habit readiness | Time availability, obstacles, confidence, and preferred support. | Selects plan complexity and reminder approach; not a psychological assessment. | Optional user wording; build if time allows. |
| Recovery risk indicator | Recent sleep, energy, fatigue, stress, and training context. | Conservative workload signal only; does not diagnose overtraining or illness. | Visible as guidance, not a numeric score; build if time allows. |
| Equipment flexibility | Environment/equipment range and travel context. | Determines available substitutions; no quality judgement. | Usually internal/explainable; must build. |
| Goal realism indicator | Target/timeline, age/safety context, history, and stated constraints. | Prompts discussion or safety routing; never labels the user as failing. | Visible in supportive language; must build for safety. |
| Safety review status | Deterministic screen result and clearance condition. | Governs what the system may do; not a diagnosis. | Visible; must build. |

## 10. User Stories

| Actor | User story | Critical acceptance criteria |
| --- | --- | --- |
| New user | As a new user, I want a short assessment path so that I can begin without answering irrelevant questions. | Can choose Quick Start; sees only required prompts; can save/resume; receives an honest limited-readiness summary. |
| Returning user | As a returning user, I want to update only what has changed so that my profile remains current without repetition. | Reassessment identifies changed domains; preserves valid answers; produces a new version and review notice. |
| Beginner | As a beginner, I want simple questions and safe starting options so that I can train with confidence. | Beginner branch avoids advanced assumptions and explains next steps. |
| Weight-loss user | As a weight-loss user, I want realistic, respectful goal questions so that guidance supports sustainable progress. | Unsafe timeline/eating-warning rules override normal plan generation; optional context is skippable. |
| Muscle-gain user | As a muscle-gain user, I want the assessment to consider experience, time, and equipment so that my plan is practical. | Branch produces appropriate progression constraints without promising outcomes. |
| Busy student | As a busy student, I want my available time and changing schedule considered so that the plan fits study life. | Short-session branch is available for under-20-minute windows. |
| Football player | As a football player, I want training and match schedules considered so that fitness work complements my sport. | Sport branch captures position/schedule and avoids match-window conflicts. |
| Goalkeeper | As a goalkeeper, I want position-specific priorities considered so that I receive relevant performance support. | Goalkeeper branch captures relevant priorities and applies normal safety limits. |
| Injured user | As a user reporting pain or injury, I want clear safe guidance so that I know when the app cannot personalise normally. | Injury route explains limits, saves progress, and pauses restricted generation when required. |
| User with allergies | As a user with allergies, I want restrictions recorded clearly so that unsuitable food guidance is avoided. | Allergy status is confirmed; nutrition guidance is constrained and never guaranteed allergen-safe. |
| Underage user | As an underage user, I want an age-appropriate route so that the platform does not encourage unsafe goals. | Age safeguards, market policy, and extreme-plan restrictions apply. |
| Admin/reviewer | As an authorised reviewer, I want safety-relevant assessment outcomes auditable so that I can investigate responsibly. | Least-privilege scope, minimum necessary detail, and immutable audit evidence apply. |
| AI Coach | As the AI Coach, I want approved, minimum necessary assessment context so that I can provide relevant, bounded guidance. | Hard safety status cannot be overridden; uncertainty and version are supplied. |
| Workout Generator | As the Workout Generator, I want safe equipment, time, experience, and limitation context so that sessions are practical. | It cannot generate when status is paused and must use current approved constraints. |
| Nutrition Planner | As the Nutrition Planner, I want preferences, restrictions, and goal context so that guidance is relevant and safe. | It respects allergies/restrictions and does not exceed the assessment safety boundary. |

## 11. UI and UX Specification

The competition experience uses a focused, mobile-first, one-question-per-screen approach for consequential or sensitive prompts and short grouped screens for simple, related preferences. A welcome screen explains the value, approximate duration, privacy controls, and Quick Start versus Full Personalization choice. A clear progress indicator shows section title, estimated remaining effort, and that some questions appear only when relevant.

Users can move back, save and exit, resume on a supported device, skip every optional question, and use “I don’t know” where uncertainty is valid. Tooltips explain why height/weight, safety, dietary, and consent questions are requested. Validation is immediate but respectful, states how to fix the issue, and never erases a valid prior answer. Editing an earlier answer explains which later answers may need review.

The interface provides loading and saving state, a recoverable error state with retry, and interrupted/offline-session behaviour that preserves local progress only in a secure, policy-approved manner and reconciles safely when connectivity returns. Before completion, a review screen groups answers, highlights missing optional context and safety constraints, and lets the user edit. The completion screen presents profile readiness, safety status, the next step, and a transparent transition to AI analysis—not a promise of an instant perfect plan.

Accessibility includes semantic labels, keyboard sequence, visible focus, screen-reader announcements for branch changes/errors, contrast, text scaling, reduced motion, touch-target sizing, and plain language. Arabic and English readiness require localised content, appropriate numeric/unit presentation, date/time handling, and right-to-left layout support from the first design review.

## 12. Functional Requirements

| Priority | Requirement |
| --- | --- |
| Critical | The assessment must support draft, save, resume, review, completion, and reassessment states. |
| Critical | Required questions must be validated; optional questions must be skippable without penalty beyond clear readiness limits. |
| Critical | Branches must deterministically update when earlier answers change and must identify dependent answers requiring review. |
| Critical | Every completed assessment must carry a version and preserve the approved historical result. |
| Critical | Safety flags must be deterministic, testable, auditable, and impossible for AI to override. |
| Critical | Sensitive questions must state their purpose; consent must govern optional sensitive/AI/media processing. |
| Critical | Users must be able to edit assessment data and request export/deletion through governed privacy workflows. |
| High | Quick Start must produce a conservative usable profile plus a targeted path to improve confidence. |
| High | Reassessment must trigger after defined material changes or review dates. |
| High | The system must produce versioned outputs mapped to AI, workout, nutrition, dashboard, progress, report, and notification consumers. |
| High | The flow must be usable on mobile, keyboard, screen reader, English, and Arabic/RTL-ready layouts. |
| Medium | The user may compare past assessment summaries and see why a plan was re-evaluated. |
| Medium | Athlete-specific branches may support football and goalkeeper context. |
| Future | Organisation/coach-administered assessments, wearable-prefill, photo-assisted inputs, and adaptive experimentation. |

## 13. Non-Functional Requirements

| Area | Graduation-project requirement |
| --- | --- |
| Performance | Ordinary navigation/validation should respond perceptibly immediately; save/resume status must be clear and failures recoverable. |
| Reliability | Draft saving is resilient to interruption; completion is idempotent; a user never receives two conflicting active results from one completion action. |
| Security and privacy | Authenticated, owner-scoped access is required; sensitive values are minimised, protected, and excluded from ordinary logs/analytics. |
| Accessibility | Core flow meets WCAG 2.2 AA intent, including keyboard, semantic labels, contrast, focus, error handling, and reduced-motion support. |
| Maintainability | Question/rule versions, ownership, decision rationale, and test cases are documented; safety and branching policies are isolated from presentation concerns. |
| Testability | Branches, validations, safety statuses, and output readiness have deterministic inputs and expected results. |
| Localisation | English/Arabic content, RTL readiness, locale-aware units, dates, and timezones are planned before UI implementation. |
| Scalability | High-volume analytics and AI interactions are separated from the core assessment-completion path. |
| Observability | Track completion, error, save, branch, safety, latency, and drop-off signals without raw sensitive content. |
| Auditability | Consent, completed versions, safety outcomes, professional-clearance state, and privileged access are traceable. |

## 14. Analytics and KPIs

Track assessment started, saved, resumed, section completed, optional question skipped, validation error category, branch entered, abandoned, completed, reassessment completed, safety/red-flag triggered, and AI-analysis transition. Measure completion rate, median completion time, resume rate, drop-off by section/branch, optional-data contribution to confidence, red-flag routing rate, and downstream activation after completion.

Analytics may use event type, version, timestamp, anonymous/cohort context, device category, locale, and non-sensitive flow state. They must not capture raw assessment answers, health details, free-text injury descriptions, conversation content, identifiers, passwords, media, or unredacted error payloads. Analytics improves the product by revealing confusing sections, unnecessary questions, validation friction, and whether Quick Start appropriately leads to fuller completion—not by profiling users beyond the stated purpose.

## 15. Edge Cases

| Case | Expected behaviour |
| --- | --- |
| Missing height or weight | Continue where possible; identify reduced confidence and block only features/calculations that genuinely require the value. |
| Impossible numeric value | Explain the allowed range/unit, preserve the user’s input for correction where safe, and prevent completion until required value is valid. |
| Conflicting answers | Ask a neutral clarification and show which plan assumption is affected; never silently choose the more convenient value. |
| Changed goal or injury status | Start a targeted reassessment, invalidate only affected plan context, and apply safety rules immediately. |
| Multiple goals | Require a primary priority; retain secondary goals and explain trade-offs. |
| No equipment / very limited time | Offer viable constrained profile; do not treat it as an error. |
| User does not know | Permit an uncertainty response for valid optional questions; lower confidence rather than fabricate certainty. |
| Interrupted assessment | Preserve approved draft progress, enable safe resume, and avoid duplicate completion. |
| Duplicate submission | Treat repeat completion as idempotent or request explicit revision; never create conflicting active assessment results. |
| Old assessment version | Keep it interpretable, show it is stale/superseded, and use current rule version for new completion. |
| Account deletion/export | Follow verified privacy workflow, disclose retention exceptions, and remove/restrict data according to policy. |
| Underage or unsafe timeline | Apply age/safety route and restrict extreme-plan generation. |
| AI unavailable | Assessment can still complete, show a clear pending state, and never bypass hard safety restrictions. |

## 16. Testing Strategy

Before competition, tests must cover deterministic branching, required-field validation, numeric/unit plausibility, safety-rule precedence, completion/idempotency, save/resume, answer editing/dependent review, assessment versioning, owner/role permission boundaries, and output-readiness mapping. Later integration testing verifies service boundaries without allowing external AI availability to decide safety results.

End-to-end flows must cover Quick Start, Full Personalization, beginner, no-equipment, under-20-minute, weight-loss, allergy, injury/caution, stop/clearance, and reassessment journeys. Accessibility tests cover keyboard-only completion, screen-reader labels/branch announcements, visible focus, contrast, and error recovery. Arabic/RTL tests cover translated content, directionality, numbers/units, dates, and validation layout. Manual competition acceptance includes a timed mobile walkthrough and a deliberate interrupted-session recovery demonstration.

## 17. Security and Privacy Review

Assessment access requires authentication and strict user ownership; organisation, trainer, support, or reviewer access requires an explicit scoped grant and audit trail. Sensitive fields receive stronger access control and are excluded from routine telemetry and error logging. Input is constrained, sanitised, and rate-limited to protect the service and downstream AI context. Consent records are versioned and purpose-specific, while data export/deletion follow verified workflows.

Progress photos require separate opt-in consent, private-by-default visibility, restricted storage references, and deletion controls. Minor-user safeguards apply before personalised use. AI receives the minimum approved context, never raw secrets or unnecessary sensitive prose, and cannot override deterministic safety rules. Privileged reads, safety overrides, consent changes, export/deletion actions, and configuration changes are auditable.

## 18. Competition Scope

| Must Build Before Competition | Build If Time Allows | Post-Competition |
| --- | --- | --- |
| Quick Start and Full Personalization; goal/lifestyle/equipment branching; required safety screening; Injury-Aware caution/stop routing; save/resume; editable answers; assessment summary/readiness; versioned AI-ready output; English/Arabic RTL-ready UX specification; focused automated test coverage. | Football/goalkeeper branch; recovery/habit detail; targeted reassessment notifications; richer review explanation; confidence and recovery indicators; deeper accessibility verification. | Additional sports; coach/organisation assessment workflows; wearable prefill; media/vision inputs; multilingual expansion; advanced adaptive experimentation; clinician integrations; long-term AI memory optimisation. |

The competition demonstration should show one polished complete loop: a user selects a goal, receives relevant branches, reports an injury or constraint safely, saves/resumes, reviews answers, sees explainable readiness, and transitions to a bounded AI-ready profile.

## 19. Definition of Done

Sprint 2.3 is complete when all sections and critical questions have stated purposes; required/optional status, branching, safety, outputs, and priority are documented; user stories with acceptance criteria exist; UX states, edge cases, testing, privacy, and competition scope are defined; the assessment is mapped to future modules; no implementation code was created; and the README links to this blueprint.

## 20. Judge Review

### Evaluation

This is a strong, competition-ready system design because it treats personalisation as a governed feedback loop rather than an AI prompt. It has meaningful technical depth in deterministic safety rules, versioned outputs, adaptive branching, accessibility, privacy, and testability while keeping the first build deliberately narrow.

| Criterion | Assessment |
| --- | --- |
| Originality | Strong: adaptive, safety-aware intake linked to an explainable coaching lifecycle is more substantial than a static fitness quiz. |
| Technical depth | Strong: branching, versioning, consent, output contracts, auditability, and deterministic safety boundaries are explicit. |
| Safety and AI readiness | Strong if hard safety rules are demonstrably independent from AI availability. |
| Personalisation and UX | Strong if Quick Start remains genuinely short and the review/transition is polished. |
| Feasibility | Good only if the team limits athlete scope and avoids vision/wearable/community additions. |
| Documentation quality | Strong: assumptions, restrictions, and future boundaries are explicit. |

**Strengths:** credible product value, clear safety position, reusable structured context, and a demonstrable end-to-end loop.  
**Weaknesses:** self-reported data can be incomplete; safety policy needs market/legal validation; broad sport/nutrition ambitions can dilute the demo.  
**Likely judge questions:** How are red flags tested? What happens when answers change? Why is AI trusted? How is sensitive data protected? What can the competition build actually demonstrate?  
**Recommended improvement:** show a live branch-and-safety test matrix alongside a polished mobile walkthrough, and clearly state that the platform does not diagnose or replace professionals.  
**Score:** 91/100 as a blueprint; a first-place score depends on delivering a narrow, tested, visibly polished implementation later.

## 21. Startup Review

The assessment supports retention because it makes coaching relevant from day one and gives users a reason to revisit when their routine changes. It supports subscription value when the user can see that recommendations, reports, and accountability are based on their own stated context. Its durable differentiation is trusted, explainable, permissioned personalisation—not merely AI-generated text.

Build the core branching, safety, save/resume, profile summary, structured outputs, and reassessment triggers now. Postpone broad sport coverage, wearables, vision, community, coach organisations, and autonomous adaptive plans. Premium candidates include deeper personalisation, advanced reports, sport-specific modules, regulated/validated integrations where appropriate, and human-coach collaboration. Long-term advantage comes from longitudinal, user-controlled context, rigorous safety evaluation, high-quality outcome feedback, and a product experience users can trust with sensitive lifestyle information.
