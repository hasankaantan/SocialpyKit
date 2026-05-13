import logging

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
)
from app.settings import settings
from app.web.api.router import api_router
from app.web.lifespan import lifespan_setup
from app.web.rate_limit import register_rate_limiter


async def handle_not_found(_: Request, exc: NotFoundError) -> JSONResponse:
    """Map :class:`NotFoundError` to HTTP 404."""
    return JSONResponse(status_code=404, content={"detail": exc.message})


async def handle_already_exists(
    _: Request,
    exc: AlreadyExistsError,
) -> JSONResponse:
    """Map :class:`AlreadyExistsError` to HTTP 409."""
    return JSONResponse(status_code=409, content={"detail": exc.message})


async def handle_validation(_: Request, exc: ValidationError) -> JSONResponse:
    """Map :class:`ValidationError` to HTTP 422."""
    return JSONResponse(status_code=422, content={"detail": exc.message})


async def handle_authentication(
    _: Request,
    exc: AuthenticationError,
) -> JSONResponse:
    """Map :class:`AuthenticationError` to HTTP 401 with the WWW-Authenticate
    header that OAuth2 clients expect."""
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def handle_authorization(
    _: Request,
    exc: AuthorizationError,
) -> JSONResponse:
    """Map :class:`AuthorizationError` to HTTP 403."""
    return JSONResponse(status_code=403, content={"detail": exc.message})


def _register_exception_handlers(app: FastAPI) -> None:
    """Wire the domain exception handlers into the FastAPI app."""
    app.add_exception_handler(NotFoundError, handle_not_found)  # type: ignore[arg-type]
    app.add_exception_handler(AlreadyExistsError, handle_already_exists)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationError, handle_validation)  # type: ignore[arg-type]
    app.add_exception_handler(AuthenticationError, handle_authentication)  # type: ignore[arg-type]
    app.add_exception_handler(AuthorizationError, handle_authorization)  # type: ignore[arg-type]


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    if settings.sentry_dsn:
        # Enables sentry integration.
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=settings.sentry_sample_rate,
            environment=settings.environment,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                LoggingIntegration(
                    level=logging.getLevelNamesMapping()[settings.log_level.value],
                    event_level=logging.ERROR,
                ),
                SqlalchemyIntegration(),
            ],
        )
    app = FastAPI(
        title="socialpykit",
        lifespan=lifespan_setup,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    register_rate_limiter(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    _register_exception_handlers(app)

    return app
