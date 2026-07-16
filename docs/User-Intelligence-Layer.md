# RAHFIT AI — User Intelligence Layer

**Status:** Implemented foundation

**Scope:** Canonical user profile, separate health profile, deterministic readiness validation, minimum-necessary AI context projection, MongoDB persistence, and tests. No public profile endpoint, authentication change, AI provider change, Safety Engine change, or frontend implementation is included.

## 1. Purpose

The User Intelligence Layer is the canonical source for user facts consumed by future AI decisions. Authentication remains responsible only for identity and access. Assessment remains an intake workflow. Workout and nutrition remain execution domains. The intelligence layer owns the current validated profile and health declarations produced by those workflows or future profile interfaces.

The dependency direction is:

```text
Profile/health input workflow
        ↓
ProfileService / HealthProfileService
        ↓
user_profiles / health_profiles
        ↓
UserIntelligenceService
        ↓
ReadinessChecker
        ↓
UserIntelligenceContextBuilder
        ↓
AIService → Safety Engine → AI Provider
```

No provider SDK, prompt logic, authentication logic, or generated business plan exists in this layer.

## 2. Module Responsibilities

| Module | Responsibility |
| --- | --- |
| `app/profile` | Strict canonical profile models, computed BMI/BMR/age group, owner-scoped persistence, and profile service |
| `app/health` | Separate sensitive health declaration models, computed clearance flags, owner-scoped persistence, and health service |
| `app/users` | Single read boundary that combines the owned profile and health profile into one intelligence snapshot |
| `app/readiness` | Deterministic completeness, consistency, plausibility, and safety-related readiness checks |
| `app/context` | Minimum-necessary projection from a ready intelligence snapshot into the existing `AIApprovedContext` contract |

## 3. Canonical User Profile

The user profile is divided into cohesive sections:

- Identity: full name, age, gender option, and ISO alpha-2 country code.
- Body: height, weight, and optional body-fat percentage.
- Goals: primary goal, optional secondary goal, and optional paired target weight/date.
- Training: experience, available days, session duration, equipment, and workout location.
- Lifestyle: sleep, stress, activity level, and daily water intake in milliliters.
- Nutrition: dietary preferences, allergies, and normalized dietary restrictions.

The model rejects unknown fields, numeric string coercion, invalid ranges, duplicated equipment/restrictions, identical primary and secondary goals, and incomplete target weight/date pairs.

### Computed fields

- BMI uses `weight_kg / height_m²` and is rounded to two decimal places.
- BMR uses the Mifflin–St Jeor estimate and is rounded to whole kilocalories.
- Age group is classified as adolescent, young adult, middle adult, or older adult.

BMR is an estimate, not a diagnosis or prescription. For non-binary or undisclosed gender options, the implementation uses the midpoint of the two traditional formula adjustments to avoid asserting a sex-specific coefficient. Future clinical-grade personalization should collect an explicit metabolic-formula input with informed user consent.

## 4. Health Profile

Health data is stored separately from authentication and the general profile. It contains explicit structured records for:

- injuries
- chronic conditions
- pain areas and intensity
- mobility limitations
- surgery history and clearance
- optional private notes

Empty tuples mean that the user explicitly confirmed no records for that category. Absence of the entire health profile means the information is incomplete.

Computed health fields identify active injury areas and whether medical clearance is required. Future provider context never includes free-text health notes, surgery descriptions, or chronic-condition names by default.

## 5. Persistence

| Collection | Ownership | Index |
| --- | --- | --- |
| `user_profiles` | one document per `user_id` | unique `user_profiles_user_unique` |
| `health_profiles` | one document per `user_id` | unique `health_profiles_user_unique` |

Repositories use owner-scoped reads and atomic upserts. `created_at` is immutable after insertion, while `updated_at` and schema versions change with each save. Computed values are not persisted; they are recalculated from canonical inputs to prevent drift.

Target and surgery dates are persisted as ISO dates and validated when reconstructed. Password hashes, tokens, and provider credentials never enter either collection.

## 6. Readiness Checker

The Readiness Checker is deterministic and performs no I/O or AI calls. It returns:

- status: `ready`, `caution`, `needs_information`, or `blocked`
- `ready_for_ai`
- completeness score from 0 to 100
- stable missing field paths
- structured issues with stable codes, severity, field path, message, and professional-guidance flag

