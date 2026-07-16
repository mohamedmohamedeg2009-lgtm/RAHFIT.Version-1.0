# Setup Guide

## Prerequisites

- Python 3.12 (canonical; CI and tooling target this exact minor version)
- Node.js 22+
- MongoDB 7+
- Git

## Environment

Copy the root example, then set non-development secrets through your deployment platform:

```powershell
Copy-Item .env.example .env
```

`JWT_SECRET_KEY` must be at least 32 characters. Do not reuse the example secret in any shared or deployed environment. `ALLOWED_ORIGINS` accepts comma-separated browser origins.

## Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements-dev.txt
uvicorn app.main:app --app-dir backend --reload
```

The service has no public business endpoints in Phase 1. A running MongoDB is required because startup validates connectivity.

## Frontend

```powershell
Set-Location frontend
npm install
npm run dev
```

## Local quality gate

Run the commands listed in the README before opening a pull request. CI enforces formatting, static analysis, tests, linting, and a production frontend build.
