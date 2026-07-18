# RAHFIT AI

RAHFIT AI is a safety-first fitness, nutrition, and health-readiness web application. It turns an authenticated user's assessment, profile, and health constraints into explainable dashboard guidance and deterministic workout and nutrition experiences.

The competition build focuses on a reliable vertical slice: register, sign in, complete the readiness journey, view a personalized dashboard, and use protected fitness features without exposing health decisions to an unbounded AI system.

## Quick Start with Docker

Requirements: Docker Desktop running and a `.env` file with a non-placeholder `JWT_SECRET_KEY` of at least 32 characters.

```powershell
Copy-Item .env.example .env
# Edit .env and set JWT_SECRET_KEY to a long random value.

docker compose up --build -d
docker compose ps
```

Wait until `mongodb` and `backend` report `healthy`, then open:

- Frontend: <http://localhost:8080>
- Same-origin API base: <http://localhost:8080/api/v1>
- API documentation through Nginx: <http://localhost:8080/docs>

The Compose file does **not** publish backend port `8000` to the host. These backend URLs are available inside the Compose network, not directly from the browser host:

- Backend health: <http://localhost:8000/health>
- Backend API docs: <http://localhost:8000/docs>

Use this PowerShell command to verify health from the running backend container:

```powershell
docker compose exec -T backend curl -fsS http://localhost:8000/health
```

Expected response:

```json
{"status":"ok","database":"ok"}
```

Stop the local stack when finished:

```powershell
docker compose down
```

## Five-Minute Judge Demo

1. Open <http://localhost:8080>.
2. Register a new account with an email and a password of at least 12 characters.
3. Continue to the authenticated dashboard and review its personalized next action and feature states.
4. Refresh the browser; the refresh-token flow restores the session.
5. Navigate through assessment, workout, or nutrition from the dashboard as appropriate for the account state.
6. Do not use AI Coach message sending as a demo feature: its conversation storage/availability foundation exists, but its public messages route is intentionally unregistered.
7. Log out, then visit <http://localhost:8080/app>; the protected route returns the user to sign-in.

## What RAHFIT AI Solves

Generic fitness advice can ignore readiness, injury declarations, dietary preferences, and recovery constraints. RAHFIT AI provides a structured, owner-isolated flow that gathers this information, applies deterministic rules, and presents safe next steps instead of treating health or fitness guidance as an unrestricted chatbot problem.

## Implemented Features

- Password authentication, JWT access/refresh flow, Google ID-token integration, and session revocation.
- Owner-isolated MongoDB persistence for users, assessments, workout plans/sessions, nutrition plans/logs, dashboards, and AI conversation records.
- Adaptive assessment, health/profile readiness checks, safety states, and dashboard aggregation.
- Deterministic workout generation, session recording, recovery-aware adaptation recommendations, and nutrition targets/logging.
- React dashboard, protected routes, loading/empty/error states, Arabic/English locale support, responsive layouts, and typed API services.
- Provider-neutral AI infrastructure: classifier, policy layer, safety engine, minimum-necessary context builder, availability state, and guarded provider adapters.

## Current Scope and Limitations

| Status | Scope |
| --- | --- |
| Fully implemented | Authentication, assessment/readiness, dashboard, deterministic workout and nutrition flows, owner isolation, API validation, MongoDB indexes, Docker deployment, and core test coverage. |
| Partially implemented | AI Coach UI and conversation lifecycle/availability foundations. Conversation creation, listing, reading, closing, and deletion are available; public message sending/listing is intentionally not registered. Some dashboard widgets are present as staged UI work and may show explicit empty states until corresponding API data is available. |
| Planned | A bounded public AI Coach message flow, streaming, feedback, usage/cost telemetry, reports, notifications, wearable integrations, payments, and enterprise administration. |

## Technology Stack

- Backend: Python 3.12, FastAPI, Pydantic Settings, Motor/PyMongo, MongoDB, PyJWT, pwdlib, Structlog.
- Frontend: React 19, TypeScript, Vite, React Router, Vitest, Testing Library, Tailwind/Vite styling, Framer Motion.
- Delivery: Docker Compose, Nginx, GitHub Actions, Ruff, Black, mypy, ESLint, Prettier.

## Architecture Overview

The backend uses controller -> service -> repository boundaries. Controllers expose versioned HTTP contracts; services own domain rules and ownership checks; repositories isolate MongoDB access; Pydantic models/schemas define persistence and transport boundaries. The frontend uses route-level React pages, providers for authentication/theme/locale state, and typed services that call the same-origin `/api/v1` proxy.

Startup creates the required MongoDB indexes and assessment catalogue. The Nginx frontend proxies `/api/`, `/docs`, and `/openapi.json` to the backend while serving the React single-page application.

For deeper design detail, see [Architecture](docs/Architecture.md), [Setup Guide](docs/Setup-Guide.md), [Dashboard Architecture](docs/Dashboard-Architecture.md), [Workout Architecture](docs/Workout-Architecture.md), [Nutrition Architecture](docs/Nutrition-Architecture.md), and the [Competition Evaluator Guide](COMPETITION.md).

## Local Development

Prerequisites: Python 3.12, Node.js 22, npm, MongoDB 7+, and a configured `.env` copied from `.env.example`.

Backend, from the repository root:

```powershell
py -3.12 -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements-dev.txt
uvicorn app.main:app --app-dir backend --reload
```

Frontend, in a second PowerShell window:

```powershell
Set-Location frontend
npm ci
npm run dev
```

The Vite development app uses <http://localhost:5173>; its default API base is <http://127.0.0.1:8000/api/v1>.

## Release Checks

From the repository root, with backend development dependencies installed:

```powershell
ruff check backend
black --check backend
mypy backend/app
pytest
```

Frontend checks:

```powershell
Set-Location frontend
npm run lint
npm run format:check
npm run test -- --run
.\node_modules\.bin\tsc.cmd --noEmit -p tsconfig.app.json
npm run build
```

## Security and AI Safety Highlights

- Validated environment settings, secret-aware fields, JWT expiry/type/version checks, password hashing, reset-token hashing, and token-version revocation.
- Owner-scoped repository queries, validated request schemas, NoSQL operator rejection, CORS allowlisting, security headers, and baseline rate limiting.
- AI requests are constrained by deterministic capability classification, policy allowlists, safety evaluation, readiness/context checks, provider availability checks, and minimal context projection. AI does not diagnose, prescribe medication, override safety rules, expose secrets, or bypass deterministic workout/nutrition engines.

## Repository Structure

```text
.
├── backend/                 FastAPI application, domain services, repositories, tests
├── frontend/                React/Vite client, typed API services, component tests
├── docs/                    Architecture, API, setup, and domain documentation
├── .github/workflows/       Continuous-integration workflow
├── docker-compose.yml       MongoDB, backend, and Nginx frontend services
├── .env.example             Required environment-variable template
├── COMPETITION.md           Evaluator-oriented competition guide
└── pyproject.toml           Python quality-tool configuration
```

## Competition Status

The repository is ready for the core live competition demonstration when started through Docker Compose: the running stack provides registration, login, session refresh, protected dashboard access, logout, and health checks. The AI Coach public message endpoint remains a deliberately deferred capability and should not be presented as complete.
