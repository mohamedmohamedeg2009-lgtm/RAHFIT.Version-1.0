from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

import structlog
from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import router
from app.config import get_settings
from app.core.exceptions import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging
from app.database.assessment_catalog import initialize_assessment_catalog
from app.database.indexes import initialize_indexes
from app.database.mongodb import MongoDatabase
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.security import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    database = MongoDatabase(settings)
    await database.connect()
    await initialize_indexes(database.database)
    await initialize_assessment_catalog(database.database)
    app.state.database = database
    yield
    await database.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
    app.state.logger = structlog.get_logger()
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(RateLimitMiddleware, settings=settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.allowed_origins],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    app.add_exception_handler(StarletteHTTPException, cast(Any, http_exception_handler))
    app.add_exception_handler(RequestValidationError, cast(Any, validation_exception_handler))
    app.add_exception_handler(Exception, unhandled_exception_handler)

    @app.get("/health", tags=["Health"], summary="Check application and database availability")
    async def health() -> dict[str, str]:
        """Expose a secret-free readiness probe without requiring authentication."""
        database = getattr(app.state, "database", None)
        client = getattr(database, "client", None)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "database_unavailable", "message": "Database is unavailable."},
            )
        try:
            await client.admin.command("ping")
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "database_unavailable", "message": "Database is unavailable."},
            ) from exc
        return {"status": "ok", "database": "ok"}

    app.include_router(router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
