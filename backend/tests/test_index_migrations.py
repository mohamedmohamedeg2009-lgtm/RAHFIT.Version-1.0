import pytest

from app.database.indexes import (
    AI_CONVERSATION_INDEXES,
    AI_MESSAGE_INDEXES,
    WORKOUT_SESSION_INDEX,
    ensure_ai_conversation_indexes,
    ensure_named_index,
    ensure_workout_session_index,
)


class FakeCollection:
    def __init__(self, index: dict[str, object] | None) -> None:
        self.index = index
        self.dropped: list[str] = []
        self.created: list[dict[str, object]] = []

    async def index_information(self) -> dict[str, dict[str, object]]:
        return {WORKOUT_SESSION_INDEX: self.index} if self.index else {}

    async def drop_index(self, name: str) -> None:
        self.dropped.append(name)

    async def create_index(self, keys: object, **options: object) -> None:
        self.created.append({"keys": keys, **options})


@pytest.mark.asyncio
async def test_legacy_workout_index_is_upgraded_before_creation() -> None:
    collection = FakeCollection({"key": []})

    await ensure_workout_session_index(collection)

    assert collection.dropped == [WORKOUT_SESSION_INDEX]
    assert collection.created[0]["unique"] is True
    assert collection.created[0]["partialFilterExpression"] == {"status": "in_progress"}


@pytest.mark.asyncio
async def test_compatible_workout_index_is_not_dropped() -> None:
    collection = FakeCollection(
        {"unique": True, "partialFilterExpression": {"status": "in_progress"}}
    )

    await ensure_workout_session_index(collection)

    assert collection.dropped == []


class FakeNamedIndexCollection:
    def __init__(self) -> None:
        self.indexes: dict[str, dict[str, object]] = {}
        self.dropped: list[str] = []
        self.created: list[str] = []

    async def index_information(self) -> dict[str, dict[str, object]]:
        return dict(self.indexes)

    async def drop_index(self, name: str) -> None:
        self.dropped.append(name)
        self.indexes.pop(name, None)

    async def create_index(self, keys: object, **options: object) -> None:
        name = str(options["name"])
        self.created.append(name)
        self.indexes[name] = {"key": keys}


class FakeIndexDatabase:
    def __init__(self) -> None:
        self.collections = {
            "ai_conversations": FakeNamedIndexCollection(),
            "ai_messages": FakeNamedIndexCollection(),
        }

    def __getitem__(self, name: str) -> FakeNamedIndexCollection:
        return self.collections[name]


@pytest.mark.asyncio
async def test_ai_indexes_initialize_repeatedly_without_conflicts() -> None:
    database = FakeIndexDatabase()

    await ensure_ai_conversation_indexes(database)
    await ensure_ai_conversation_indexes(database)

    conversation_collection = database["ai_conversations"]
    message_collection = database["ai_messages"]
    assert conversation_collection.created == [name for name, _ in AI_CONVERSATION_INDEXES]
    assert message_collection.created == [name for name, _ in AI_MESSAGE_INDEXES]
    assert conversation_collection.dropped == message_collection.dropped == []


@pytest.mark.asyncio
async def test_same_name_ai_index_drift_is_replaced_without_dropping_other_indexes() -> None:
    collection = FakeNamedIndexCollection()
    collection.indexes = {
        "ai_conversations_owner_activity": {"key": [("user_id", 1)]},
        "unrelated_index": {"key": [("keep", 1)]},
    }
    expected = [("user_id", 1), ("last_activity_at", -1), ("_id", -1)]

    await ensure_named_index(collection, expected, "ai_conversations_owner_activity")

    assert collection.dropped == ["ai_conversations_owner_activity"]
    assert "unrelated_index" in collection.indexes
    assert collection.indexes["ai_conversations_owner_activity"]["key"] == expected
