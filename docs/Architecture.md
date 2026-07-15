# Architecture

## Design

RAHFIT AI uses a modular monorepo with a React client and a FastAPI service. The backend follows clean-architecture-inspired dependency direction:

```
API / controllers → services → repositories → database
                    ↑
              schemas / models
```

Controllers translate HTTP only. Services will own use cases and transaction orchestration. Repositories isolate Motor/MongoDB calls. Models represent persistence; schemas are explicit request/response contracts. Feature code must depend on abstractions at its boundary, not on other features' database internals.

## Cross-cutting infrastructure

- `config`: Pydantic Settings validates all deployment configuration at startup. Secrets are environment variables and never committed.
- `core`: structured JSON logging and one standard API error envelope.
- `middleware`: correlation IDs, security headers, CORS, and a deliberately simple rate-limit seam.
- `security`: password hashing, JWT creation primitive, and Mongo operator rejection. No authentication route or authentication policy exists in this phase.
- `database`: application lifecycle owns the Motor client; index registration is centralized.

## Production decisions

Mongo is pinged on startup so an unhealthy deployment fails early. Each response carries `X-Request-ID`, and logs contain the same context. Error details are returned for validation failures; unexpected exception details are not leaked. The current rate limiter is process-local by design and must be replaced by Redis or a gateway policy before horizontal scaling.

## Extension points

- Add a feature package spanning `api`, `controllers`, `services`, `repositories`, `models`, and `schemas`.
- Register database indexes only in `database/indexes.py`, adjacent to collection introduction.
- Replace rate-limit storage with Redis and wire monitoring/tracing adapters at the existing middleware/logging seams.
- Add JWT verification and authorization dependencies only alongside an explicitly approved authentication phase.
- Place AI providers behind interfaces in `app/ai`; services should receive those interfaces through dependency injection.
