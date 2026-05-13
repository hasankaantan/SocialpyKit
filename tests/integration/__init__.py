"""Integration tests that exercise the real stack end to end.

Conventions:

- Tests drive the FastAPI app through ``httpx.AsyncClient`` + ASGI transport.
- Persistence runs against the real test PostgreSQL database via the
  fixtures in ``tests/conftest.py``. No mocking the database here.
- External services (Sentry, email, third-party APIs) are mocked at their
  boundaries when they would otherwise make network calls.
"""
