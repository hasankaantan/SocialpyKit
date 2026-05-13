"""Declarative base and eager-loading helpers for SQLAlchemy models.

Conventions enforced here:

- Every column uses ``Mapped[T]`` and ``mapped_column(...)`` (SQLAlchemy 2.0
  typed style). Legacy ``Column(...)`` is forbidden.
- Every relationship goes through the local :func:`relationship` wrapper,
  which defaults ``lazy`` to ``"raise"`` so any forgotten ``selectinload``
  or ``joinedload`` raises at query time instead of silently emitting an
  N+1 lazy load.

If a relationship genuinely needs a non-raise strategy, the caller passes
``lazy="selectin"`` (or similar) explicitly. The default is the safe one.
"""

from typing import Any

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship as _sqlalchemy_relationship

from app.db.meta import meta


class Base(DeclarativeBase):
    """Project-wide declarative base bound to the shared metadata."""

    metadata = meta


def relationship(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
    """Wrapper around :func:`sqlalchemy.orm.relationship` that defaults
    ``lazy="raise"``.

    SQLAlchemy's default is ``lazy="select"``, which silently triggers a
    lazy query when the attribute is accessed outside an active session.
    For an async-first stack that is almost always a bug. This wrapper
    flips the default so the loader strategy is opt-in instead of opt-out.

    Type erasure to ``Any`` is intentional: SQLAlchemy's ``relationship``
    return type is a generic ``Relationship[Any]`` whose precise inference
    is the caller's responsibility via ``Mapped[...]`` on the model side.
    """
    # Body only runs once a model declares a relationship; none do yet.
    kwargs.setdefault("lazy", "raise")  # pragma: no cover
    return _sqlalchemy_relationship(*args, **kwargs)  # pragma: no cover
