# RAHFIT AI Competition Demo Script

**Target duration:** 3–5 minutes.
**Core message:** RAHFIT AI uses structured health/readiness data and deterministic safety rules before any AI-assisted capability is considered.

## One-Page Rehearsal Checklist

### Start the stack

~~~powershell
docker compose up --build -d
docker compose ps
docker compose exec -T backend curl -fsS http://localhost:8000/health
~~~

Confirm that mongodb and backend are healthy and health returns {"status":"ok","database":"ok"}.

### Prepare

- App: <http://localhost:8080>
- API docs: <http://localhost:8080/docs>
- Backup references: [README](../README.md), [AI Safety Engine](AI-Safety-Engine.md)
- Use a fresh throwaway account, for example judge-demo-<date>@example.test, with a password of at least 12 characters.
- Keep a prepared account with completed assessment data as a fallback.
- Do not show .env, credentials, tokens, MongoDB records, or AI Coach message sending.

### Final check

~~~powershell
git status --short
docker compose ps
~~~

## 30-Second Introduction

> “RAHFIT AI is a safety-first fitness, nutrition, and health-readiness application. Generic fitness advice can ignore injuries, recovery, dietary constraints, and readiness. RAHFIT AI collects structured, authenticated user information first, then applies deterministic rules to provide safe next steps. It is different because AI is governed by Python-owned policy, context, and safety layers instead of being allowed to give unrestricted health advice.”

## 3–5 Minute Live Demo Script

### 0:00–0:30 — Homepage

**Action:** Open <http://localhost:8080>.

**Say:**

> “This is the React and TypeScript frontend, served by Nginx. It calls FastAPI through the same-origin /api/v1 proxy.”

> “Authentication comes first because every assessment, dashboard, workout, and nutrition record is owner-scoped.”

### 0:30–1:10 — Register and sign in

**Action:** Select **Create an account**, register the throwaway account, and continue to the protected experience.

**Say:**

> “The backend validates the registration request, hashes the password, and creates the account.”

> “After authentication it issues an access token and refresh token. Protected data is served only for the authenticated owner.”

### 1:10–1:30 — Session persistence

**Action:** Refresh the authenticated page.

**Say:**

> “The refresh flow restores the session after a browser reload. The backend still validates token type, expiry, signature, and token version.”

### 1:30–2:30 — Dashboard

**Action:** Show /app. For a new account, show the next action and prerequisite state. For a prepared account, show assessment, workout, and nutrition data.

**Say:**

> “The dashboard aggregates assessment state, readiness, workout state, nutrition state, safety notices, and one explainable next action.”

> “For a new user, the correct next action is assessment. The system does not invent a plan before it has enough approved information.”

> “For a prepared user, the server owns the readiness and safety decision; the frontend presents the resulting state.”

**Action:** Point to health, recovery, goals, analytics, timeline, and AI-insight widgets only when visible.

**Say:**

> “These areas are dashboard widgets with loading and empty states. I only call a metric live when it is supported by current API data.”

> “That is deliberate: the product does not fabricate health or progress metrics.”

### 2:30–3:15 — Workout and nutrition boundaries

**Action:** Open assessment, intelligent workout setup, workout, or nutrition from a dashboard action.

**Say:**

> “Assessment and health declarations feed readiness. Workout generation is deterministic and constrained by goals, equipment, and safety rules.”

> “Nutrition uses deterministic calculations and safety constraints. An optional provider cannot override the validated workout or nutrition engine.”

### 3:15–3:40 — AI Coach, accurately scoped

**Action:** Optionally open /ai-coach to show availability and conversation UI. Do not send a message.

**Say:**

> “The AI Coach foundation includes availability and owner-isolated conversation lifecycle.”

> “Public message sending and listing are intentionally unregistered. The classifier, policy, context, and safety layers exist, but we will not expose an incomplete public generation route.”

> “That is a deliberate safety decision.”

### 3:40–4:15 — Logout and route protection

**Action:** Log out, then open <http://localhost:8080/app>.

**Say:**

> “Logout clears the client session and invalidates the server token version.”

> “The protected route returns the user to sign-in. The browser route guard improves the experience, and the backend independently requires a valid bearer token.”

### 4:15–4:40 — Close

**Say:**

> “This is a runnable vertical slice: secure authentication, owner-isolated data, readiness-aware dashboard decisions, deterministic workout and nutrition logic, and a governed AI architecture.”

> “The next step is a bounded public AI Coach message contract with fallbacks and end-to-end safety tests.”

## Judge-Friendly Technical Architecture

> “React and TypeScript run in the browser. Nginx serves the app and proxies /api/v1 requests. FastAPI owns typed APIs, validation, authentication, services, and structured logs. MongoDB stores owner-scoped documents and indexes. JWT identifies the user. Python owns the AI classifier, policy, approved context, and safety layers, so an external model is never the final authority. Docker Compose runs MongoDB, FastAPI, and Nginx/React together.”

| Implemented | Partially implemented | Planned |
| --- | --- | --- |
| Authentication, assessment/readiness, dashboard, deterministic workout/nutrition flows, MongoDB persistence/indexes, Docker, and core tests. | AI Coach UI, availability, and conversation lifecycle. Public message sending/listing is intentionally unregistered. Some dashboard widgets may correctly show staged/empty states. | Bounded public AI messaging, streaming, feedback, telemetry, reports, notifications, wearables, payments, and enterprise controls. |

## Backup Plan

### If Docker is slow

Say:

> “The stack is three services: MongoDB, FastAPI, and Nginx/React. While the first build completes, I can show the README quick start, architecture, and generated API documentation.”

Show docker compose ps, then [README Quick Start](../README.md#quick-start-with-docker). Do not claim readiness until services are healthy.

### If the internet is unavailable

Say:

> “The core password registration, dashboard, workout, nutrition, and safety flows are local to Docker. Google sign-in and optional external-provider behavior are not required for this demo.”

Use password registration; do not attempt Google sign-in or provider generation.

### If one page fails

1. Return to the homepage and demonstrate authentication and protected routing.
2. Open <http://localhost:8080/docs> and show the typed API contract.
3. Show [README](../README.md) or [Architecture](Architecture.md).
4. Use a prepared screenshot only if it is clearly labelled as a successful earlier local run.

Say:

> “I will not hide the failure. The core stack is health-checked and the API contract is visible. I will continue with the verified flow rather than improvising unsupported behavior.”

### If the dashboard has no populated data

Say:

> “This is the correct new-user state. RAHFIT AI blocks plan assumptions until assessment and readiness information are available. I can continue through assessment or use the prepared account for populated data.”
