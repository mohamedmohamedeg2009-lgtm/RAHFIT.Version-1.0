from datetime import UTC, datetime, timedelta

import httpx
import pytest
from fastapi import FastAPI

from app.ai.conversation_limits import AIConversationLimits
from app.ai.providers import OpenAICompatibleProvider
from app.config import Settings, get_settings
from app.controllers.ai_coach import get_ai_conversation_service, router
from app.controllers.auth import get_auth_service, get_current_user
from app.models.ai_conversation import (
    AIConversation,
    AIConversationStatus,
    AIMessage,
    AIMessageRole,
)
from app.models.user import User
from app.services.ai_conversation import (
    AIConversationLimitError,
    AIConversationNotFoundError,
    AIConversationService,
    AIConversationStateError,
    AIConversationValidationError,
)


class InMemoryAIConversationStore:
    def __init__(self) -> None:
        self.conversations: dict[str, AIConversation] = {}
        self.messages: dict[str, AIMessage] = {}

    async def create(self, conversation: AIConversation) -> AIConversation:
        self.conversations[conversation.id] = conversation
        return conversation

    async def find_by_id_and_owner(
        self, conversation_id: str, user_id: str
    ) -> AIConversation | None:
        conversation = self.conversations.get(conversation_id)
        if (
            not conversation
            or conversation.user_id != user_id
            or conversation.status == AIConversationStatus.DELETED
        ):
            return None
        return conversation

    async def list_by_owner(
        self, user_id: str, limit: int, offset: int
    ) -> tuple[list[AIConversation], bool]:
        owned = sorted(
            (
                item
                for item in self.conversations.values()
                if item.user_id == user_id and item.status != AIConversationStatus.DELETED
            ),
            key=lambda item: (item.last_activity_at, item.id),
            reverse=True,
        )
        page = owned[offset : offset + limit + 1]
        return page[:limit], len(page) > limit

    async def close(self, conversation_id: str, user_id: str) -> AIConversation | None:
        conversation = await self.find_by_id_and_owner(conversation_id, user_id)
        if not conversation:
            return None
        if conversation.status == AIConversationStatus.CLOSED:
            return conversation
        now = datetime.now(UTC)
        closed = conversation.model_copy(
            update={
                "status": AIConversationStatus.CLOSED,
                "closed_at": now,
                "updated_at": now,
                "last_activity_at": now,
            }
        )
        self.conversations[conversation_id] = closed
        return closed

    async def soft_delete(self, conversation_id: str, user_id: str) -> AIConversation | None:
        conversation = await self.find_by_id_and_owner(conversation_id, user_id)
        if not conversation:
            return None
        now = datetime.now(UTC)
        deleted = conversation.model_copy(
            update={
                "status": AIConversationStatus.DELETED,
                "deleted_at": now,
                "updated_at": now,
                "last_activity_at": now,
            }
        )
        self.conversations[conversation_id] = deleted
        return deleted

    async def record_message(
        self,
        conversation_id: str,
        user_id: str,
        created_at: datetime,
        allowed_statuses: tuple[AIConversationStatus, ...],
    ) -> AIConversation | None:
        conversation = await self.find_by_id_and_owner(conversation_id, user_id)
        if not conversation or conversation.status not in allowed_statuses:
            return None
        updated = conversation.model_copy(
            update={
                "message_count": conversation.message_count + 1,
                "last_message_at": created_at,
                "last_activity_at": created_at,
                "updated_at": created_at,
            }
        )
        self.conversations[conversation_id] = updated
        return updated

    async def create_message(self, message: AIMessage) -> AIMessage:
        self.messages[message.id] = message
        return message

    async def list_by_conversation_and_owner(
        self, conversation_id: str, user_id: str, limit: int
    ) -> list[AIMessage]:
        matching = sorted(
            (
                item
                for item in self.messages.values()
                if item.conversation_id == conversation_id
                and item.user_id == user_id
                and item.deleted_at is None
            ),
            key=lambda item: (item.created_at, item.id),
        )
        return matching[-limit:]

    async def soft_delete_by_conversation(self, conversation_id: str, user_id: str) -> None:
        now = datetime.now(UTC)
        for message_id, message in tuple(self.messages.items()):
            if message.conversation_id == conversation_id and message.user_id == user_id:
                self.messages[message_id] = message.model_copy(update={"deleted_at": now})

    async def soft_delete_message(self, message_id: str, user_id: str) -> None:
        message = self.messages.get(message_id)
        if message and message.user_id == user_id:
            self.messages[message_id] = message.model_copy(update={"deleted_at": datetime.now(UTC)})


