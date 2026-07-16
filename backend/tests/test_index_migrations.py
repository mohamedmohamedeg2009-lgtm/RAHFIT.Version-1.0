import pytest

from app.database.indexes import WORKOUT_SESSION_INDEX, ensure_workout_session_index


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
