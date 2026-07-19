from functools import lru_cache
from typing import Annotated, Any, Literal, cast

from pydantic import Field, MongoDsn, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Validated runtime configuration loaded only from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
        populate_by_name=True,
    )

    app_name: str = "RAHFIT AI API"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    # DEBUG is a common host/tooling variable and may contain values such as "release".
    # A namespaced key prevents unrelated process state from breaking API startup.
    app_debug: bool = Field(default=False, validation_alias="RAHFIT_DEBUG")
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
        ]
    )
    mongodb_uri: MongoDsn = Field(validation_alias="MONGODB_URI")
    mongodb_database: str = Field(min_length=1, validation_alias="MONGODB_DATABASE")
    mongodb_server_selection_timeout_ms: int = Field(
        default=5000,
        ge=1000,
        le=30000,
        validation_alias="MONGODB_SERVER_SELECTION_TIMEOUT_MS",
    )
    mongodb_connect_timeout_ms: int = Field(
        default=10000,
        ge=1000,
        le=30000,
        validation_alias="MONGODB_CONNECT_TIMEOUT_MS",
    )
    mongodb_app_name: str = Field(
        default="rahfit-ai-api",
        min_length=1,
        max_length=128,
        validation_alias="MONGODB_APP_NAME",
    )
    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=30, gt=0)
    jwt_refresh_token_expire_days: int = Field(default=7, gt=0)
    rate_limit_requests: int = Field(default=100, gt=0)
    rate_limit_window_seconds: int = Field(default=60, gt=0)
    google_client_id: str | None = Field(default=None, validation_alias="GOOGLE_CLIENT_ID")
    ai_feature_enabled: bool = Field(default=False, validation_alias="AI_FEATURE_ENABLED")
    ai_provider: str = Field(default="gemini", validation_alias="AI_PROVIDER")
    gemini_api_key: SecretStr | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", validation_alias="GEMINI_MODEL")
    ai_timeout: float = Field(default=15, ge=1, le=60, validation_alias="AI_TIMEOUT")
    # Legacy OpenAI-compatible configuration remains supported for existing deployments.
    ai_api_key: SecretStr | None = Field(default=None, validation_alias="AI_API_KEY")
    ai_model: str = Field(default="gpt-4.1-mini", validation_alias="AI_MODEL")
    ai_request_timeout_seconds: float = Field(
        default=15, ge=1, le=60, validation_alias="AI_REQUEST_TIMEOUT_SECONDS"
    )
    ai_max_output_tokens: int = Field(
        default=600, ge=1, le=4096, validation_alias="AI_MAX_OUTPUT_TOKENS"
    )

    @property
    def debug(self) -> bool:
        return self.app_debug

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.app_env != "production":
            return self
        secret = self.jwt_secret_key.get_secret_value()
        if (
            len(secret) < 48
            or "replace-with" in secret.lower()
            or "dev-secret" in secret.lower()
            or len(set(secret)) < 8
        ):
            raise ValueError(
                "JWT_SECRET_KEY must be a high-entropy production secret of at least 48 characters."
            )
        if any(
            origin.startswith(("http://localhost", "http://127.0.0.1"))
            for origin in self.allowed_origins
        ):
            raise ValueError("ALLOWED_ORIGINS must not contain localhost origins in production.")
        return self

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str]) -> list[str]:
        values = value.split(",") if isinstance(value, str) else value
        origins = [origin.strip().rstrip("/") for origin in values if origin.strip()]
        if not origins:
            raise ValueError("ALLOWED_ORIGINS must include at least one origin.")
        if "*" in origins:
            raise ValueError("ALLOWED_ORIGINS cannot contain '*' when credentials are enabled.")
        return origins

    @field_validator("mongodb_database", "mongodb_app_name", mode="before")
    @classmethod
    def normalize_mongodb_text(cls, value: object) -> str:
        normalized = str(value).strip() if value is not None else ""
        return normalized

    @field_validator("ai_provider", mode="before")
    @classmethod
    def normalize_ai_provider(cls, value: object) -> str:
        normalized = str(value).strip().lower() if value is not None else "gemini"
        return normalized[:50]

    @field_validator("ai_feature_enabled", mode="before")
    @classmethod
    def normalize_ai_feature_enabled(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
        raise ValueError("AI_FEATURE_ENABLED must be a Boolean value.")

    @field_validator("ai_model", mode="before")
    @classmethod
    def normalize_ai_model(cls, value: object) -> str:
        normalized = str(value).strip() if value is not None else ""
        return (normalized or "gpt-4.1-mini")[:100]

    @field_validator("gemini_model", mode="before")
    @classmethod
    def normalize_gemini_model(cls, value: object) -> str:
        normalized = str(value).strip() if value is not None else ""
        return (normalized or "gemini-2.5-flash")[:100]

    @field_validator("ai_api_key", mode="before")
    @classmethod
    def normalize_ai_api_key(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("gemini_api_key", mode="before")
    @classmethod
    def normalize_gemini_api_key(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("ai_timeout", mode="before")
    @classmethod
    def normalize_primary_ai_timeout(cls, value: object) -> float:
        try:
            parsed = float(str(value))
        except (TypeError, ValueError):
            return 15
        return parsed if 1 <= parsed <= 60 else 15

    @field_validator("ai_request_timeout_seconds", mode="before")
    @classmethod
    def normalize_ai_timeout(cls, value: object) -> float:
        try:
            parsed = float(str(value))
        except (TypeError, ValueError):
            return 15
        return parsed if 1 <= parsed <= 60 else 15

    @field_validator("ai_max_output_tokens", mode="before")
    @classmethod
    def normalize_ai_output_tokens(cls, value: object) -> int:
        try:
            parsed = int(str(value))
        except (TypeError, ValueError):
            return 600
        return parsed if 1 <= parsed <= 4096 else 600


@lru_cache
def get_settings() -> Settings:
    settings_factory = cast(Any, Settings)
    return cast(Settings, settings_factory())
