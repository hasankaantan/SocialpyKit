"""Core building blocks used across services, repositories, and DTOs."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from pydantic import BaseModel as _PydanticBaseModel
from pydantic import ConfigDict


class BaseModel(_PydanticBaseModel):
    """Mutable Pydantic v2 base for internal data shapes."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class BaseSchema(_PydanticBaseModel):
    """Immutable Pydantic v2 base for request and response DTOs."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class BaseRepository[EntityT, IdT](ABC):
    """Abstract data access surface.

    Concrete repositories implement these methods against a single aggregate
    root. Services depend on this interface, not on SQLAlchemy directly, so
    that storage can be swapped at the seam without touching business logic.
    """

    @abstractmethod
    async def get(self, entity_id: IdT) -> EntityT | None:
        """Return a single entity by its identifier, or None if missing."""

    @abstractmethod
    async def list(self) -> Sequence[EntityT]:
        """Return every entity managed by this repository."""

    @abstractmethod
    async def create(self, entity: EntityT) -> EntityT:
        """Persist a new entity and return the stored representation."""

    @abstractmethod
    async def update(self, entity: EntityT) -> EntityT:
        """Persist changes to an existing entity and return the new state."""

    @abstractmethod
    async def delete(self, entity_id: IdT) -> None:
        """Remove the entity identified by ``entity_id``."""
