from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConfigurationError, ConnectionFailure, OperationFailure, PyMongoError

from app.config import Settings


class DatabaseConnectionError(RuntimeError):
    """Raised when MongoDB cannot be reached without exposing connection secrets."""


def redact_mongodb_uri(uri: str) -> str:
    """Remove URI credentials before an address is ever included in diagnostics."""
    scheme, separator, remainder = uri.partition("://")
    if not separator:
        return "<invalid MongoDB URI>"
    credentials, at_sign, location = remainder.partition("@")
    if not at_sign:
        return f"{scheme}://{remainder}"
    del credentials
    return f"{scheme}://<credentials-redacted>@{location}"


class MongoDatabase:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.client: AsyncIOMotorClient[dict[str, object]] | None = None

    async def connect(self) -> None:
        try:
            self.client = AsyncIOMotorClient(
                self._settings.mongodb_uri.unicode_string(),
                serverSelectionTimeoutMS=self._settings.mongodb_server_selection_timeout_ms,
                connectTimeoutMS=self._settings.mongodb_connect_timeout_ms,
                retryWrites=True,
                appname=self._settings.mongodb_app_name,
            )
            await self.client.admin.command("ping")
        except (
            ConfigurationError,
            ConnectionFailure,
            OperationFailure,
            OSError,
            PyMongoError,
        ) as exc:
            if self.client:
                self.client.close()
            self.client = None
            raise DatabaseConnectionError(self._connection_error_message(exc)) from None

    @staticmethod
    def _connection_error_message(exc: BaseException) -> str:
        error_text = str(exc).lower()
        if isinstance(exc, OperationFailure) or "authentication" in error_text:
            return "MongoDB authentication failed. Check the database user credentials and permissions."
        if isinstance(exc, ConfigurationError) or "dns" in error_text or "srv" in error_text:
            return "MongoDB URI or DNS/SRV resolution failed. Check MONGODB_URI and network access."
        return (
            "MongoDB is unreachable or timed out. Check network access and database availability."
        )

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None

    @property
    def database(self) -> AsyncIOMotorDatabase[dict[str, object]]:
        if not self.client:
            raise RuntimeError("Database connection has not been initialized.")
        return self.client[self._settings.mongodb_database]
