from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )

    ENVIRONMENT: str = "local"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str
    SECRET_KEY: str
    JWT_EXPIRE_MINUTES: int = 60 * 24  # access token lifetime (default 1 day)

    SENTRY_DSN: str = ""  # empty disables Sentry (SDK no-ops on empty DSN)

    # Comma-separated. "*" (default) disables credentialed CORS — browsers reject
    # wildcard origin + allow_credentials, so app/main.py only enables credentials
    # once you set real origins here.
    CORS_ORIGINS: str = "*"


settings = Settings()
