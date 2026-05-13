"""Business-logic services for SocialpyKit.

Conventions for this layer:

- One service class per aggregate or domain area.
- Services are framework-agnostic — no FastAPI imports here.
- Services depend on ``BaseRepository`` abstractions from
  ``app.core.essentials``, never on SQLAlchemy directly.
- Inputs and outputs at the service boundary are ``BaseSchema`` DTOs or
  immutable domain objects.
- Business-rule failures raise the domain exceptions defined in
  ``app.core.exceptions``; the API layer maps those to HTTP status codes.
"""
