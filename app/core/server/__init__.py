"""HTTP server composition: FastAPI factory, lifespan, and middleware.

Re-exports the ``get_app`` factory so callers can do
``from app.core.server import get_app`` without knowing whether the
implementation lives in factory.py, lifespan.py, or rate_limit.py.
"""

from app.core.server.factory import get_app

__all__ = ["get_app"]
