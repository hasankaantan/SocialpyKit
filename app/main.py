"""Application entrypoint used by uvicorn / gunicorn / asgi servers.

Production startup:

    uvicorn app.main:app --reload

The module-level ``app`` instance is built once at import time so the
runtime does not need to know about the factory. Tests still call
:func:`app.core.server.get_app` directly to build a fresh instance per
fixture session.
"""

from app.core.server import get_app

app = get_app()
