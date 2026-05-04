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

    # ── AWS Bedrock ──────────────────────────────────────────────────────────────
    bedrock_model_id: str = "meta.llama3-70b-instruct-v1:0"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"

    # ── Backend API ──────────────────────────────────────────────────────────
    backend_url: str = "http://13.51.155.66:8989"
    customer_token: str = ""
    admin_token: str = ""

    # ── MongoDB ──────────────────────────────────────────────────────────────
    mongodb_uri: str = ""

    @property
    def APP_NAME(self) -> str:
        return self.app_name


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Convenient singleton
settings = get_settings()
