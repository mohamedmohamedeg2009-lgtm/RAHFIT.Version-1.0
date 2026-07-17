from functools import lru_cache
from typing import Annotated, Any, Literal, cast

from pydantic import Field, MongoDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Validated runtime configuration loaded only from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

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
    mongodb_uri: MongoDsn
    mongodb_database: str = Field(min_length=1)
    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=30, gt=0)
    jwt_refresh_token_expire_days: int = Field(default=7, gt=0)
    rate_limit_requests: int = Field(default=100, gt=0)
    rate_limit_window_seconds: int = Field(default=60, gt=0)
    google_client_id: str | None = Field(default=None, validation_alias="GOOGLE_CLIENT_ID")
    email_provider: Literal["development", "smtp"] = Field(
        default="development", validation_alias="EMAIL_PROVIDER"
    )
    smtp_host: str = Field(default="localhost", validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    smtp_username: str | None = Field(default=None, validation_alias="SMTP_USERNAME")
    smtp_password: SecretStr | None = Field(default=None, validation_alias="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="noreply@rafhit.ai", validation_alias="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="RAHFIT AI", validation_alias="SMTP_FROM_NAME")
    smtp_use_tls: bool = Field(default=True, validation_alias="SMTP_USE_TLS")
    password_reset_url: str = Field(
        default="http://localhost:5173/reset-password", validation_alias="PASSWORD_RESET_URL"
    )
    password_reset_token_ttl_minutes: int = Field(
        default=15, validation_alias="PASSWORD_RESET_TOKEN_TTL_MINUTES"
    )

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

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

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
        return normalized in {"1", "true", "yes", "on"}

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
