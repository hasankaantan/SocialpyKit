"""Smoke test that the production entrypoint resolves to a real app."""

from fastapi import FastAPI


def test_main_module_exposes_a_fastapi_instance() -> None:
    """``uvicorn app.main:app --reload`` works iff ``app.main.app`` is a
    FastAPI. Import-time side effects (sentry init, exception handlers)
    are exercised by getting here without raising."""
    from app.main import app

    assert isinstance(app, FastAPI)
