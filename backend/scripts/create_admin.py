"""Create or promote one administrator from environment-provided credentials."""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings
from app.database.mongodb import MongoDatabase
from app.repositories.users import UserRepository
from app.security.passwords import hash_password


def admin_credentials() -> tuple[str, str]:
    email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    password = os.environ.get("ADMIN_PASSWORD", "")
    if email.count("@") != 1 or email.startswith("@") or email.endswith("@"):
        raise ValueError("ADMIN_EMAIL must be a valid email address.")
    if (
        len(password) < 12
        or not any(char.isalpha() for char in password)
        or not any(char.isdigit() for char in password)
    ):
        raise ValueError(
            "ADMIN_PASSWORD must be at least 12 characters and include letters and numbers."
        )
    return email, password


async def create_or_promote_admin() -> str:
    email, password = admin_credentials()
    get_settings.cache_clear()
    database = MongoDatabase(get_settings())
    await database.connect()
    try:
        users = UserRepository(database.database["users"])
        user = await users.find_by_email(email)
        if user is None:
            user = await users.create(email, hash_password(password))
            action = "created"
        else:
            action = "promoted"
        updated = await users.set_role(user.id, "admin")
        if updated is None:
            raise RuntimeError("Admin account could not be updated.")
        return action
    finally:
        await database.disconnect()


def main() -> None:
    try:
        action = asyncio.run(create_or_promote_admin())
    except (RuntimeError, ValueError) as exc:
        print(f"Admin provisioning failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
    print(f"Administrator account {action} successfully.")


if __name__ == "__main__":
    main()
