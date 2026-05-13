"""Request rate limiting wired through slowapi.

Limits are documented on the individual route decorators in
``app.web.api.auth.views``. This module owns the shared :class:`Limiter`
instance and the integration glue (middleware + exception handler) that
:func:`app.web.application.get_app` calls during startup.

Disabled under pytest via ``settings.rate_limit_enabled``. Set
``SOCIALPYKIT_RATE_LIMIT_ENABLED=false`` to disable in any other
environment too (e.g. local stress tests).
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.settings import settings

limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.rate_limit_enabled,
    default_limits=[],
)


def register_rate_limiter(app: FastAPI) -> None:
    """Attach the shared limiter to the FastAPI app and install its glue.

    Wraps slowapi's default 429 handler so the body shape matches the rest
    of the API's error responses (``{"detail": "..."}``).
    """
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _handle_rate_limit_exceeded)  # type: ignore[arg-type]


def _handle_rate_limit_exceeded(  # pragma: no cover
    request: Request,
    exc: RateLimitExceeded,
) -> JSONResponse:
    """Wrap slowapi's default response so the body shape matches the
    rest of the API and so the Retry-After header survives.

    Not exercised under pytest because the limiter is disabled there. In
    production this fires whenever a client crosses one of the per-route
    limits declared on the auth router.
    """
    response = _rate_limit_exceeded_handler(request, exc)
    return JSONResponse(
        status_code=response.status_code,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
        headers=dict(response.headers),
    )
