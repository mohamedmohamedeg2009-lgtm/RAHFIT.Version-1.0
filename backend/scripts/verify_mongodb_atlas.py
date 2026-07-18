"""Verify a MongoDB deployment without printing its URI or credentials.

Run from the backend directory:
    python scripts/verify_mongodb_atlas.py
"""

import asyncio
import sys

from pydantic import ValidationError

from app.config import get_settings
from app.database.indexes import initialize_indexes, verify_required_indexes
from app.database.mongodb import DatabaseConnectionError, MongoDatabase


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
