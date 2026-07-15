# RAHFIT AI

Engineering foundation for an AI-powered health, fitness, and nutrition SaaS platform. This repository intentionally contains **no product features, authentication endpoints, AI implementation, or fitness/nutrition logic**. It establishes the standards and cross-cutting infrastructure required to build those safely.

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

See [Setup Guide](docs/Setup-Guide.md) for details, [Architecture](docs/Architecture.md) for boundaries and extension points, the [Product Blueprint](docs/Product-Blueprint.md) for the approved product specification before feature implementation, the [Smart Assessment Blueprint](docs/Smart-Assessment-Blueprint.md) for the approved adaptive-assessment specification, the [AI Architecture Blueprint](docs/AI-Architecture-Blueprint.md) for the approved hybrid AI design, the [API Blueprint](docs/API-Blueprint.md) for the approved REST interface contract, the [Enterprise Domain Blueprint](docs/Enterprise-Domain-Blueprint.md) for the approved business-domain model, the [UI/UX Blueprint](docs/UI-UX-Blueprint.md) for the approved product experience and interface architecture, and the [Implementation Plan](docs/Implementation-Plan.md) for the approved development roadmap.

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
