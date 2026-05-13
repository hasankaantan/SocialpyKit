"""Domain routers wired into the v1 API root in app/api/v1/router.py.

Conventions:

- One module per aggregate. The module exposes a top-level ``router``
  variable that the central router includes with the appropriate prefix
  and tags.
- Routers depend on services, never on repositories or models directly
  (see CLAUDE.md layer rules).
- Dependency helpers live next door under ``app/api/v1/dependencies/``.
"""
