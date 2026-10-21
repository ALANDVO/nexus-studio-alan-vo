from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "nexus-studio"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    database_url: str = "sqlite+aiosqlite:///./nexus_studio.db"
    database_echo: bool = False

    # Keycloak/OIDC
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "nexus-studio"
    keycloak_client_id: str = "nexus-studio-client"
    keycloak_client_secret: str = ""
    oidc_issuer_url: str = ""

    # LLM Provider settings
    llm_provider: str = "openai-compatible"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_timeout: int = 30

    # Security
    secret_key: str = "dev-secret-change-in-production"
    csrf_secret: str = "dev-csrf-secret-change-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()