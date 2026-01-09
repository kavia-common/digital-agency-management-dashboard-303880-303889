import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application configuration loaded from environment variables."""

    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    cors_allow_origins: list[str]


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable {name}. "
            "Ask the orchestrator to add it to the container .env."
        )
    return value


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Return Settings loaded from environment variables."""
    database_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or os.getenv("DB_URL")
    if not database_url:
        raise RuntimeError(
            "Missing DATABASE_URL (or POSTGRES_URL/DB_URL) environment variable. "
            "Expected a PostgreSQL URL like: postgresql://user:pass@host:port/dbname"
        )

    cors_origins_raw = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000")
    cors_allow_origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]

    return Settings(
        database_url=database_url,
        jwt_secret_key=_get_required_env("JWT_SECRET_KEY"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        cors_allow_origins=cors_allow_origins,
    )
