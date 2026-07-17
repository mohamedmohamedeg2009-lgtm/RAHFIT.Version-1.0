# RAHFIT AI — Competition Evaluator Guide

## Project Problem
Typical fitness applications either provide generic, non-individualized templates that ignore injury risk, or rely entirely on unconstrained AI models that hallucinate unsafe exercises, contradict medical conditions, and expose host platforms to liability.

## Solution
RAHFIT AI combines a secure, Clean/Hexagonal FastAPI backend with a React SPA to deliver a hybrid, safety-first training assistant. Exercise selection, clinical safety rules, and progression boundaries are run deterministically in Python. Large Language Models (LLMs) are strictly restricted to explaining plans already generated and validated by the backend.

---

## Strongest Differentiators

### 1. Python-Owned Deterministic Safety
All training decisions are governed by clean-room code:
- **Readiness check**: Validates sleep, stress, and previous session outcomes.
- **Medical clearance gates**: Automatically pauses training or requires professional medical clearance if high-risk flags (e.g. chest pain, active injuries) are declared.
- **Strict exercise exclusions**: Excludes movements that stress declared pain areas (e.g. squats are blocked if active knee pain is declared).

### 2. Provider-Neutral AI Isolation
AI interactions are strictly quarantined:
- LLM outputs are structured, validated against a Pydantic schema, and fail-closed.
- If the AI provider (Gemini or OpenAI compatible) is offline, rate-limited, or returns malformed/unsafe content, the system transparently applies a fully validated deterministic fallback plan.
- The AI can never modify exercise prescriptions directly; its role is limited to natural language explanation.

---

## Intelligent Workout Journey
1. **Setup & Onboarding**: The user completes a comprehensive Training Profile and an explicit Health Declaration.
2. **Deterministic Validation**: The backend checks rules. If clear, a training cycle is initialized.
3. **Plan Generation**: The system builds an 8-week cycle. If AI is enabled and safe, an explanation is appended.
4. **Session Recording**: The user tracks set-by-set load, reps, RPE, and records pain occurrences.
5. **Outcome Evaluation**: The backend calculates completion percentage and adaptation flags (e.g. deload required).

---

## System Architecture Summary
- **Backend**: FastAPI, Clean Architecture (Controllers, Services, Repositories), MongoDB (via Motor).
- **Frontend**: React, Vite, Vanilla CSS, TypeScript.
- **AI Safety Engine**: Intercepts requests, evaluates capability permissions, filters prompt context, and post-validates provider output.

---

## How AI is Restricted
- **Zero Direct Mutation**: AI cannot edit exercises, sets, or reps.
- **Context Sandboxing**: Prompt builders restrict LLM context strictly to public information and authorized profile attributes.
- **Safety Engine Interceptor**: Pre-generation policies check for medical bypass patterns and fail-closed immediately.

---

## Quality & Verification
- **Backend Test Suite**: 438 automated tests (including security header validation, safety engine pre-checks, and smoke tests).
- **Frontend Test Suite**: 61+ automated unit and integration tests (covering page setups, auth routing, i18n translation, error recovery, and session completion).
- **Static Quality**: Strict linting, formatting, and strict type verification (mypy, ruff, black, eslint, prettier).

---

## Exact Demo Flow
1. **Register/Login**: Create a test account or log in.
2. **Complete Setup**:
   - Go to **Intelligent Workouts**.
   - Fill in **Training Profile** (goals, experience, equipment).
   - Fill in **Health Declaration** (injuries, pain areas).
3. **Generate Plan**: Click "Generate safe plan".
4. **Execute Session**:
   - Open the active plan.
   - Start the workout session.
   - Record set completion and mark "I experienced pain" to trigger server-side adaptation flags.
   - Complete or abandon the session.
5. **View Adaptation**: Click "Review adaptation" to view server-calculated recommendations.

---

## Known Non-Commercial Limitations
- **Disabled AI features**: The natural-language AI Coach interface is currently gated (`ai_feature_enabled=false`) to prevent unvalidated advice.
- **In-Memory Rate Limiting**: The rate limiter is stateful in-memory and must be replaced with a Redis provider before multi-instance production deployment.
- **Session Storage Tokens**: Refresh tokens are stored in sessionStorage and must move to secure HttpOnly cookies for enterprise-grade session protection.
- **Content-Security-Policy (CSP)**: Must be configured at the web server/reverse proxy level serving the static HTML build, as the FastAPI backend is JSON-only.
