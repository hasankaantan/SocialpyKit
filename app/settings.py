import enum
from pathlib import Path
from tempfile import gettempdir

from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(enum.StrEnum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO
    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "socialpykit"
    db_pass: str = "socialpykit"  # noqa: S105
    db_base: str = "socialpykit"
    db_echo: bool = False

    # Rate limiting (slowapi). Disabled under pytest so the auth integration
    # suite is not subject to the per-IP limits documented on the routes.
    rate_limit_enabled: bool = True

    # CORS origins that may call the API from a browser. Dev defaults
    # cover both the Vite (5173, legacy) and Nuxt (3000) dev servers;
    # production deployments must override via SOCIALPYKIT_CORS_ORIGINS
    # (json list of urls).
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # JWT auth configuration.
    # In production, jwt_secret_key MUST come from the environment
    # (SOCIALPYKIT_JWT_SECRET_KEY). The default below is only for local dev
    # and pytest; never use it in deployments.
    jwt_secret_key: str = "dev-only-do-not-use-in-production"  # noqa: S105
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Sentry's configuration.
    sentry_dsn: str | None = None
    sentry_sample_rate: float = 1.0

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SOCIALPYKIT_",
        env_file_encoding="utf-8",
    )


settings = Settings()
