# RAHFIT AI — Assessment Frontend Architecture

**Sprint:** 3.2.3  
**Status:** Implemented  
**Scope:** Authenticated Smart Assessment frontend only.

## 1. Experience Flow

The assessment is a protected, mobile-first journey with five explicit experience states:

1. **Welcome** explains adaptive behavior, safety, privacy, and save/resume before the first question.
2. **Resume** restores an unfinished session with its server-provided completion, readiness, and safety state.
3. **Wizard** presents one backend-selected question at a time and saves before advancing.
4. **Review** displays server-owned progress, risk, missing categories, safety state, and every saved answer with edit navigation.
5. **Completed** presents the deterministic backend summary and routes to the existing dashboard placeholder.

Visiting the welcome route starts or recovers the user's single active assessment. A session with saved answers is redirected to the Resume experience. A new session remains on Welcome until the user explicitly begins.

## 2. Source of Truth and State

`AssessmentProvider` owns only API orchestration and presentation state:

- Versioned question catalogue.
- Current assessment session.
- Current completed result.
- Loading and saving state.
- Normalized API error code, message, and field reference.

The frontend never evaluates visibility rules, safety rules, risk, readiness, missing categories, or completion eligibility. It renders `next_question`, `progress`, and result data returned by the backend. Editing an answer submits it to the same backend endpoint; the updated session determines which answer remains valid and which question comes next.

API payloads are mapped from snake_case transport contracts to typed camelCase view models at the service boundary. This keeps components independent of transport naming without changing the backend contract.

## 3. Routing

All assessment routes are protected by the existing authentication boundary and share one persistent provider and layout.

| Route                                                 | Responsibility                                                     |
| ----------------------------------------------------- | ------------------------------------------------------------------ |
| `/assessment`                                         | Welcome and automatic unfinished-session discovery.                |
| `/assessment/resume/:sessionId`                       | Resume confirmation and saved progress.                            |
| `/assessment/session/:sessionId`                      | Current server-selected question.                                  |
| `/assessment/session/:sessionId/question/:questionId` | Edit a question that exists in the server-returned answer history. |
| `/assessment/session/:sessionId/review`               | Pre-completion review and completion command.                      |
| `/assessment/completed/:sessionId`                    | Completed deterministic result.                                    |
| `/app`                                                | Existing dashboard placeholder used by the final call to action.   |

Assessment pages are lazy-loaded into separate production chunks. Direct navigation reloads the owned session or latest completed result through authenticated APIs.

## 4. Component Architecture

| Component                  | Responsibility                                                                            |
| -------------------------- | ----------------------------------------------------------------------------------------- |
| `AssessmentLayout`         | Shared brand, theme, locale, logout, responsive shell, and route outlet.                  |
| `AssessmentProgressHeader` | Server-provided completeness, readiness, category, and question position.                 |
| `AssessmentQuestionField`  | Generic accessible rendering for every backend question type.                             |
| `SafetyStatusCard`         | `SAFE`, `CAUTION`, and `STOP` presentation with risk and explanations.                    |
| Design-system primitives   | Buttons, inputs, textarea, select, radio, checkbox, cards, badges, loading, and progress. |

The question renderer supports text, textarea, number, integer, boolean, single choice, multiple choice, date, height, weight, time, and slider inputs. Long single-choice lists use a select; shorter lists use radio cards; multiple-choice uses checkboxes. Height and weight use numeric controls with the backend-provided unit and bounds.

Components contain presentation behavior only. No component embeds assessment branching, risk, safety, readiness, or profile business rules.

## 5. Validation and Saving

Required controls must contain a local value before the Save and Continue action is enabled. Native input attributes expose numeric bounds, date/time controls, and input modes, but the backend remains authoritative.

Every advancing action sends one answer to the backend. A successful response replaces the local session and navigates to its `next_question` or Review. Backend field errors render inline through `aria-invalid`, `aria-describedby`, and an alert message. Network or non-field errors render in a safe page-level alert. Saving state disables controls and is announced through an ARIA live region.

`STOP` disables completion in Review, and the backend still enforces the restriction if a stale client attempts completion.

## 6. Accessibility

- Semantic headings, landmarks, fieldsets, legends, labels, lists, and definition lists.
- Keyboard-operable inputs, choices, navigation, edit actions, theme, locale, and logout.
- Focus moves to the question heading when the server-selected question changes.
- Progress uses native progress semantics and accessible values.
- Field errors are associated with their control and announced.
- Safety `STOP` uses an alert; non-blocking safety states use status semantics.
- Minimum touch targets, visible focus rings, and WCAG AA semantic colors.
- Reduced-motion media queries remove non-essential animation and transitions.
- Screen-reader text preserves requiredness, current progress, saving state, and action purpose.

## 7. Localization and Direction

The experience supports English LTR and Arabic RTL. Locale changes update the document language and direction and persist locally. Layout uses logical CSS properties, while directional icons are mirrored under RTL.

All current version-one question titles and options have Arabic presentation translations keyed by stable backend question identifiers. Unknown future questions safely fall back to backend text. Category, safety, risk, progress, review, and completed-summary presentation are localized independently of branching behavior.

## 8. Responsive and Visual System

The experience reuses the existing semantic tokens for color, spacing, typography, radius, shadow, focus, motion, light mode, and dark mode. Desktop and ultra-wide layouts use bounded content widths and two-column context panels. Tablet collapses context below or above the primary task. Phone layouts use one column, full-width actions, large controls, and reduced decorative scale.

The visual language is calm and health-oriented: generous whitespace, soft borders and shadows, low-saturation semantic surfaces, rounded cards, and restrained motion. No gaming patterns, fake metrics, or placeholder assessment content are used.

## 9. Performance

- Route-level lazy loading creates independent chunks for Welcome, Resume, Wizard, Review, and Completed.
- The generic question renderer is memoized.
- Context commands are stable callbacks and the context value is memoized.
- The backend sends one next question, avoiding client-side catalogue scans for branching.
- Session data replaces local state atomically after each save, avoiding competing answer stores.

## 10. Testing

Automated tests cover required-answer validation, save-before-navigation, previous navigation, progress semantics, control variants, resume state, all safety presentations, review, completion, and dashboard-placeholder navigation. The build, lint, formatting, and test suites are required gates for the sprint.

## 11. Known Boundaries

- The backend does not currently expose an explicit skip representation for optional boolean, numeric, or single-choice questions; those controls require an explicit selection when presented.
- Arabic translations cover the current versioned catalogue. A future catalogue publishing workflow should deliver localized content from the backend.
- The Dashboard destination remains the existing placeholder, as required by Sprint 3.2.3 scope.
- No frontend logic is allowed to override backend safety, risk, readiness, or branching decisions.
