# RAHFIT AI Judge Questions and Answers

Use these concise answers as a guide. Do not claim functionality outside the current competition scope.

## Product

### What problem does RAHFIT AI solve?

It helps users move from generic fitness advice to readiness-aware next steps. It gathers structured assessment, profile, and health information before presenting dashboard, workout, and nutrition guidance.

### What makes it different from normal fitness applications?

Safety and explainability are first-class. The product uses owner-scoped data, deterministic readiness rules, and explicit feature states instead of treating an LLM as an unrestricted coach.

### How could this become a real business?

The next commercial steps are a bounded AI Coach flow, subscriptions/payments, reports, notifications, wearables, and coach or organization features. Those should follow validated user needs and a defined privacy/retention model.

## Technology Choices

### Why FastAPI?

FastAPI provides typed request/response contracts, Pydantic validation, dependency injection, automatic OpenAPI documentation, and an asynchronous fit for MongoDB access. It keeps the API explicit and testable.

### Why React and TypeScript?

React supports route-level product experiences and reusable UI state. TypeScript makes API mappings, route data, and component contracts safer during frontend iteration.

### Why MongoDB?

The product stores evolving user-centered aggregates such as assessment sessions, plans, logs, and conversations. MongoDB fits those document shapes while indexes support owner-scoped reads and lifecycle queries.

### What percentage of the project uses Python?

We do not use a percentage as a quality metric. Python owns the backend, domain rules, authentication, persistence, tests, and AI safety architecture. TypeScript owns the browser application. Both are essential parts of the system.

### How does Docker help the project?

Docker Compose starts MongoDB, FastAPI, and Nginx/React together with predictable service names and health dependencies. A judge can run the core stack with one command instead of manually wiring services.

## Security and Data Protection

### How does authentication work?

Users can use password authentication, and Google ID-token support is available when configured. Passwords are hashed. The backend issues an access token and refresh token after successful authentication.

### How are APIs protected?

Protected endpoints require a bearer access token. The backend validates JWT signature, expiry, token type, and token version, then loads the authenticated user. Controllers and repositories use that owner identity rather than trusting a user ID from the client.

### How does session refresh work?

The frontend keeps the access token in memory and uses the refresh token to obtain a new token pair after a reload. The backend checks refresh-token type and current token version before issuing new tokens.

### How is user data isolated?

Every addressed resource is queried with both its identifier and the authenticated owner identifier. Missing and foreign records use the same safe not-found behavior, which avoids revealing another user’s data.

### How do you handle injuries?

Health declarations and assessment safety status feed readiness and workout-selection rules. The system blocks or constrains unsafe plan generation; it does not diagnose an injury or invent medical rehabilitation advice.

## AI and Safety

### Where is the actual AI?

The repository includes provider adapters and a provider-neutral AI service boundary. More importantly, Python owns the deterministic classifier, policy layer, approved context builder, and safety engine that govern whether a provider could be used.

### How does the AI safety system work?

It receives typed classifier, policy, owner, and approved-context inputs. It evaluates deterministic rules in precedence order and returns allow, caution, refusal, professional-guidance, or fail-closed fallback decisions. Unsafe cases do not reach a provider.

### Why is AI Coach messaging not fully public yet?

Conversation lifecycle and availability foundations are implemented, but public message sending/listing is intentionally unregistered. Exposing it requires a stable public contract, complete fallback behavior, and end-to-end safety coverage. Deferring it is the safer release decision.

### How do you prevent unsafe fitness or medical advice?

The policy layer forbids diagnosis, medication advice, safety overrides, secret disclosure, and similar actions. The safety engine detects urgent symptoms, injury/allergy conflicts, dangerous fasting or training, and prompt-security attempts. It can require professional guidance or refuse the request before provider generation.

## Architecture and Testing

### What tests were implemented?

The backend suite covers authentication, owner isolation, assessment, workout and nutrition engines, dashboard behavior, security headers, indexes, AI classifier/policy/context/safety/provider boundaries, and API contracts. The frontend suite covers authentication, dashboard, assessment, workout, nutrition, intelligent-workout, error-boundary, and UI behavior.

### What would you build next?

First, complete the bounded public AI Coach messaging contract with safe fallbacks and end-to-end tests. Then add reports, notifications, usage telemetry, and carefully scoped integrations such as wearables.

### What was the most difficult technical issue?

A strong answer is: “Keeping the product useful without letting AI bypass safety or domain rules. The solution was to make readiness, policy, context, and safety deterministic Python layers, then treat any provider as a constrained dependency.”

### What did you personally implement and learn?

Answer only from your own work. A safe template is: “I implemented [your actual contribution] and learned how to [specific technical lesson]. The main lesson was that a health-adjacent product needs explicit validation, ownership boundaries, and safe failure states—not only attractive UI.”

## Quick Architecture Answer

> “React and TypeScript run in the browser. Nginx serves the app and proxies same-origin API requests. FastAPI exposes typed, authenticated APIs and delegates domain rules to services. MongoDB stores owner-scoped documents. JWT verifies the user. Python-owned classifier, policy, context, and safety layers constrain AI behavior. Docker Compose runs the three services together.”

## Scope Answer

| Implemented | Partially implemented | Planned |
| --- | --- | --- |
| Authentication, assessment/readiness, dashboard, deterministic workout/nutrition flows, persistence, Docker, and core tests. | AI Coach UI, availability, and conversation lifecycle; public message sending/listing is intentionally deferred. | Public bounded AI messaging, streaming, feedback, reports, notifications, wearables, payments, and enterprise features. |
