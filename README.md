# RAHFIT AI

Engineering foundation and production vertical slices for an AI-powered health, fitness, and nutrition SaaS platform. Authentication, Smart Assessment, Intelligent Dashboard, and deterministic workout and nutrition engines are implemented. Provider-neutral AI infrastructure is available; AI Coach product features remain deferred.

## Repository layout

```
.
├── backend/                 # FastAPI service
├── frontend/                # React + TypeScript client
├── docs/                    # Architecture and setup documentation
├── .github/workflows/       # Continuous integration
├── .env.example             # Required environment variables
└── pyproject.toml           # Python quality-tool configuration
```

## Quick start

1. Copy `.env.example` to `.env` and set a real `JWT_SECRET_KEY`.
2. Start MongoDB locally.
3. Create a Python 3.12 virtual environment, install `backend/requirements-dev.txt`, then run `uvicorn app.main:app --app-dir backend --reload`.
4. In `frontend`, run `npm install`, then `npm run dev`.

See [Setup Guide](docs/Setup-Guide.md) for details, [Architecture](docs/Architecture.md) for boundaries and extension points, the [Dashboard Architecture](docs/Dashboard-Architecture.md) for the Intelligent Dashboard aggregation and UX contract, the [Workout Architecture](docs/Workout-Architecture.md) for deterministic plan generation and session execution, the [Product Blueprint](docs/Product-Blueprint.md) for the approved product specification before feature implementation, the [Smart Assessment Blueprint](docs/Smart-Assessment-Blueprint.md) for the approved adaptive-assessment specification, the [AI Architecture Blueprint](docs/AI-Architecture-Blueprint.md) for the approved hybrid AI design, the [API Blueprint](docs/API-Blueprint.md) for the approved REST interface contract, the [Enterprise Domain Blueprint](docs/Enterprise-Domain-Blueprint.md) for the approved business-domain model, the [UI/UX Blueprint](docs/UI-UX-Blueprint.md) for the approved product experience and interface architecture, and the [Implementation Plan](docs/Implementation-Plan.md) for the approved development roadmap.

The [Nutrition Architecture](docs/Nutrition-Architecture.md) documents deterministic nutrition calculations, food safety rules, meal generation, and daily progress tracking.

The [AI Provider Infrastructure](docs/AI-Provider-Infrastructure.md) documents the AIService boundary, provider pattern, Gemini and Mock adapters, structured output validation, safe configuration, and future provider extension process.

The [AI Conversation Domain](docs/AI-Conversation-Domain.md) documents owner-isolated conversation persistence, lifecycle rules, trusted internal messages, bounded retention, and migration-safe indexes.

The [Approved AI Context Builder](docs/AI-Context-Builder.md) documents purpose-minimized, owner-isolated, size-bounded context selection for future AI Coach safety and orchestration stages.

The [AI Policy Layer](docs/AI-Policy-Layer.md) documents deterministic capability permissions, forbidden actions, professional-guidance decisions, and stable reason codes.

The [AI Capability Classifier](docs/AI-Capability-Classifier.md) documents deterministic English, Arabic, and mixed-language intent classification, priority rules, confidence metadata, and safe unsupported routing.

The [Deterministic AI Safety Engine](docs/AI-Safety-Engine.md) documents fail-closed pre-generation decisions, safety precedence, policy and context integration, provider eligibility, and privacy-preserving findings.

The [AI Architecture Gate Review](docs/AI-Architecture-Gate-Review.md) evaluates end-to-end readiness before provider generation and defines the required compatibility, validation, idempotency, persistence, cost-control, and testing gates.

The [User Intelligence Layer](docs/User-Intelligence-Layer.md) defines the canonical profile and health domains, deterministic readiness validation, minimum-approved AI context projection, persistence, privacy boundaries, and adoption migration.

The [Workout Engine](docs/Workout-Engine.md) defines the versioned Python exercise catalog, readiness-gated deterministic planning, owner-scoped plan and session persistence, strict validation, progress records, and auditable adaptation recommendations. Gemini is optional and may only explain an already-valid plan through `AIService`; disabled, timed-out, rate-limited, malformed, or unsafe provider output uses the deterministic fallback without requiring a Gemini key. Its authenticated, versioned API is available at `/api/v1/intelligent-workouts`; the legacy `/api/v1/workouts` contract remains compatible.

The [Intelligent Workout API Contract](docs/Intelligent-Workout-API-Contract.md) is the frontend-facing source for stable operation IDs, authenticated setup, request/response types, error handling, lifecycle rules, and the repeatable HTTP smoke-test workflow.

## Quality checks

```powershell
ruff check backend
black --check backend
mypy backend/app
pytest

# Focused Workout Engine verification
pytest backend/tests/test_intelligent_workout_engine.py -q
pytest backend/tests/test_intelligent_workout_api.py -q
pytest backend/tests/test_intelligent_workout_openapi.py -q
pytest backend/tests/test_intelligent_workout_http_smoke.py -q

Set-Location frontend
npm run lint
npm run format:check
npm run build
```

Install local hooks with `pre-commit install` after installing the Python development dependencies.
