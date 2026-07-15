# Folder Structure

## Backend

| Folder | Responsibility |
| --- | --- |
| `api` | Router composition and API versioning |
| `controllers` | Thin HTTP request/response translation |
| `services` | Feature use cases and business orchestration |
| `repositories` | Database access abstractions |
| `models` | Persistence representations |
| `schemas` | Pydantic contracts |
| `middleware` | Request-wide HTTP behavior |
| `security` | Reusable security primitives |
| `config`, `core` | Settings and cross-cutting concerns |
| `database` | MongoDB lifecycle and indexes |
| `ai` | Future provider boundary only |
| `utils` | Narrow pure helpers |
| `tests` | Automated tests |

## Frontend

| Folder | Responsibility |
| --- | --- |
| `app` | Root composition and global error handling |
| `components`, `layouts`, `pages` | Reusable UI, page shells, routes |
| `hooks`, `contexts` | Shared state and browser behavior |
| `services` | Typed API clients and external integrations |
| `types`, `utils` | Shared types and pure helpers |
| `assets`, `styles` | Static resources and global styling |

Empty folders are intentionally retained to make the approved architecture visible before features begin.
