from typing import Any, cast

import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import ValidationError
from pymongo.errors import (
    ConfigurationError,
    InvalidURI,
    OperationFailure,
    ServerSelectionTimeoutError,
)

from app.config.settings import Settings
from app.database import mongodb
from app.database.indexes import REQUIRED_INDEXES, initialize_indexes, verify_required_indexes
from app.database.mongodb import (
    DatabaseConnectionError,
    MongoDatabase,
    classify_mongodb_connection_error,
    mongodb_connection_configuration,
    mongodb_uri_scheme,
)


def required_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MONGODB_URI", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGODB_DATABASE", "rahfit_test")
    monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)


def test_settings_accept_local_mongodb_uri(monkeypatch: pytest.MonkeyPatch) -> None:
    required_environment(monkeypatch)

    settings = Settings(_env_file=None)

    assert settings.mongodb_uri == "mongodb://localhost:27017"
    assert settings.mongodb_database == "rahfit_test"


def test_settings_read_exact_render_mongodb_environment_aliases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    required_environment(monkeypatch)
    monkeypatch.setenv("MONGODB_URI", "mongodb+srv://user:password@cluster.example.mongodb.net/")
    monkeypatch.setenv("MONGODB_DATABASE", "rahfit")

    settings = Settings(_env_file=None)

    assert settings.mongodb_uri.startswith("mongodb+srv://")
    assert settings.mongodb_database == "rahfit"


def test_invalid_mongodb_uri_validation_hides_credential_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    required_environment(monkeypatch)
    monkeypatch.setenv("MONGODB_URI", "not-a-uri-with-secret-password")

    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None)

    assert "not-a-uri-with-secret-password" not in str(error.value)


def test_settings_accept_atlas_srv_uri(monkeypatch: pytest.MonkeyPatch) -> None:
    required_environment(monkeypatch)
    monkeypatch.setenv(
        "MONGODB_URI",
        "mongodb+srv://atlas-user:encoded-password@cluster.example.mongodb.net/"
        "?retryWrites=true&w=majority",
    )

    settings = Settings(_env_file=None)

    assert settings.mongodb_uri.startswith("mongodb+srv://atlas-user:")


@pytest.mark.parametrize("variable", ("MONGODB_URI", "MONGODB_DATABASE"))
def test_settings_require_mongodb_configuration(
    monkeypatch: pytest.MonkeyPatch, variable: str
) -> None:
    required_environment(monkeypatch)
    monkeypatch.delenv(variable)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_mongodb_connection_configuration_excludes_credentials_and_query_values() -> None:
    configuration = mongodb_connection_configuration(
        "mongodb+srv://atlas-user:secret%40password@cluster.example.mongodb.net/"
        "rahfit?retryWrites=true&authSource=admin",
        "rahfit",
    )

    assert configuration.uri_scheme == "mongodb+srv"
    assert configuration.hostname == "cluster.example.mongodb.net"
    assert configuration.database_name == "rahfit"
    assert configuration.query_keys == ("authSource", "retryWrites")


@pytest.mark.parametrize(
    ("error", "safe_reason", "message"),
    [
        (
            OperationFailure("Authentication failed.", code=18),
            "authentication_failed",
            "MongoDB authentication failed.",
        ),
        (
            ServerSelectionTimeoutError("server selection timed out"),
            "server_selection_timeout",
            "MongoDB server selection timed out.",
        ),
        (
            ConfigurationError("unknown option"),
            "configuration_error",
            "MongoDB driver configuration is invalid.",
        ),
        (
            ConfigurationError("The DNS query name does not exist"),
            "dns_srv_resolution_failed",
            "MongoDB DNS/SRV resolution failed.",
        ),
        (
            OSError("[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed"),
            "tls_certificate_failed",
            "MongoDB TLS or certificate validation failed.",
        ),
        (
            ConfigurationError("Invalid URI scheme"),
            "invalid_uri",
            "MongoDB URI is invalid.",
        ),
        (
            InvalidURI("mongodb+srv URI has an invalid host"),
            "invalid_uri",
            "MongoDB URI is invalid.",
        ),
    ],
)
def test_connection_errors_have_distinct_safe_diagnostics(
    error: BaseException, safe_reason: str, message: str
) -> None:
    diagnostic = classify_mongodb_connection_error(error)

    assert diagnostic.exception_class == type(error).__name__
    assert diagnostic.safe_reason == safe_reason
    assert diagnostic.message.startswith(message)


@pytest.mark.parametrize(
    ("uri", "expected_scheme"),
    [
        ("mongodb://user:password@localhost:27017", "mongodb"),
        ("mongodb+srv://user:password@cluster.example.mongodb.net/", "mongodb+srv"),
        ("postgres://user:password@localhost/db", "invalid"),
    ],
)
def test_mongodb_uri_scheme_never_includes_credentials(uri: str, expected_scheme: str) -> None:
    assert mongodb_uri_scheme(uri) == expected_scheme


def test_settings_preserve_mongodb_uri_without_normalization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uri = "mongodb+srv://atlas-user:encoded%40password@cluster.example.mongodb.net/"
    monkeypatch.setenv("MONGODB_URI", uri)
    monkeypatch.setenv("MONGODB_DATABASE", "rahfit")
    monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)

    settings = Settings(_env_file=None)

    assert settings.mongodb_uri == uri


