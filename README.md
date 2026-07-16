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

The [AI Provider Infrastructure](docs/AI-Provider-Infrastructure.md) documents the provider-neutral contract, safe configuration, availability states, error mapping, and test-only fake provider.

The [AI Conversation Domain](docs/AI-Conversation-Domain.md) documents owner-isolated conversation persistence, lifecycle rules, trusted internal messages, bounded retention, and migration-safe indexes.

The [Approved AI Context Builder](docs/AI-Context-Builder.md) documents purpose-minimized, owner-isolated, size-bounded context selection for future AI Coach safety and orchestration stages.

The [AI Policy Layer](docs/AI-Policy-Layer.md) documents deterministic capability permissions, forbidden actions, professional-guidance decisions, and stable reason codes.

## Quality checks

```powershell
ruff check backend
black --check backend
mypy backend/app
pytest

Set-Location frontend
npm run lint
npm run format:check
npm run build
```

Install local hooks with `pre-commit install` after installing the Python development dependencies.
