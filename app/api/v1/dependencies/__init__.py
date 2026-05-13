"""FastAPI ``Depends()`` helpers shared by the v1 routers.

Each module owns a thin layer of dependency wiring: a callable that
FastAPI can resolve, sometimes a typed ``Annotated`` alias for ergonomic
reuse, and nothing else. No business logic — that lives in
``app/services/``.
"""