class FakeAdmin:
    def __init__(self, result: object) -> None:
        self.result = result

    async def command(self, name: str) -> dict[str, int]:
        assert name == "ping"
        if isinstance(self.result, Exception):
            raise self.result
        return {"ok": 1}


class FakeClient:
    def __init__(self, result: object) -> None:
        self.admin = FakeAdmin(result)
        self.closed = False

    def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_connect_reports_safe_health_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(
        _env_file=None,
        mongodb_uri="mongodb://atlas-user:secret-password@localhost:27017",
        mongodb_database="rahfit_test",
        jwt_secret_key="a" * 32,
    )
    client = FakeClient(ServerSelectionTimeoutError("network timeout"))
    monkeypatch.setattr(mongodb, "AsyncIOMotorClient", lambda *args, **kwargs: client)

    with pytest.raises(DatabaseConnectionError, match="server selection timed out") as error:
        await MongoDatabase(settings).connect()

    assert "secret-password" not in str(error.value)
    assert client.closed is True


@pytest.mark.asyncio
async def test_connect_logs_only_safe_connection_diagnostic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(
        _env_file=None,
        mongodb_uri="mongodb+srv://atlas-user:secret-password@cluster.example.mongodb.net/",
        mongodb_database="rahfit",
        jwt_secret_key="a" * 32,
    )
    client = FakeClient(OperationFailure("Authentication failed for atlas-user", code=18))
    logged: dict[str, object] = {}

    class Logger:
        def info(self, event: str, **kwargs: object) -> None:
            return None

        def error(self, event: str, **kwargs: object) -> None:
            logged["event"] = event
            logged.update(kwargs)

    monkeypatch.setattr(mongodb, "AsyncIOMotorClient", lambda *args, **kwargs: client)
    monkeypatch.setattr(mongodb, "logger", Logger())

    with pytest.raises(DatabaseConnectionError, match="authentication failed"):
        await MongoDatabase(settings).connect()

    assert logged == {
        "event": "mongodb_startup_failed",
        "exception_class": "OperationFailure",
        "safe_reason": "authentication_failed",
        "uri_scheme": "mongodb+srv",
    }


@pytest.mark.asyncio
async def test_connect_accepts_mocked_atlas_client(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(
        _env_file=None,
        mongodb_uri=(
            "mongodb+srv://atlas-user:encoded-password@cluster.example.mongodb.net/"
            "?retryWrites=true&w=majority&authSource=admin"
        ),
        mongodb_database="rahfit",
        jwt_secret_key="a" * 32,
    )
    client = FakeClient({"ok": 1})
    captured: dict[str, object] = {}

    def create_client(*args: object, **kwargs: object) -> FakeClient:
        captured["uri"] = args[0]
        captured.update(kwargs)
        return client

    monkeypatch.setattr(mongodb, "AsyncIOMotorClient", create_client)
    database = MongoDatabase(settings)

    await database.connect()

    assert captured["uri"] == settings.mongodb_uri
    assert captured["serverSelectionTimeoutMS"] == 5000
    assert captured["connectTimeoutMS"] == 10000
    assert captured["retryWrites"] is True
    assert captured["appname"] == "rahfit-ai-api"
    await database.disconnect()
    assert client.closed is True


@pytest.mark.asyncio
async def test_connect_reports_atlas_authentication_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(
        _env_file=None,
        mongodb_uri="mongodb://localhost:27017",
        mongodb_database="rahfit_test",
        jwt_secret_key="a" * 32,
    )
    client = FakeClient(OperationFailure("Authentication failed."))
    monkeypatch.setattr(mongodb, "AsyncIOMotorClient", lambda *args, **kwargs: client)

    with pytest.raises(DatabaseConnectionError, match="authentication failed"):
        await MongoDatabase(settings).connect()


class IndexInfoCollection:
    def __init__(self, index_names: frozenset[str]) -> None:
        self.index_names = index_names

    async def index_information(self) -> dict[str, dict[str, object]]:
        return {name: {} for name in self.index_names}


class VerifiedIndexDatabase:
    def __getitem__(self, collection_name: str) -> IndexInfoCollection:
        return IndexInfoCollection(REQUIRED_INDEXES[collection_name])


@pytest.mark.asyncio
async def test_required_indexes_verify_after_initialization() -> None:
    await verify_required_indexes(VerifiedIndexDatabase())


class InitializationCollection:
    def __init__(self) -> None:
        self.indexes: dict[str, dict[str, object]] = {}

    async def index_information(self) -> dict[str, dict[str, object]]:
        return dict(self.indexes)

    async def drop_index(self, name: str) -> None:
        self.indexes.pop(name, None)

    async def create_index(self, keys: object, **options: object) -> None:
        self.indexes[str(options["name"])] = {"key": keys, **options}


class InitializationDatabase:
    def __init__(self) -> None:
        self.collections: dict[str, InitializationCollection] = {}

    def __getitem__(self, collection_name: str) -> InitializationCollection:
        return self.collections.setdefault(collection_name, InitializationCollection())


@pytest.mark.asyncio
async def test_full_index_initialization_remains_functional() -> None:
    database = InitializationDatabase()

    await initialize_indexes(cast(AsyncIOMotorDatabase[dict[str, Any]], database))
    await verify_required_indexes(database)
