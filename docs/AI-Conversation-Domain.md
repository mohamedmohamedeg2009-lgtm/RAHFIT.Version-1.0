# RAHFIT AI — AI Conversation Domain and Persistence

## Sprint scope

Sprint 2.2 establishes secure storage and lifecycle foundations for AI Coach conversations. It does not generate responses, call an AI provider, build prompts or context, summarize history, create memory, track tokens, stream output, or add frontend chat routes.

## Conversation model

An AI conversation is a versioned aggregate owned by exactly one authenticated user. Its public contract contains a generated conversation ID, normalized bounded title, lifecycle status, creation and activity timestamps, optional close and last-message timestamps, message count, and schema version. The persisted owner ID and deletion timestamp are internal authorization and lifecycle fields and are not accepted from or exposed to clients.

New conversations use the safe title `New conversation` when no meaningful title is supplied. Titles are collapsed to single-space word boundaries and limited to 120 characters.

## Message model

Messages are versioned, plain-text records scoped by both conversation ID and owner ID. Persisted roles are:

- `user`, created only by the dedicated trusted user-message service method;
- `assistant`, created only by an internal application method;
- `system_notice`, created only by an internal lifecycle method.

Each message records a generated ID, conversation ID, internal owner ID, fixed role, bounded content, trusted source, creation time, optional deletion time, and schema version. Content is limited to 4,000 characters, whitespace-only input and unsupported control characters are rejected, and no HTML rendering, prompt execution, or dynamic evaluation occurs.

## Ownership and authorization

Authentication supplies the owner ID. Request schemas forbid extra ownership, status, timestamps, message-count, provider, model, or metadata fields. Repository lookups include both conversation ID and owner ID whenever a caller addresses a specific resource. Missing, deleted, and differently owned conversations share the same safe not-found response for read and close operations.

List and detail operations never return another user's records. There is no public message-creation endpoint, so clients cannot submit an assistant or system role.

## Lifecycle

Supported states are `active`, `closed`, and `deleted`.

| Current state | Operation | Result |
|---|---|---|
| Active | Close | Closed with an immutable first close timestamp |
| Active | Delete | Soft-deleted |
| Closed | Close | Closed; idempotent success |
| Closed | Read | Allowed |
| Closed | Delete | Soft-deleted |
| Closed | Normal user/assistant append | Rejected |
| Closed | Exceptional system notice | Allowed only through the trusted lifecycle method |
| Deleted | Read, close, or append | Hidden or rejected |
| Deleted | Delete | Idempotent no-content success |

Deletion marks the parent and every owned child message as deleted. Normal list and detail queries exclude deleted parents, so child history cannot be reached through the service or API after deletion.

## Repository architecture

`AIConversationRepository` owns creation, owner-scoped retrieval and pagination, atomic activity counters, close transitions, and soft deletion in `ai_conversations`. `AIMessageRepository` owns trusted message persistence, owner-scoped bounded history, stable chronological output, and child soft deletion in `ai_messages`.

Conversation list ordering is deterministic: newest `last_activity_at` first with ID as a tie-breaker. Message history selects the most recent bounded records and reverses that selection into chronological order for the response.

## Service responsibilities

`AIConversationService` owns title normalization, ownership behavior, pagination limits, lifecycle transitions, safe deletion, history truncation metadata, retained-message limits, and distinct trusted append methods. It performs no authentication parsing and receives the authenticated user ID from the controller dependency. It never resolves or invokes an AI provider.

## API

All routes are authenticated under `/api/v1/ai-coach`.

| Method | Route | Behavior |
|---|---|---|
| `POST` | `/conversations` | Creates one active local conversation; accepts only an optional title |
| `GET` | `/conversations` | Returns a bounded owner-only summary page, newest activity first |
| `GET` | `/conversations/{conversation_id}` | Returns owner-only detail and bounded chronological history |
| `POST` | `/conversations/{conversation_id}/close` | Performs the explicit, idempotent close transition |
| `DELETE` | `/conversations/{conversation_id}` | Soft-deletes the owner-scoped aggregate and returns no content |

`POST` is used for close to match existing project lifecycle-command conventions. No `/messages` route exists in this sprint.

## Limits and retention

Competition-ready centralized defaults are:

- 20 conversations per page by default and 50 maximum;
- 120 title characters;
- 4,000 message characters;
- 100 most recent messages in a detail response;
- 500 retained messages per conversation.

History truncation is explicit through `message_history_limit` and `messages_truncated`. The retained history is not summarized or silently reordered. Soft-deleted records remain available only for future controlled retention jobs and operational recovery; no TTL index is installed, so active competition data cannot expire unexpectedly. A production privacy policy must define the later purge window before commercialization.

## Index design and migration safety

Named indexes support owner activity ordering, owner/status filtering, creation-time operations, conversation chronology, and owner/conversation message isolation. Index initialization reads existing definitions first. A compatible named index is left unchanged; only an incompatible index owned by this domain is replaced, and unrelated indexes are never dropped. Initialization is safe to repeat.

Any future index definition change must use a new reviewed migration or the same inspect-and-replace helper, validate data compatibility before enforcing uniqueness, and include repeated-initialization and conflict-regression tests.

## Security and logging

The design prevents mass assignment, broken object-level authorization, ID enumeration disclosure, role impersonation, unbounded reads, deleted-data exposure, and lifecycle bypass. Generated IDs follow a strict 32-character hexadecimal format. MongoDB filters are constructed by repositories from validated scalar inputs rather than client-provided query objects.

Message content is treated exclusively as plain text and must be escaped by every future renderer. The service emits no content logs. Production logs may include authenticated user ID, conversation ID, operation, transition, stable error category, and message length. They must never include message content, prompts, tokens, passwords, API keys, or provider credentials.

## Testing strategy

Automated coverage verifies authentication, safe input validation, owner derivation, cross-user isolation, list ordering and bounds, lifecycle idempotency, deletion hiding, trusted fixed roles, message validation, chronological truncation, retained-history limits, migration-safe repeated index initialization, conflict replacement, provider non-use, and compatibility with existing features.

## Explicitly deferred

Provider generation, public message sending, prompt and context construction, capability classification, AI safety generation gates, governed memory, summarization, token and cost tracking, feedback, streaming, tool use, internet access, autonomous behavior, frontend chat state, and workout or nutrition mutation are deferred to later approved sprints.