class MessageStoreAdapter:
    def __init__(self, store: InMemoryAIConversationStore) -> None:
        self.store = store

    async def create(self, message: AIMessage) -> AIMessage:
        return await self.store.create_message(message)

    async def list_by_conversation_and_owner(
        self, conversation_id: str, user_id: str, limit: int
    ) -> list[AIMessage]:
        return await self.store.list_by_conversation_and_owner(conversation_id, user_id, limit)

    async def soft_delete_by_conversation(self, conversation_id: str, user_id: str) -> None:
        await self.store.soft_delete_by_conversation(conversation_id, user_id)

    async def soft_delete_message(self, message_id: str, user_id: str) -> None:
        await self.store.soft_delete_message(message_id, user_id)


def conversation_service(
    limits: AIConversationLimits | None = None,
) -> tuple[AIConversationService, InMemoryAIConversationStore]:
    store = InMemoryAIConversationStore()
    service = AIConversationService(
        store, MessageStoreAdapter(store), limits or AIConversationLimits()
    )
    return service, store


def authenticated_user(user_id: str = "owner-user") -> User:
    return User(
        id=user_id,
        email=f"{user_id}@example.com",
        password_hash="hash-never-exposed",
    )


def configured_settings() -> Settings:
    return Settings(
        _env_file=None,
        mongodb_uri="mongodb://localhost:27017",
        mongodb_database="rahfit_test",
        jwt_secret_key="a" * 32,
    )


@pytest.mark.asyncio
async def test_creation_normalizes_title_and_derives_owner_from_trusted_identity() -> None:
    service, _ = conversation_service()

    titled = await service.create_conversation("owner-user", "  Weekly   coaching  ")
    defaulted = await service.create_conversation("owner-user", "   ")

    assert titled.title == "Weekly coaching"
    assert titled.user_id == "owner-user"
    assert titled.status == AIConversationStatus.ACTIVE
    assert defaulted.title == "New conversation"


@pytest.mark.asyncio
async def test_service_rejects_oversized_title_and_unsafe_pagination() -> None:
    service, _ = conversation_service()

    with pytest.raises(AIConversationValidationError):
        await service.create_conversation("owner-user", "x" * 121)
    with pytest.raises(AIConversationValidationError):
        await service.list_conversations("owner-user", limit=51)


@pytest.mark.asyncio
async def test_list_is_owner_isolated_excludes_deleted_and_orders_recent_activity() -> None:
    service, store = conversation_service()
    older = await service.create_conversation("owner-user", "Older")
    other = await service.create_conversation("other-user", "Private")
    newer = await service.create_conversation("owner-user", "Newer")
    store.conversations[older.id] = older.model_copy(
        update={"last_activity_at": datetime.now(UTC) - timedelta(days=1)}
    )
    await service.delete_conversation("other-user", other.id)

    result = await service.list_conversations("owner-user", limit=10)

    assert [item.id for item in result.items] == [newer.id, older.id]
    assert all(item.user_id == "owner-user" for item in result.items)


@pytest.mark.asyncio
async def test_cross_user_operations_share_safe_not_found_behavior() -> None:
    service, _ = conversation_service()
    conversation = await service.create_conversation("owner-user")

    with pytest.raises(AIConversationNotFoundError):
        await service.get_conversation("other-user", conversation.id)
    with pytest.raises(AIConversationNotFoundError):
        await service.close_conversation("other-user", conversation.id)
    await service.delete_conversation("other-user", conversation.id)
    assert (await service.get_conversation("owner-user", conversation.id)).conversation.id == (
        conversation.id
    )


