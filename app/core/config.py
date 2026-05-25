from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_URL: str
    CORS_ALLOWED_ORIGIN: str


settings = Settings()  # type: ignore[call-arg]
