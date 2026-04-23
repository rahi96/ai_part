"""
Navelle AI Module — Configuration
Loads all environment variables via pydantic-settings.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────────
    app_name: str = "Navelle AI Module"
    debug: bool = False

    # ── OpenAI ───────────────────────────────────────────────────────────────
    openai_api_key: str = ""
    openai_model: str = "gpt-4"

    # ── Backend API ──────────────────────────────────────────────────────────
    backend_url: str = "http://13.51.155.66:8989"
    customer_token: str = ""
    admin_token: str = ""

    @property
    def APP_NAME(self) -> str:
        return self.app_name


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Convenient singleton
settings = get_settings()
