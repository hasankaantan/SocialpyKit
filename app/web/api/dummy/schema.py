"""Immutable DTOs for the dummy demo endpoints."""

from app.core.essentials import BaseSchema


class DummyModelDTO(BaseSchema):
    """Response DTO returned when reading dummy rows."""

    id: int
    name: str


class DummyModelInputDTO(BaseSchema):
    """Request DTO accepted when creating a new dummy row."""

    name: str
