#!/usr/bin/env python3
"""Promote an existing user to the admin role.

Usage:
    uv run python scripts/promote_admin.py <email>

The user must already exist (register via the API first). This is the
intended bootstrap path: register the very first account, then run this
script to grant it admin so it can manage everyone else through the
dashboard.
"""

from __future__ import annotations

import asyncio
import sys

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models.user import UserRole
from app.repositories.user import UserRepository
from app.settings import settings


async def promote(email: str) -> int:
    engine = create_async_engine(str(settings.db_url))
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with session_factory() as session:
            repo = UserRepository(session)
            user = await repo.get_by_email(email)
            if user is None:
                print(  # noqa: T201
                    f"error: no user with email {email!r}; register first",
                    file=sys.stderr,
                )
                return 1

            if user.role is UserRole.ADMIN:
                print(f"{email} is already an admin")  # noqa: T201
                return 0

            user.role = UserRole.ADMIN
            await repo.update(user)
            await session.commit()
            print(f"promoted {email} to admin")  # noqa: T201
            return 0
    finally:
        await engine.dispose()


def main() -> int:
    if len(sys.argv) != 2:  # noqa: PLR2004
        print(  # noqa: T201
            "usage: uv run python scripts/promote_admin.py <email>",
            file=sys.stderr,
        )
        return 2
    return asyncio.run(promote(sys.argv[1]))


if __name__ == "__main__":
    raise SystemExit(main())