@pytest.mark.asyncio
async def test_close_is_idempotent_readable_and_rejects_normal_messages() -> None:
    service, _ = conversation_service()
    conversation = await service.create_conversation("owner-user")

    first = await service.close_conversation("owner-user", conversation.id)
    second = await service.close_conversation("owner-user", conversation.id)
    detail = await service.get_conversation("owner-user", conversation.id)

    assert first.status == second.status == AIConversationStatus.CLOSED
    assert first.closed_at == second.closed_at
    assert detail.conversation.status == AIConversationStatus.CLOSED
    with pytest.raises(AIConversationStateError):
        await service.append_user_message("owner-user", conversation.id, "Cannot append")
    with pytest.raises(AIConversationStateError):
        await service.append_assistant_message("owner-user", conversation.id, "Cannot append")


@pytest.mark.asyncio
async def test_trusted_methods_create_only_their_fixed_roles_and_plain_text() -> None:
    service, _ = conversation_service()
    conversation = await service.create_conversation("owner-user")

    with pytest.raises(AIConversationValidationError):
        await service.append_user_message(
            "owner-user", conversation.id, "<script>not stored</script>"
        )
    user_message = await service.append_user_message("owner-user", conversation.id, "Plain text")
    assistant = await service.append_assistant_message(
        "owner-user", conversation.id, "Application response"
    )
    notice = await service.append_system_notice("owner-user", conversation.id, "Safety notice")

    assert user_message.role == AIMessageRole.USER
    assert user_message.content == "Plain text"
    assert assistant.role == AIMessageRole.ASSISTANT
    assert notice.role == AIMessageRole.SYSTEM_NOTICE


@pytest.mark.asyncio
async def test_message_validation_and_retention_limit_are_enforced() -> None:
    limits = AIConversationLimits(maximum_message_length=10, maximum_retained_messages=1)
    service, _ = conversation_service(limits)
    conversation = await service.create_conversation("owner-user")

    with pytest.raises(AIConversationValidationError):
        await service.append_user_message("owner-user", conversation.id, "   ")
    with pytest.raises(AIConversationValidationError):
        await service.append_user_message("owner-user", conversation.id, "x" * 11)
    await service.append_user_message("owner-user", conversation.id, "first")
    with pytest.raises(AIConversationLimitError):
        await service.append_user_message("owner-user", conversation.id, "second")


@pytest.mark.asyncio
async def test_history_returns_latest_bounded_messages_in_chronological_order() -> None:
    limits = AIConversationLimits(maximum_history_response=2)
    service, _ = conversation_service(limits)
    conversation = await service.create_conversation("owner-user")
    await service.append_user_message("owner-user", conversation.id, "first")
    await service.append_assistant_message("owner-user", conversation.id, "second")
    await service.append_system_notice("owner-user", conversation.id, "third")

    detail = await service.get_conversation("owner-user", conversation.id)

    assert [message.content for message in detail.messages] == ["second", "third"]
    assert detail.messages_truncated is True
    assert detail.message_history_limit == 2


@pytest.mark.asyncio
async def test_delete_is_repeatable_and_hides_conversation_and_messages() -> None:
    service, store = conversation_service()
    conversation = await service.create_conversation("owner-user")
    message = await service.append_user_message("owner-user", conversation.id, "Private content")

    await service.delete_conversation("owner-user", conversation.id)
    await service.delete_conversation("owner-user", conversation.id)

    with pytest.raises(AIConversationNotFoundError):
        await service.get_conversation("owner-user", conversation.id)
    assert store.messages[message.id].deleted_at is not None
    assert (await service.list_conversations("owner-user")).items == ()


