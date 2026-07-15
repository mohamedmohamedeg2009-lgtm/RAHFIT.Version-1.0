from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import Settings


class MongoDatabase:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.client: AsyncIOMotorClient[dict[str, object]] | None = None

    async def connect(self) -> None:
        self.client = AsyncIOMotorClient(self._settings.mongodb_uri.unicode_string())
        await self.client.admin.command("ping")

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None

    @property
    def database(self) -> AsyncIOMotorDatabase[dict[str, object]]:
        if not self.client:
            raise RuntimeError("Database connection has not been initialized.")
        return self.client[self._settings.mongodb_database]
