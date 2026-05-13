"""SQLAlchemy model for the ``users`` table."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserRole(enum.StrEnum):
    """Authorization role attached to every user row.

    Stored as a short string in postgres so the enum can grow without a
    schema migration. The api layer compares against ``UserRole.ADMIN``
    to gate admin-only routes.
    """

    USER = "user"
    ADMIN = "admin"


class User(Base):
    """Authenticated user of the application."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(length=320),
        unique=True,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(length=255))
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
    )
    role: Mapped[UserRole] = mapped_column(
        String(length=16),
        default=UserRole.USER,
        server_default=UserRole.USER.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
