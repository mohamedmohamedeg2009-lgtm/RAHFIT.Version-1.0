"""Verify a MongoDB deployment without printing its URI or credentials.

Run from the backend directory:
    python scripts/verify_mongodb_atlas.py
"""

import asyncio
import ssl
import sys
from pathlib import Path
from urllib.parse import urlsplit

import dns.resolver
from pydantic import ValidationError

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import get_settings  # noqa: E402
from app.database.indexes import initialize_indexes, verify_required_indexes  # noqa: E402
from app.database.mongodb import (  # noqa: E402
    DatabaseConnectionError,
    MongoDatabase,
    mongodb_uri_scheme,
)


def srv_lookup(uri: str) -> None:
    """Resolve the Atlas SRV record without printing the hostname or URI."""
    if mongodb_uri_scheme(uri) != "mongodb+srv":
        return
    hostname = urlsplit(uri).hostname
    if not hostname:
        raise ValueError("MongoDB SRV URI does not contain a host.")
    dns.resolver.resolve(f"_mongodb._tcp.{hostname}", "SRV")


async def verify() -> int:
    try:
        settings = get_settings()
    except ValidationError:
        print(
            "MongoDB readiness failed: configuration is invalid. "
            "Set MONGODB_URI and MONGODB_DATABASE in the environment.",
            file=sys.stderr,
        )
        return 1

    database = MongoDatabase(settings)
    try:
        uri = settings.mongodb_uri.unicode_string()
        scheme = mongodb_uri_scheme(uri)
        if scheme == "invalid":
            print("MongoDB diagnostic: invalid URI scheme.", file=sys.stderr)
            return 1
        try:
            srv_lookup(uri)
        except (ValueError, dns.exception.DNSException, OSError, ssl.SSLError) as exc:
            print(
                "MongoDB diagnostic: "
                f"exception_class={type(exc).__name__} safe_reason=dns_srv_resolution_failed "
                f"uri_scheme={scheme}",
                file=sys.stderr,
            )
            return 1
        await database.connect()
        await initialize_indexes(database.database)
        await verify_required_indexes(database.database)
    except (DatabaseConnectionError, RuntimeError) as exc:
        print(f"MongoDB readiness failed: {exc}", file=sys.stderr)
        return 1
    finally:
        await database.disconnect()

    print(f"MongoDB ping succeeded. Database: {settings.mongodb_database}")
    print("Required MongoDB indexes are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(verify()))
