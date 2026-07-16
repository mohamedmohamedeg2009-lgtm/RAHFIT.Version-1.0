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

    @property
    def debug(self) -> bool:
        return self.app_debug

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    settings_factory = cast(Any, Settings)
    return cast(Settings, settings_factory())