@pytest.mark.asyncio
async def test_conversation_api_lifecycle_rejects_mass_assignment_and_exposes_no_owner() -> None:
    service, _ = conversation_service()
    current_user = {"value": authenticated_user()}
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_current_user] = lambda: current_user["value"]
    app.dependency_overrides[get_ai_conversation_service] = lambda: service

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        rejected = await client.post(
            "/api/v1/ai-coach/conversations",
            json={"title": "Unsafe", "user_id": "attacker", "status": "closed"},
        )
        created = await client.post(
            "/api/v1/ai-coach/conversations", json={"title": " API conversation "}
        )
        conversation_id = created.json()["id"]
        listed = await client.get("/api/v1/ai-coach/conversations?limit=10")
        fetched = await client.get(f"/api/v1/ai-coach/conversations/{conversation_id}")
        closed = await client.post(f"/api/v1/ai-coach/conversations/{conversation_id}/close")
        deleted = await client.delete(f"/api/v1/ai-coach/conversations/{conversation_id}")
        missing = await client.get(f"/api/v1/ai-coach/conversations/{conversation_id}")

    assert rejected.status_code == 422
    assert created.status_code == 201
    assert created.json()["title"] == "API conversation"
    assert "user_id" not in created.json()
    assert listed.json()["items"][0]["id"] == conversation_id
    assert fetched.status_code == 200
    assert closed.json()["status"] == "closed"
    assert deleted.status_code == 204
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_api_cross_user_access_and_identifier_enumeration_do_not_leak() -> None:
    service, _ = conversation_service()
    current_user = {"value": authenticated_user("owner-user")}
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_current_user] = lambda: current_user["value"]
    app.dependency_overrides[get_ai_conversation_service] = lambda: service

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        created = await client.post("/api/v1/ai-coach/conversations", json={})
        conversation_id = created.json()["id"]
        current_user["value"] = authenticated_user("other-user")
        get_denied = await client.get(f"/api/v1/ai-coach/conversations/{conversation_id}")
        close_denied = await client.post(f"/api/v1/ai-coach/conversations/{conversation_id}/close")
        delete_hidden = await client.delete(f"/api/v1/ai-coach/conversations/{conversation_id}")
        absent = await client.get("/api/v1/ai-coach/conversations/0" + "0" * 31)
        invalid = await client.get("/api/v1/ai-coach/conversations/not-an-id")

    assert get_denied.status_code == close_denied.status_code == absent.status_code == 404
    assert get_denied.json() == close_denied.json() == absent.json()
    assert delete_hidden.status_code == 204
    assert invalid.status_code == 422


@pytest.mark.asyncio
async def test_every_conversation_endpoint_requires_authentication() -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_settings] = configured_settings
    app.dependency_overrides[get_auth_service] = lambda: object()
    conversation_id = "0" * 32

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        responses = [
            await client.post("/api/v1/ai-coach/conversations", json={}),
            await client.get("/api/v1/ai-coach/conversations"),
            await client.get(f"/api/v1/ai-coach/conversations/{conversation_id}"),
            await client.post(f"/api/v1/ai-coach/conversations/{conversation_id}/close"),
            await client.delete(f"/api/v1/ai-coach/conversations/{conversation_id}"),
        ]

    assert all(response.status_code == 401 for response in responses)


@pytest.mark.asyncio
async def test_conversation_operations_never_call_provider_or_log_content(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    async def forbidden_generate(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("Conversation persistence must not call a provider.")

    monkeypatch.setattr(OpenAICompatibleProvider, "generate", forbidden_generate)
    service, _ = conversation_service()
    conversation = await service.create_conversation("owner-user", "Local only")
    secret_content = "private-message-content-must-not-be-logged"
    await service.append_user_message("owner-user", conversation.id, secret_content)
    await service.get_conversation("owner-user", conversation.id)

    assert secret_content not in caplog.text


@pytest.mark.asyncio
async def test_public_message_endpoints_remain_unregistered() -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_settings] = configured_settings
    app.dependency_overrides[get_auth_service] = lambda: object()
    conversation_id = "0" * 32

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Top level unregistered message paths return 404
        unregistered = [
            await client.get("/api/v1/ai-coach/messages"),
            await client.post("/api/v1/ai-coach/messages", json={"content": "hello"}),
        ]
        get_on_messages = await client.get(f"/api/v1/ai-coach/conversations/{conversation_id}/messages")

    assert all(response.status_code == 404 for response in unregistered)
    assert get_on_messages.status_code == 405


@pytest.mark.asyncio
async def test_message_endpoint_is_available_for_an_authenticated_conversation() -> None:
    service, _ = conversation_service()
    current_user = {"value": authenticated_user("owner-user")}
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_current_user] = lambda: current_user["value"]
    app.dependency_overrides[get_ai_conversation_service] = lambda: service

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Create conversation
        created = await client.post("/api/v1/ai-coach/conversations", json={"title": "Chat"})
        conversation_id = created.json()["id"]

        # GET messages returns 405 Method Not Allowed
        msgs_before = await client.get(f"/api/v1/ai-coach/conversations/{conversation_id}/messages")
        assert msgs_before.status_code == 405