### Validation categories

Required information:

- every required profile group
- explicit health declarations
- paired target weight and target date

Cross-field consistency:

- fat-loss targets must be below current weight
- muscle-gain targets must be above current weight
- target dates must be future dates
- requested weight-change rates must remain within conservative deterministic thresholds

Dangerous combinations:

- extreme BMI or body-fat values
- very low sleep combined with high stress and very high activity
- severe active injury
- uncontrolled or uncleared chronic condition
- severe pain
- recent uncleared surgery
- advanced programming for a young user
- seven-day availability without planned recovery
- unusually low reported hydration

Critical or error findings block AI readiness. Missing data produces `needs_information`. Warning-only results permit `caution` so downstream safety can apply conservative limits.

## 7. Minimum-Approved AI Context

`UserIntelligenceContextBuilder` implements the existing context-builder method contract and can be injected into `AIService`. It first loads an owner-scoped intelligence snapshot and runs Readiness Checker. A blocked or incomplete snapshot never reaches provider context construction.

Every allowed context contains:

- deterministic safety/readiness facts
- normalized current request

Additional sections are purpose-limited:

- workout purposes receive training constraints and active injury/mobility areas
- nutrition purposes receive required measurements, BMR estimate, lifestyle factors, allergies, and dietary restrictions
- explanation and motivation purposes receive only the required derived profile and goal facts
- alternative requests omit profile and goal sections when the existing Safety Engine does not approve them

The context explicitly excludes:

- full name
- email
- country
- password hash and tokens
- health notes
- surgery descriptions
- chronic-condition names
- provider credentials
- unrelated workout or nutrition data
- conversation history

The output uses the existing bounded `AIApprovedContext` model, records inclusion/omission reasons, and enforces the existing serialized-size ceiling.

## 8. Security and Privacy

- Authentication identity and sensitive health data remain separate collections.
- Every repository query uses authenticated `user_id` ownership.
- Services verify repository ownership invariants before returning data.
- Unknown fields are forbidden at domain boundaries.
- Free-text fields are bounded and normalized.
- Provider context follows purpose limitation and data minimization.
- Computed readiness uses deterministic rules and cannot be overridden by a provider.
- No context is logged or persisted by the Context Builder.
- No API key, token, password hash, or raw authentication model is accepted by this layer.
- Health data should use encrypted transport, encrypted storage, least-privilege database credentials, and audited administrative access in deployment.

## 9. Data Flow

1. An authenticated intake workflow validates `UserProfileData` and `HealthProfileData`.
2. Profile and health services save owner-scoped canonical documents.
3. `UserIntelligenceService` loads both documents for one authenticated owner.
4. Readiness Checker calculates completeness and deterministic issues.
5. A blocked or incomplete snapshot stops before AI context construction.
6. Context Builder selects only sections required for the requested purpose.
7. `AIService` sends that context through the existing Safety Engine before any provider call.
8. The provider receives only Safety-approved context sections.

## 10. Testing

Tests cover:

- strict numeric validation and impossible ranges
- normalization and duplicate rejection
- BMI, BMR, age group, active injury, and clearance computations
- required health declarations
- owner-scoped MongoDB upserts and ISO date persistence
- unique owner indexes
- missing profile and health data
- goal/target incompatibility
- dangerous health and recovery combinations
- owner-scoped intelligence aggregation
- workout and nutrition context minimization
- exclusion of identity, authentication, and private health details
- context size bounds
- readiness stop before context construction
- compatibility with the existing deterministic Safety Engine

## 11. Migration and Adoption

Startup creates the two new unique owner indexes. No existing collection is modified.

Existing users do not automatically receive canonical profiles. Before this layer becomes mandatory in a public generation flow, the project must choose one controlled adoption path:

1. map completed Assessment results into reviewed profile/health drafts and require user confirmation, or
2. require users to complete a dedicated profile and health intake workflow.

Until that adoption occurs, missing canonical documents correctly return `needs_information` and block AI context construction. Automatic unreviewed migration of sensitive health answers is intentionally not implemented.

## 12. Deferred Scope

- public profile and health endpoints
- frontend profile forms
- Assessment-to-profile migration workflow
- consent/version history
- field-level encryption key management
- administrative health-data access
- audit events for profile reads and writes
- localized validation messages
- profile revision history
- integration into a public Gemini generation endpoint
