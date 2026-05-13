"""Unit tests for sentry SDK wiring in :func:`app.web.application.get_app`."""

from unittest.mock import patch

import pytest

from app.settings import settings
from app.web.application import get_app


def test_sentry_init_skipped_when_dsn_is_blank() -> None:
    """Pytest config sets SOCIALPYKIT_SENTRY_DSN to empty string so the
    sentry branch must be a no-op in the default test environment."""
    with patch("app.web.application.sentry_sdk.init") as mock_init:
        get_app()

    mock_init.assert_not_called()


def test_sentry_init_runs_when_dsn_is_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "sentry_dsn",
        "https://example@example.ingest.sentry.io/1",
    )

    with patch("app.web.application.sentry_sdk.init") as mock_init:
        get_app()

    mock_init.assert_called_once()


def test_sentry_init_passes_configured_dsn_and_sample_rate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sentry init receives the settings values verbatim so deployment
    knobs flow through without translation."""
    monkeypatch.setattr(
        settings,
        "sentry_dsn",
        "https://example@example.ingest.sentry.io/1",
    )
    monkeypatch.setattr(settings, "sentry_sample_rate", 0.5)
    monkeypatch.setattr(settings, "environment", "staging")

    with patch("app.web.application.sentry_sdk.init") as mock_init:
        get_app()

    kwargs = mock_init.call_args.kwargs
    assert kwargs["dsn"] == "https://example@example.ingest.sentry.io/1"
    assert kwargs["traces_sample_rate"] == 0.5
    assert kwargs["environment"] == "staging"


def test_sentry_init_wires_all_three_integrations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """FastAPI, logging, and sqlalchemy integrations must all be installed
    so request errors, log records, and orm spans flow into sentry."""
    monkeypatch.setattr(
        settings,
        "sentry_dsn",
        "https://example@example.ingest.sentry.io/1",
    )

    with patch("app.web.application.sentry_sdk.init") as mock_init:
        get_app()

    integrations = mock_init.call_args.kwargs["integrations"]
    class_names = {type(integration).__name__ for integration in integrations}

    assert class_names == {
        "FastApiIntegration",
        "LoggingIntegration",
        "SqlalchemyIntegration",
    }
