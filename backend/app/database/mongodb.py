import ssl
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlsplit

import structlog
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import (
    ConfigurationError,
    ConnectionFailure,
    InvalidURI,
    OperationFailure,
    PyMongoError,
    ServerSelectionTimeoutError,
)

from app.config import Settings


class DatabaseConnectionError(RuntimeError):
    """Raised when MongoDB cannot be reached without exposing connection secrets."""


logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class MongoConnectionDiagnostic:
    """Secret-free details suitable for a startup log entry."""

    exception_class: str
    safe_reason: str
    message: str


@dataclass(frozen=True)
class MongoConnectionConfiguration:
    """Safe, parsed connection details that never include credentials or query values."""

    uri_scheme: str
    hostname: str | None
    database_name: str
    query_keys: tuple[str, ...]


def mongodb_uri_scheme(uri: str) -> str:
    """Return the permitted URI scheme without retaining any credential-bearing URI data."""
    scheme = uri.partition("://")[0].lower()
    return scheme if scheme in {"mongodb", "mongodb+srv"} else "invalid"


def mongodb_connection_configuration(uri: str, database_name: str) -> MongoConnectionConfiguration:
    """Inspect a URI for diagnostics without transforming the value sent to Motor."""
    try:
        parsed = urlsplit(uri)
        hostname = parsed.hostname
        query_keys = tuple(
            sorted({key for key, _ in parse_qsl(parsed.query, keep_blank_values=True)})
        )
    except ValueError:
        hostname = None
        query_keys = ()
    return MongoConnectionConfiguration(
        uri_scheme=mongodb_uri_scheme(uri),
        hostname=hostname,
        database_name=database_name,
        query_keys=query_keys,
    )


def _is_dns_srv_failure(exc: BaseException, error_text: str) -> bool:
    return (
        isinstance(exc, OSError)
        and getattr(exc, "errno", None) in {-2, 11001}
        or "dns" in error_text
        or "srv" in error_text
        or "name or service not known" in error_text
        or "nodename nor servname" in error_text
    )


def _is_tls_failure(exc: BaseException, error_text: str) -> bool:
    return isinstance(exc, ssl.SSLError) or any(
        marker in error_text
        for marker in ("certificate verify", "ssl handshake", "tls handshake", "[ssl:")
    )


def _is_invalid_uri(error_text: str) -> bool:
    return any(
        marker in error_text
        for marker in (
            "invalid uri",
            "invaliduri",
            "must begin with",
            "mongodb uri",
            "invalid connection string",
        )
    )


def classify_mongodb_connection_error(exc: BaseException) -> MongoConnectionDiagnostic:
    """Classify common driver failures without including exception text in logs."""
    error_text = str(exc).lower()
    exception_class = type(exc).__name__

    if isinstance(exc, OperationFailure) and (exc.code == 18 or "authentication" in error_text):
        return MongoConnectionDiagnostic(
            exception_class,
            "authentication_failed",
            "MongoDB authentication failed. Check the database user credentials and permissions.",
        )
    if isinstance(exc, InvalidURI) or _is_invalid_uri(error_text):
        return MongoConnectionDiagnostic(
            exception_class,
            "invalid_uri",
            "MongoDB URI is invalid. Check the URI format and URL-encode reserved password characters.",
        )
    if _is_dns_srv_failure(exc, error_text):
        return MongoConnectionDiagnostic(
            exception_class,
            "dns_srv_resolution_failed",
            "MongoDB DNS/SRV resolution failed. Check the Atlas cluster host and DNS availability.",
        )
    if _is_tls_failure(exc, error_text):
        return MongoConnectionDiagnostic(
            exception_class,
            "tls_certificate_failed",
            "MongoDB TLS or certificate validation failed. Check Atlas TLS connectivity and certificate trust.",
        )
    if isinstance(exc, ServerSelectionTimeoutError):
        return MongoConnectionDiagnostic(
            exception_class,
            "server_selection_timeout",
            "MongoDB server selection timed out. Check Atlas network access and cluster availability.",
        )
    if isinstance(exc, ConfigurationError):
        return MongoConnectionDiagnostic(
            exception_class,
            "configuration_error",
            "MongoDB driver configuration is invalid. Check the supported URI options.",
        )
    if isinstance(exc, ConnectionFailure):
        return MongoConnectionDiagnostic(
            exception_class,
            "connection_failure",
            "MongoDB connection failed. Check network access and database availability.",
        )
    return MongoConnectionDiagnostic(
        exception_class,
        "mongo_operation_failed",
        "MongoDB startup operation failed. Check the safe startup diagnostic category in logs.",
    )


class MongoDatabase:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.client: AsyncIOMotorClient[dict[str, object]] | None = None

    async def connect(self) -> None:
        configuration = mongodb_connection_configuration(
            self._settings.mongodb_uri, self._settings.mongodb_database
        )
        logger.info(
            "mongodb_connection_configured",
            uri_scheme=configuration.uri_scheme,
            hostname=configuration.hostname,
            database_name=configuration.database_name,
            query_keys=configuration.query_keys,
        )
        try:
            self.client = AsyncIOMotorClient(
                self._settings.mongodb_uri,
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
            diagnostic = classify_mongodb_connection_error(exc)
            logger.error(
                "mongodb_startup_failed",
                exception_class=diagnostic.exception_class,
                safe_reason=diagnostic.safe_reason,
                uri_scheme=configuration.uri_scheme,
            )
            raise DatabaseConnectionError(diagnostic.message) from None

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None

    @property
    def database(self) -> AsyncIOMotorDatabase[dict[str, object]]:
        if not self.client:
            raise RuntimeError("Database connection has not been initialized.")
        return self.client[self._settings.mongodb_database]
