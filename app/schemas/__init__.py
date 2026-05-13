"""Immutable Pydantic DTOs exchanged at the API boundary.

Every schema inherits from ``BaseSchema`` (frozen, extra forbidden,
str_strip_whitespace, from_attributes) so:

- Inputs are validated structurally at the FastAPI request layer.
- Outputs can be built directly from sqlalchemy orm instances via
  ``Schema.model_validate(orm_object)`` without writing manual maps.
- The same instance cannot be mutated after creation, which keeps
  service-layer code from leaking state by accident.
"""
